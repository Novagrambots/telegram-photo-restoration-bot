"""Сервис реставрации старых фото через HuggingFace Spaces.

Используем gradio_client (синхронный), оборачиваем вызовы в asyncio.to_thread.
Основной Space: modelscope/old_photo_restoration (раскраска + улучшение).
Fallback: leonelhs/deoldify (только раскраска).

Локальный fallback для режима upscale_lanczos: PIL LANCZOS (без AI, мгновенно).
"""
from __future__ import annotations

import asyncio
import logging
import os
import shutil
import time
from pathlib import Path

from PIL import Image, ImageEnhance

from bot.config import settings

logger = logging.getLogger(__name__)

# идентификаторы Spaces
SPACE_MODELSCOPE = "modelscope/old_photo_restoration"
SPACE_DEOLDIFY = "leonelhs/deoldify"


class RestorerError(Exception):
    """Ошибка реставрации."""


class RestorerTimeoutError(RestorerError):
    """Таймаут вызова Space."""


class AllSpacesFailedError(RestorerError):
    """Не сработал ни один Space (основной + fallback)."""


def _import_gradio_client():
    """Импорт gradio_client лениво — модуль тяжёлый, не нужен на старте."""
    from gradio_client import Client, handle_file  # type: ignore
    return Client, handle_file


def _make_client(space_id: str):
    """Создаёт Client синхронно (вызывается через asyncio.to_thread).

    В разных версиях gradio_client параметр для токена называется по-разному
    (hf_token / token / отсутствует). Перебираем варианты, чтобы не падать.
    Для публичных Spaces токен не обязателен.
    """
    Client, _ = _import_gradio_client()
    token = settings.hf_api_token or None
    if token:
        for kwarg in ("hf_token", "token"):
            try:
                return Client(space_id, **{kwarg: token})
            except TypeError:
                continue
    return Client(space_id)


def _predict_sync(client, args: tuple, kwargs: dict):
    """Синхронный вызов client.predict — для запуска через to_thread."""
    return client.predict(*args, **kwargs)


async def _call_space(
    space_id: str,
    args: tuple,
    kwargs: dict,
    timeout: int,
):
    """Вызывает Space синхронно через gradio_client в потоке.

    args — позиционные аргументы для predict (для Spaces, которые не принимают keyword).
    kwargs — ключевые (например api_name).

    Возвращает результат predict (тип зависит от Space).
    Поднимает RestorerTimeoutError при таймауте, RestorerError при сбое.
    """
    started = time.time()
    logger.info("calling space %s", space_id)
    try:
        client = await asyncio.wait_for(
            asyncio.to_thread(_make_client, space_id),
            timeout=timeout,
        )
    except asyncio.TimeoutError as e:
        logger.warning("space %s connect timeout", space_id)
        raise RestorerTimeoutError(f"connect_timeout:{space_id}") from e
    except Exception as e:
        logger.warning("space %s connect failed: %s", space_id, e)
        raise RestorerError(f"connect_failed:{space_id}:{e}") from e

    try:
        result = await asyncio.wait_for(
            asyncio.to_thread(_predict_sync, client, args, kwargs),
            timeout=timeout,
        )
    except asyncio.TimeoutError as e:
        logger.warning("space %s predict timeout", space_id)
        raise RestorerTimeoutError(f"predict_timeout:{space_id}") from e
    except Exception as e:
        logger.warning("space %s predict failed: %s", space_id, e)
        raise RestorerError(f"predict_failed:{space_id}:{e}") from e
    finally:
        # gradio_client запускает фоновый heartbeat-поток, который продолжает
        # стучаться в Space и забивать логи 404-ками. Принудительно закрываем
        # клиент чтобы heartbeat остановился.
        try:
            await asyncio.to_thread(_close_client, client)
        except Exception as e:
            logger.debug("space %s close failed: %s", space_id, e)

    elapsed = time.time() - started
    logger.info("space %s done in %.1fs", space_id, elapsed)
    return result


