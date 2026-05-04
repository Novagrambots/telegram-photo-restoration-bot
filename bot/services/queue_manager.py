"""Менеджер очереди задач реставрации.

HF Spaces — внешний HTTP-сервис, поэтому параллельность можно поднять до 3
(не CPU-bound, а сетевые вызовы).
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import FSInputFile, InputMediaDocument

from bot.config import settings
from bot.database import async_session
from bot.database.crud import (
    create_restore_request,
    increment_user_restored_count,
)
from bot.database.models import RequestStatus, RestoreMode
from bot.i18n import t
from bot.services import restorer
from bot.services.restorer import (
    AllSpacesFailedError,
    RestorerError,
    RestorerTimeoutError,
)

logger = logging.getLogger(__name__)

# примерное время обработки в секундах для расчёта ETA
MODE_ETA_SEC = {
    "restore_full": 70,      # DeOldify (~35с) + ModelScope (~20с) + PIL (~1с) + сеть
    "colorize": 40,          # DeOldify (~35с) + PIL
    "upscale_lanczos": 2,
}

# параллельных воркеров
WORKER_CONCURRENCY = 3


@dataclass
class RestoreTask:
    """Задача в очереди реставрации."""
    task_id: str
    user_id: int                # telegram_id
    chat_id: int
    db_user_id: int             # внутренний User.id
    input_path: str
    mode: str
    status_message_id: int
    lang: str
    input_size_kb: int
    enqueued_at: float = field(default_factory=time.time)


# для совместимости с импортами из старого upscale.py — алиас
UpscaleTask = RestoreTask


class QueueManager:
    """Очередь задач с несколькими воркерами (HTTP-bound)."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[RestoreTask] = asyncio.Queue()
        self._tasks: list[RestoreTask] = []
        self._lock = asyncio.Lock()
        self._user_to_task: dict[int, str] = {}

    async def enqueue(self, task: RestoreTask) -> int:
        """Ставит задачу в очередь, возвращает позицию (1 = следующая)."""
        async with self._lock:
            self._tasks.append(task)
            self._user_to_task[task.user_id] = task.task_id
            position = len(self._tasks)
        await self._queue.put(task)
        logger.info(
            "queue: enqueue task=%s user=%s mode=%s pos=%d",
            task.task_id, task.user_id, task.mode, position,
        )
        return position

    async def get_position(self, task_id: str) -> int:
        async with self._lock:
            for idx, t_ in enumerate(self._tasks, start=1):
                if t_.task_id == task_id:
                    return idx
            return 0

    async def get_user_position(self, user_id: int) -> int:
        async with self._lock:
            task_id = self._user_to_task.get(user_id)
            if not task_id:
                return 0
            for idx, t_ in enumerate(self._tasks, start=1):
                if t_.task_id == task_id:
                    return idx
            return 0

    def get_queue_size(self) -> int:
        return len(self._tasks)

    @staticmethod
    def estimate_wait_seconds(position: int, mode: str) -> int:
        per_task = MODE_ETA_SEC.get(mode, 30)
        # с учётом параллельности воркеров
        effective_pos = max(1, (position + WORKER_CONCURRENCY - 1) // WORKER_CONCURRENCY)
        return max(per_task, effective_pos * per_task)

    async def _remove_task(self, task_id: str) -> None:
        async with self._lock:
            self._tasks = [t_ for t_ in self._tasks if t_.task_id != task_id]
            for uid, tid in list(self._user_to_task.items()):
                if tid == task_id:
                    del self._user_to_task[uid]

    async def worker(self, bot: Bot) -> None:
        """Запускает несколько воркеров параллельно."""
        logger.info("QueueManager: запуск %d воркеров", WORKER_CONCURRENCY)
        await asyncio.gather(
            *[self._worker_loop(bot, idx) for idx in range(WORKER_CONCURRENCY)]
        )

    async def _worker_loop(self, bot: Bot, idx: int) -> None:
        logger.info("worker[%d] started", idx)
        while True:
            try:
                task = await self._queue.get()
            except asyncio.CancelledError:
                logger.info("worker[%d] остановлен", idx)
                raise
            try:
                await self._process_task(bot, task)
            except Exception:
                logger.exception("worker[%d]: непредвиденная ошибка", idx)
            finally:
                await self._remove_task(task.task_id)
                self._queue.task_done()

    async def _process_task(self, bot: Bot, task: RestoreTask) -> None:
        """Обработка одной задачи: вызов restorer.* и отправка результата."""
        from bot.keyboards.inline import get_repeat_keyboard

        queue_wait_ms = int((time.time() - task.enqueued_at) * 1000)
        output_path = task.input_path + ".out.png"

        # уведомляем юзера, что началась обработка
        try:
            await bot.edit_message_text(
                chat_id=task.chat_id,
                message_id=task.status_message_id,
                text=t("restore.processing", task.lang,
                       model_name=_mode_to_label(task.mode),
                       eta=MODE_ETA_SEC.get(task.mode, 30)),
                parse_mode="HTML",
            )
        except Exception as e:
            logger.debug("edit_message_text processing failed: %s", e)

        status = RequestStatus.ok
        error_text: Optional[str] = None
        result: dict = {}
        output_size_kb: Optional[int] = None

        # фоновая таска прогресса для длинных режимов
        progress_task: Optional[asyncio.Task] = None
        if task.mode in ("restore_full", "colorize"):
            progress_task = asyncio.create_task(
                _progress_loop(bot, task)
            )

        try:
            try:
                try:
                    result = await _dispatch_restore(task.mode, task.input_path, output_path)
                except RestorerTimeoutError as e:
                    status = RequestStatus.timeout
                    error_text = f"timeout:{e}"[:500]
                    logger.warning("task=%s timeout", task.task_id)
                    await _stop_progress(progress_task)
                    progress_task = None
                    await _safe_edit(bot, task, t("error.timeout", task.lang))
                    return
                except AllSpacesFailedError as e:
                    status = RequestStatus.error
                    error_text = f"all_failed:{e}"[:500]
                    logger.warning("task=%s all spaces failed", task.task_id)
                    await _stop_progress(progress_task)
                    progress_task = None
                    await _safe_edit(bot, task, t("error.all_models_failed", task.lang))
                    return
                except RestorerError as e:
                    status = RequestStatus.error
                    error_text = f"{type(e).__name__}: {e}"[:500]
                    logger.exception("task=%s обработка упала", task.task_id)
                    await _stop_progress(progress_task)
                    progress_task = None
                    await _safe_edit(bot, task, t("error.processing_failed", task.lang))
                    return
                except Exception as e:
                    status = RequestStatus.error
                    error_text = f"{type(e).__name__}: {e}"[:500]
                    logger.exception("task=%s неожиданная ошибка", task.task_id)
                    await _stop_progress(progress_task)
                    progress_task = None
                    await _safe_edit(bot, task, t("error.processing_failed", task.lang))
                    return
            finally:
                # прогресс-таска больше не нужна — обработка завершилась (успех/ошибка)
                if progress_task is not None:
                    await _stop_progress(progress_task)
                    progress_task = None

            # успех — отправляем результат как «до» + «после» в media_group
            try:
                output_size_kb = max(1, Path(output_path).stat().st_size // 1024)
                seconds = result.get("processing_time_ms", 0) / 1000.0
                caption = t(
                    "restore.done",
                    task.lang,
                    input_res=result.get("input_resolution") or "?",
                    output_res=result.get("output_resolution") or "?",
                    model=result.get("model_used", "?"),
                    seconds=f"{seconds:.1f}",
                )
                if result.get("fallback_used"):
                    caption += "\n\n" + t("restore.fallback_notice", task.lang)
                if settings.bot_username:
                    caption += t(
                        "restore.promo", task.lang,
                        bot_username=settings.bot_username,
                    )

                # media_group из 2 документов: оригинал («До») + результат (полный caption).
                # reply_markup в media_group не передаётся — кнопку шлём отдельным сообщением ниже.
                media = [
                    InputMediaDocument(
                        media=FSInputFile(task.input_path),
                        caption=t("restore.before_caption", task.lang),
                        parse_mode="HTML",
                    ),
                    InputMediaDocument(
                        media=FSInputFile(output_path),
                        caption=caption,
                        parse_mode="HTML",
                    ),
                ]
                await bot.send_media_group(
                    chat_id=task.chat_id,
                    media=media,
                )
                # отдельное сообщение с кнопками «Повторить / Назад»
                await bot.send_message(
                    chat_id=task.chat_id,
                    text=t("restore.done_short", task.lang),
                    parse_mode="HTML",
                    reply_markup=get_repeat_keyboard(task.mode, task.lang),
                )
                try:
                    await bot.delete_message(
                        chat_id=task.chat_id,
                        message_id=task.status_message_id,
                    )
                except Exception:
                    pass
            except Exception as e:
                status = RequestStatus.error
                error_text = f"send_failed:{e}"[:500]
                output_size_kb = None
                logger.exception("task=%s отправка результата упала", task.task_id)
                try:
                    await bot.send_message(
                        chat_id=task.chat_id,
                        text=t("error.send_failed", task.lang),
                        parse_mode="HTML",
                    )
                except Exception:
                    pass

            if status == RequestStatus.ok:
                try:
                    async with async_session() as session:
                        await increment_user_restored_count(session, task.user_id)
                except Exception:
                    logger.exception("increment_user_restored_count failed")
        finally:
            await self._save_log(
                task,
                status,
                error_text,
                queue_wait_ms,
                result,
                output_size_kb=output_size_kb if status == RequestStatus.ok else None,
            )
            self._cleanup_files(task.input_path, output_path)

    async def _save_log(
        self,
        task: RestoreTask,
        status: RequestStatus,
        error_text: Optional[str],
        queue_wait_ms: int,
        result: dict,
        output_size_kb: Optional[int] = None,
    ) -> None:
        try:
            async with async_session() as session:
                await create_restore_request(
                    session=session,
                    user_id=task.db_user_id,
                    mode=RestoreMode(task.mode),
                    status=status,
                    models_used=result.get("models_used"),
                    space_used=result.get("space_used"),
                    input_size_kb=task.input_size_kb,
                    output_size_kb=output_size_kb,
                    input_resolution=result.get("input_resolution"),
                    output_resolution=result.get("output_resolution"),
                    processing_time_ms=result.get("processing_time_ms"),
                    queue_wait_ms=queue_wait_ms,
                    error_text=error_text,
                )
        except Exception:
            logger.exception("create_restore_request failed")

    @staticmethod
    def _cleanup_files(*paths: str) -> None:
        for p in paths:
            try:
                Path(p).unlink(missing_ok=True)
            except Exception:
                logger.debug("cleanup: не удалось удалить %s", p)


async def _dispatch_restore(mode: str, input_path: str, output_path: str) -> dict:
    """Маршрутизация по режиму."""
    if mode == "restore_full":
        return await restorer.restore_full(input_path, output_path)
    if mode == "colorize":
        return await restorer.colorize_only(input_path, output_path)
    if mode == "upscale_lanczos":
        return await restorer.upscale_lanczos(input_path, output_path, scale=2)
    raise RestorerError(f"unknown_mode:{mode}")


def _mode_to_label(mode: str) -> str:
    if mode == "restore_full":
        return "DeOldify + ModelScope + PIL Enhance"
    if mode == "colorize":
        return "DeOldify + PIL Enhance"
    if mode == "upscale_lanczos":
        return "Pillow LANCZOS"
    return mode


async def _safe_edit(bot: Bot, task: RestoreTask, text: str) -> None:
    try:
        await bot.edit_message_text(
            chat_id=task.chat_id,
            message_id=task.status_message_id,
            text=text,
            parse_mode="HTML",
        )
    except TelegramBadRequest:
        # обычно "message is not modified" — игнорируем
        pass
    except Exception:
        pass


# интервал между апдейтами прогресса
_PROGRESS_INTERVAL_SEC = 13


async def _progress_loop(bot: Bot, task: RestoreTask) -> None:
    """Циклически обновляет статус-сообщение, чтобы юзер видел движение.

    Меняет фразы в зависимости от режима. Срабатывает примерно каждые 13 сек.
    Отменяется снаружи через task.cancel() — мы корректно ловим CancelledError.
    """
    if task.mode == "restore_full":
        steps = [
            "restore.progress.full_step1",
            "restore.progress.full_step2",
            "restore.progress.full_step3",
        ]
    elif task.mode == "colorize":
        steps = [
            "restore.progress.colorize_step1",
            "restore.progress.colorize_step2",
        ]
    else:
        return  # для upscale_lanczos прогресс не нужен

    eta = MODE_ETA_SEC.get(task.mode, 30)
    started = time.time()
    idx = 0
    try:
        while True:
            await asyncio.sleep(_PROGRESS_INTERVAL_SEC)
            elapsed = time.time() - started
            # после превышения ETA — переключаемся на «cold start» сообщение
            if elapsed > eta:
                key = "restore.progress.cold_start"
            else:
                key = steps[idx % len(steps)]
                idx += 1
            await _safe_edit(bot, task, t(key, task.lang))
    except asyncio.CancelledError:
        # нормальный путь: основная корутина дождалась результата и отменила нас
        raise


async def _stop_progress(progress_task: Optional[asyncio.Task]) -> None:
    """Останавливает фоновую таску прогресса, ждёт её корректного выхода."""
    if progress_task is None:
        return
    if progress_task.done():
        return
    progress_task.cancel()
    try:
        await progress_task
    except (asyncio.CancelledError, Exception):
        pass


# глобальный singleton
queue_manager = QueueManager()


def make_task_id() -> str:
    return uuid.uuid4().hex[:12]
