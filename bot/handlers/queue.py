"""Хэндлер /queue — статус очереди обработки."""
from __future__ import annotations

import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.database import async_session
from bot.database.crud import get_user_language
from bot.i18n import t
from bot.keyboards.inline import get_back_keyboard
from bot.services.queue_manager import queue_manager

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("queue"))
async def cmd_queue(message: Message) -> None:
    """Показывает размер очереди и позицию юзера."""
    async with async_session() as session:
        lang = await get_user_language(session, message.from_user.id)

    size = queue_manager.get_queue_size()
    if size == 0:
        await message.answer(t("queue.empty", lang), parse_mode="HTML")
        return

    user_position = await queue_manager.get_user_position(message.from_user.id)
    if user_position > 0:
        user_line = t("queue.your_position", lang, position=user_position)
    else:
        user_line = ""

    await message.answer(
        t("queue.status", lang, size=size, user_position_line=user_line),
        reply_markup=get_back_keyboard(lang),
        parse_mode="HTML",
    )