def _close_client(client) -> None:
    """Корректно завершает Client: останавливает heartbeat и закрывает httpx-сессию."""
    # в разных версиях gradio_client API закрытия разное — пробуем все варианты
    for method in ("close", "reset_session", "_close"):
        fn = getattr(client, method, None)
        if callable(fn):
            try:
                fn()
                return
            except Exception:
                pass
    # fallback: убить httpx-клиент и executor вручную
    for attr in ("session", "_client", "httpx_client"):
        sess = getattr(client, attr, None)
        if sess is not None:
            try:
                sess.close()
            except Exception:
                pass


def _resolve_result_path(result) -> str:
    """Извлекает путь к файлу из результата gradio.

    ModelScope old_photo_restoration → tuple[str, str], второй элемент — восстановленный.
    DeOldify → str (путь к webp/png).
    """
    if isinstance(result, (list, tuple)):
        if len(result) >= 2:
            return str(result[1])
        if len(result) == 1:
            return str(result[0])
        raise RestorerError("empty_gradio_result")
    if isinstance(result, dict):
        # некоторые Spaces возвращают {"path": "..."} или {"name": "..."}
        for key in ("path", "name", "image"):
            if key in result and result[key]:
                return str(result[key])
        raise RestorerError("unexpected_dict_result")
    if isinstance(result, str):
        return result
    raise RestorerError(f"unexpected_result_type:{type(result).__name__}")


def _copy_and_cleanup(src: str, dst: str) -> None:
    """Копирует результат в dst и удаляет gradio-кэш."""
    shutil.copy(src, dst)
    # gradio складывает результаты в /tmp/gradio/... — чистим за собой
    try:
        src_path = Path(src)
        if src_path.exists() and "/tmp/" in str(src_path):
            src_path.unlink(missing_ok=True)
    except Exception:
        pass


def _get_resolution(path: str) -> str | None:
    """Возвращает 'WxH' или None."""
    try:
        with Image.open(path) as img:
            return f"{img.width}x{img.height}"
    except Exception:
        return None


def _boost_saturation(input_path: str, output_path: str,
                      saturation: float = 1.4, contrast: float = 1.08,
                      sharpness: float = 1.15) -> None:
    """Локальный post-processing: усиливает насыщенность, контраст и резкость через PIL.

    DeOldify красит мягко (приглушённые цвета). После него поднимаем насыщенность
    на 40%, контраст на 8%, резкость на 15% — результат становится визуально живее.
    Работает мгновенно, без AI и без интернета.
    """
    with Image.open(input_path) as img:
        if img.mode != "RGB":
            img = img.convert("RGB")
        img = ImageEnhance.Color(img).enhance(saturation)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        img = ImageEnhance.Sharpness(img).enhance(sharpness)
        img.save(output_path, format="PNG", optimize=True)


def _post_process_in_place(path: str) -> None:
    """Применяет _boost_saturation к файлу in-place (через временный файл)."""
    tmp = path + ".enhanced.png"
    try:
        _boost_saturation(path, tmp)
        before = Path(path).stat().st_size
        after = Path(tmp).stat().st_size
        shutil.move(tmp, path)
        logger.info(
            "post-process: saturation+contrast+sharpness applied (size %d → %d bytes)",
            before, after,
        )
    except Exception as e:
        logger.warning("post-process failed (%s), keeping original", e)
        Path(tmp).unlink(missing_ok=True)


# === Публичные функции ===


