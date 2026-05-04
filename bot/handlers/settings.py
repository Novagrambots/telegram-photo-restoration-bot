"""Настройки пользователя — режим реставрации по умолчанию."""
from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.database import async_session
from bot.database.crud import (
    get_or_create_user,
    get_user_language,
    update_user_default_mode,
)
from bot.database.models import RestoreMode
from bot.i18n import t
from bot.keyboards.inline import get_settings_keyboard

logger = logging.getLogger(__name__)
router = Router()


def _mode_label(mode, lang: str) -> str:
    if mode is None:
        return t("mode.ask", lang)
    val = mode.value if hasattr(mode, "value") else str(mode)
    return t(f"mode.{val}", lang)


async def _render_settings(target_message, user_id: int) -> None:
    async with async_session() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=user_id,
            username=None,
            full_name="",
        )
        lang = user.language or "ru"
        current_mode = user.default_mode

    cm_value = (
        current_mode.value if hasattr(current_mode, "value")
        else str(current_mode) if current_mode else None
    )

    text = t("settings.title", lang, current_mode=_mode_label(current_mode, lang))
    kb = get_settings_keyboard(cm_value, lang)

    if hasattr(target_message, "edit_text"):
        try:
            await target_message.edit_text(text, reply_markup=kb, parse_mode="HTML")
            return
        except Exception:
            pass
    await target_message.answer(text, reply_markup=kb, parse_mode="HTML")


@router.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    await _render_settings(message, message.from_user.id)


@router.callback_query(F.data == "open_settings")
async def open_settings(callback: CallbackQuery) -> None:
    await _render_settings(callback.message, callback.from_user.id)
    await callback.answer()


@router.callback_query(F.data.startswith("settings:mode:"))
async def set_mode(callback: CallbackQuery) -> None:
    """settings:mode:<mode | ask>"""
    parts = callback.data.split(":", 2)
    if len(parts) != 3:
        await callback.answer()
        return
    mode_value = parts[2]

    if mode_value == "ask":
        new_mode = None
    else:
        try:
            new_mode = RestoreMode(mode_value)
        except ValueError:
            await callback.answer()
            return

    async with async_session() as session:
        await update_user_default_mode(session, callback.from_user.id, new_mode)
        lang = await get_user_language(session, callback.from_user.id)

    await callback.answer(t("settings.saved", lang))
    await _render_settings(callback.message, callback.from_user.id)
