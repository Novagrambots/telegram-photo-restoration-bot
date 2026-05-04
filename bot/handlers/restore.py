"""Хэндлер реставрации фото — приём фото и постановка в очередь."""
from __future__ import annotations

import logging
import os
import tempfile
import time
from pathlib import Path

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.config import settings
from bot.database import async_session
from bot.database.crud import get_or_create_user, get_user_language
from bot.database.models import RestoreMode
from bot.i18n import t
from bot.keyboards.inline import get_mode_keyboard
from bot.services import restorer
from bot.services.queue_manager import RestoreTask, make_task_id, queue_manager

logger = logging.getLogger(__name__)
router = Router()

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
TMP_ROOT = "/tmp/upscaler"
ALLOWED_MODES = {"restore_full", "colorize", "upscale_lanczos"}


def _ensure_tmp_dir() -> str:
    os.makedirs(TMP_ROOT, exist_ok=True)
    return TMP_ROOT


async def _download_to_disk(message: Message, file_id: str) -> tuple[str, int]:
    """Скачивает файл, возвращает (путь, размер_в_kb)."""
    bot = message.bot
    tg_file = await bot.get_file(file_id)
    _ensure_tmp_dir()
    suffix = Path(tg_file.file_path or "").suffix or ".bin"
    fd, dest = tempfile.mkstemp(prefix="in_", suffix=suffix, dir=TMP_ROOT)
    os.close(fd)
    await bot.download(tg_file, destination=dest)
    size_kb = max(1, os.path.getsize(dest) // 1024)
    return dest, size_kb


@router.message(Command("restore"))
async def cmd_restore(message: Message) -> None:
    """/restore — подсказка прислать фото."""
    async with async_session() as session:
        lang = await get_user_language(session, message.from_user.id)
    await message.answer(t("restore.send_photo", lang), parse_mode="HTML")


@router.message(F.photo)
async def handle_photo(message: Message) -> None:
    photo = message.photo[-1]
    await _process_incoming_image(
        message=message,
        file_id=photo.file_id,
        file_size=photo.file_size or 0,
    )


@router.message(F.document)
async def handle_document(message: Message) -> None:
    doc = message.document
    if not doc:
        return
    mime = (doc.mime_type or "").lower()
    if mime not in ALLOWED_MIME:
        async with async_session() as session:
            lang = await get_user_language(session, message.from_user.id)
        await message.answer(t("error.unsupported_format", lang), parse_mode="HTML")
        return
    await _process_incoming_image(
        message=message,
        file_id=doc.file_id,
        file_size=doc.file_size or 0,
    )


async def _process_incoming_image(
    message: Message,
    file_id: str,
    file_size: int,
) -> None:
    """Общая обработка входящего изображения."""
    async with async_session() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        lang = user.language or "ru"
        default_mode = user.default_mode  # RestoreMode | None
        db_user_id = user.id

    # проверка размера
    max_bytes = settings.restore_max_input_mb * 1024 * 1024
    if file_size and file_size > max_bytes:
        await message.answer(
            t("error.too_large_file", lang, max_mb=settings.restore_max_input_mb),
            parse_mode="HTML",
        )
        return

    # скачиваем
    try:
        input_path, size_kb = await _download_to_disk(message, file_id)
    except Exception:
        logger.exception("download failed")
        await message.answer(t("error.processing_failed", lang), parse_mode="HTML")
        return

    # валидация
    try:
        restorer.validate_image(input_path)
    except ValueError as e:
        err = str(e)
        if err == "unsupported_format":
            await message.answer(t("error.unsupported_format", lang), parse_mode="HTML")
        else:
            await message.answer(t("error.processing_failed", lang), parse_mode="HTML")
        Path(input_path).unlink(missing_ok=True)
        return
    except Exception:
        logger.exception("validate_image failed")
        await message.answer(t("error.processing_failed", lang), parse_mode="HTML")
        Path(input_path).unlink(missing_ok=True)
        return

    # определяем ЧБ — для подсказки в меню режимов
    try:
        grayscale = restorer.is_grayscale(input_path)
    except Exception:
        grayscale = False

    # если у юзера есть default_mode — сразу в очередь
    if default_mode is not None:
        mode_value = default_mode.value if hasattr(default_mode, "value") else str(default_mode)
        if mode_value in ALLOWED_MODES:
            await _enqueue(
                message=message,
                input_path=input_path,
                size_kb=size_kb,
                mode=mode_value,
                lang=lang,
                db_user_id=db_user_id,
            )
            return

    # иначе показываем меню выбора
    pending_id = uuid_short()
    _register_pending(pending_id, input_path, size_kb, db_user_id)

    text = t("restore.choose_mode", lang)
    if grayscale:
        text = t("restore.detected_grayscale", lang) + "\n\n" + text

    await message.answer(
        text,
        reply_markup=get_mode_keyboard(pending_id, lang, is_grayscale=grayscale),
        parse_mode="HTML",
    )


def uuid_short() -> str:
    import uuid
    return uuid.uuid4().hex[:12]


# === Реестр pending файлов ===
_pending: dict[str, tuple[str, int, int, float]] = {}
PENDING_TTL_SEC = 600


def _register_pending(pid: str, input_path: str, size_kb: int, db_user_id: int) -> None:
    _pending[pid] = (input_path, size_kb, db_user_id, time.time())


def _pop_pending(pid: str) -> tuple[str, int, int] | None:
    item = _pending.pop(pid, None)
    if item is None:
        return None
    input_path, size_kb, db_user_id, _ts = item
    return input_path, size_kb, db_user_id


def cleanup_pending() -> int:
    """Удаляет устаревшие pending записи (>PENDING_TTL_SEC)."""
    now = time.time()
    stale = [pid for pid, val in _pending.items() if now - val[3] > PENDING_TTL_SEC]
    for pid in stale:
        input_path = _pending[pid][0]
        try:
            Path(input_path).unlink(missing_ok=True)
        except Exception:
            pass
        del _pending[pid]
    return len(stale)


async def _enqueue(
    message: Message | None,
    input_path: str,
    size_kb: int,
    mode: str,
    lang: str,
    db_user_id: int,
    chat_id: int | None = None,
    user_id: int | None = None,
    bot=None,
) -> None:
    """Формирует RestoreTask и ставит в очередь."""
    task_id = make_task_id()
    if message is not None:
        chat_id = message.chat.id
        user_id = message.from_user.id
        bot = message.bot

    status_msg = await bot.send_message(
        chat_id=chat_id,
        text=t("restore.queue_position", lang, position=1, minutes=1),
        parse_mode="HTML",
    )

    task = RestoreTask(
        task_id=task_id,
        user_id=user_id,
        chat_id=chat_id,
        db_user_id=db_user_id,
        input_path=input_path,
        mode=mode,
        status_message_id=status_msg.message_id,
        lang=lang,
        input_size_kb=size_kb,
    )
    position = await queue_manager.enqueue(task)
    eta_sec = queue_manager.estimate_wait_seconds(position, mode)
    minutes = max(1, eta_sec // 60) if eta_sec >= 60 else 1

    try:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_msg.message_id,
            text=t("restore.queue_position", lang, position=position, minutes=minutes),
            parse_mode="HTML",
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("restore:mode:"))
async def callback_choose_mode(callback: CallbackQuery) -> None:
    """callback_data: restore:mode:<mode>:<pending_id>"""
    parts = callback.data.split(":", 3)
    if len(parts) != 4:
        await callback.answer()
        return
    _, _, mode, pending_id = parts

    if mode not in ALLOWED_MODES:
        await callback.answer("unknown mode", show_alert=False)
        return

    async with async_session() as session:
        lang = await get_user_language(session, callback.from_user.id)

    pending = _pop_pending(pending_id)
    if pending is None:
        await callback.answer(t("restore.session_expired", lang), show_alert=True)
        return
    input_path, size_kb, db_user_id = pending

    try:
        await callback.message.delete()
    except Exception:
        pass

    await _enqueue(
        message=None,
        input_path=input_path,
        size_kb=size_kb,
        mode=mode,
        lang=lang,
        db_user_id=db_user_id,
        chat_id=callback.message.chat.id,
        user_id=callback.from_user.id,
        bot=callback.bot,
    )
    await callback.answer()