async def restore_full(input_path: str, output_path: str) -> dict:
    """Полная реставрация: pipeline DeOldify (раскраска) → ModelScope (улучшение).

    Если DeOldify упал — фолбэк на одиночный ModelScope.
    Если упал ModelScope на втором шаге — оставляем результат DeOldify (уже цветной).
    """
    _, handle_file = _import_gradio_client()
    started = time.time()
    in_res = _get_resolution(input_path)
    in_size = Path(input_path).stat().st_size
    logger.info("restore_full: input %s (%d bytes, %s)", input_path, in_size, in_res)
    tried: list[str] = []

    # промежуточный файл после DeOldify
    intermediate = output_path + ".deoldify.png"

    try:
        # === ШАГ 1: DeOldify — раскраска ===
        deoldify_ok = False
        try:
            tried.append(SPACE_DEOLDIFY)
            result = await _call_space(
                SPACE_DEOLDIFY,
                args=(),
                kwargs={"image": handle_file(input_path), "api_name": "/predict"},
                timeout=settings.space_timeout_sec,
            )
            result_path = _resolve_result_path(result)
            _copy_and_cleanup(result_path, intermediate)
            intermediate_size = Path(intermediate).stat().st_size
            logger.info(
                "DeOldify done: %s (%d bytes, %s)",
                intermediate, intermediate_size, _get_resolution(intermediate),
            )
            if intermediate_size < in_size * 0.3:
                logger.warning(
                    "DeOldify output suspiciously small (%d vs input %d) — Space might have returned a thumbnail",
                    intermediate_size, in_size,
                )
            deoldify_ok = True
        except (RestorerError, RestorerTimeoutError) as e:
            logger.warning("DeOldify failed (%s), falling back to ModelScope only", e)
        except Exception as e:
            logger.warning("DeOldify unexpected error: %s, falling back to ModelScope only", e)

        # Если DeOldify не отработала — пробуем ModelScope на оригинале (одиночный)
        if not deoldify_ok:
            try:
                tried.append(SPACE_MODELSCOPE)
                result = await _call_space(
                    SPACE_MODELSCOPE,
                    args=(handle_file(input_path),),
                    kwargs={"api_name": "/predict"},
                    timeout=settings.space_timeout_sec,
                )
                result_path = _resolve_result_path(result)
                _copy_and_cleanup(result_path, output_path)
                await asyncio.to_thread(_post_process_in_place, output_path)
                elapsed_ms = int((time.time() - started) * 1000)
                return {
                    "model_used": SPACE_MODELSCOPE,
                    "models_used": ",".join(tried),
                    "space_used": SPACE_MODELSCOPE,
                    "processing_time_ms": elapsed_ms,
                    "fallback_used": True,
                    "input_resolution": in_res,
                    "output_resolution": _get_resolution(output_path),
                }
            except (RestorerError, RestorerTimeoutError) as e:
                logger.error("ModelScope-only fallback also failed: %s", e)
                raise AllSpacesFailedError(f"all_failed:{tried}") from e

        # === ШАГ 2: ModelScope — улучшение качества цветной картинки ===
        try:
            tried.append(SPACE_MODELSCOPE)
            result = await _call_space(
                SPACE_MODELSCOPE,
                args=(handle_file(intermediate),),
                kwargs={"api_name": "/predict"},
                timeout=settings.space_timeout_sec,
            )
            result_path = _resolve_result_path(result)
            _copy_and_cleanup(result_path, output_path)
            out_size = Path(output_path).stat().st_size
            logger.info(
                "ModelScope done: %s (%d bytes, %s)",
                output_path, out_size, _get_resolution(output_path),
            )
            # шаг 3: post-processing PIL — насыщенность + контраст + резкость
            await asyncio.to_thread(_post_process_in_place, output_path)
            elapsed_ms = int((time.time() - started) * 1000)
            return {
                "model_used": f"{SPACE_DEOLDIFY}+{SPACE_MODELSCOPE}+pil-enhance",
                "models_used": ",".join(tried),
                "space_used": SPACE_MODELSCOPE,
                "processing_time_ms": elapsed_ms,
                "fallback_used": False,
                "input_resolution": in_res,
                "output_resolution": _get_resolution(output_path),
            }
        except (RestorerError, RestorerTimeoutError) as e:
            # ModelScope упал — оставляем результат DeOldify (цветной, но без улучшения)
            logger.warning("ModelScope step failed (%s), using DeOldify result as final", e)
            shutil.copy(intermediate, output_path)
            await asyncio.to_thread(_post_process_in_place, output_path)
            elapsed_ms = int((time.time() - started) * 1000)
            return {
                "model_used": SPACE_DEOLDIFY,
                "models_used": ",".join(tried),
                "space_used": SPACE_DEOLDIFY,
                "processing_time_ms": elapsed_ms,
                "fallback_used": True,
                "input_resolution": in_res,
                "output_resolution": _get_resolution(output_path),
            }
    finally:
        # промежуточный файл удаляется ВСЕГДА — даже если упало внутри _call_space,
        # _resolve_result_path или AllSpacesFailedError всплыло наружу
        Path(intermediate).unlink(missing_ok=True)


async def colorize_only(input_path: str, output_path: str) -> dict:
    """Только раскраска через DeOldify."""
    _, handle_file = _import_gradio_client()
    started = time.time()
    in_res = _get_resolution(input_path)

    try:
        result = await _call_space(
            SPACE_DEOLDIFY,
            args=(),
            kwargs={"image": handle_file(input_path), "api_name": "/predict"},
            timeout=settings.space_timeout_sec,
        )
        result_path = _resolve_result_path(result)
        _copy_and_cleanup(result_path, output_path)
    except RestorerTimeoutError:
        raise
    except RestorerError:
        raise

    # post-processing — DeOldify красит мягко, поднимаем насыщенность
    await asyncio.to_thread(_post_process_in_place, output_path)

    elapsed_ms = int((time.time() - started) * 1000)
    return {
        "model_used": f"{SPACE_DEOLDIFY}+pil-enhance",
        "models_used": SPACE_DEOLDIFY,
        "space_used": SPACE_DEOLDIFY,
        "processing_time_ms": elapsed_ms,
        "fallback_used": False,
        "input_resolution": in_res,
        "output_resolution": _get_resolution(output_path),
    }


def _pil_resize(input_path: str, output_path: str, scale: int) -> None:
    """Локальный апскейл через PIL LANCZOS."""
    with Image.open(input_path) as img:
        if img.mode in ("P", "LA"):
            img = img.convert("RGBA")
        elif img.mode in ("I", "I;16", "F"):
            img = img.convert("RGB")
        new_size = (img.width * scale, img.height * scale)
        resized = img.resize(new_size, Image.Resampling.LANCZOS)
        resized.save(output_path, format="PNG")


async def upscale_lanczos(input_path: str, output_path: str, scale: int = 2) -> dict:
    """Локальный апскейл через PIL LANCZOS (без AI, мгновенно)."""
    started = time.time()
    in_res = _get_resolution(input_path)
    try:
        await asyncio.to_thread(_pil_resize, input_path, output_path, scale)
    except Exception as e:
        raise RestorerError(f"lanczos_failed:{e}") from e
    elapsed_ms = int((time.time() - started) * 1000)
    return {
        "model_used": "pillow-lanczos",
        "models_used": "pillow-lanczos",
        "space_used": None,
        "processing_time_ms": elapsed_ms,
        "fallback_used": False,
        "input_resolution": in_res,
        "output_resolution": _get_resolution(output_path),
    }


def is_grayscale(path: str) -> bool:
    """Эвристика: определяем чёрно-белое ли фото.

    Для палитровых/grayscale-режимов возвращаем сразу True. Иначе сэмплируем
    ~1000 пикселей и проверяем максимальный разброс между R, G, B.
    """
    try:
        with Image.open(path) as img:
            if img.mode in ("L", "1", "LA"):
                return True
            rgb = img.convert("RGB")
            pixels = list(rgb.getdata())
            if not pixels:
                return False
            step = max(1, len(pixels) // 1000)
            sample = pixels[::step]
            max_diff = max(max(p) - min(p) for p in sample)
            return max_diff < 15
    except Exception:
        return False


def validate_image(path: str) -> tuple[int, int]:
    """Проверяет целостность и формат. Возвращает (w, h).

    Поднимает ValueError("invalid_image" | "unsupported_format").
    """
    allowed = {"JPEG", "PNG", "WEBP"}
    try:
        with Image.open(path) as img:
            img.verify()
    except Exception as e:
        raise ValueError("invalid_image") from e
    with Image.open(path) as img:
        fmt = (img.format or "").upper()
        w, h = img.size
    if fmt not in allowed:
        raise ValueError("unsupported_format")
    return w, h
