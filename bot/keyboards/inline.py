"""Inline-клавиатуры — главное меню, подписка, язык"""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import settings
from bot.emojis import E_ID
from bot.i18n import t


def get_start_keyboard(user_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Главное меню бота"""
    buttons = [
        [InlineKeyboardButton(
            text=t("btn.restore", lang),
            callback_data="upscale_photo",
            style="primary",
            icon_custom_emoji_id=E_ID["star"],
        )],
        [
            InlineKeyboardButton(
                text=t("btn.profile", lang),
                callback_data="my_profile",
                style="success",
                icon_custom_emoji_id=E_ID["profile"],
            ),
            InlineKeyboardButton(
                text=t("btn.help", lang),
                callback_data="help",
                style="success",
                icon_custom_emoji_id=E_ID["info"],
            ),
        ],
        [
            InlineKeyboardButton(
                text=t("btn.settings", lang),
                callback_data="open_settings",
                style="success",
                icon_custom_emoji_id=E_ID["edit"],
            ),
            InlineKeyboardButton(
                text=t("btn.language", lang),
                callback_data="change_language",
                style="success",
                icon_custom_emoji_id=E_ID["gear"],
            ),
        ],
    ]

    # кнопка админки для админов
    if user_id in settings.admin_id_list:
        buttons.append([InlineKeyboardButton(
            text=t("btn.admin_panel", lang),
            callback_data="admin_panel",
            style="danger",
            icon_custom_emoji_id=E_ID["lock"],
        )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_back_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка 'Назад' в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_menu",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ])


def get_subscription_keyboard(
    channels: list[dict], lang: str = "ru"
) -> InlineKeyboardMarkup:
    """Клавиатура подписки на каналы"""
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(
            text=f"{ch['title']}",
            url=ch["invite_link"],
            style="primary",
            icon_custom_emoji_id=E_ID["megaphone"],
        )])
    buttons.append([InlineKeyboardButton(
        text=t("btn.check_sub", lang),
        callback_data="check_subscription",
        style="success",
        icon_custom_emoji_id=E_ID["check"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Русский",
                callback_data="set_lang_ru",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_ru"],
            ),
            InlineKeyboardButton(
                text="O'zbek",
                callback_data="set_lang_uz",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_uz"],
            ),
            InlineKeyboardButton(
                text="English",
                callback_data="set_lang_en",
                style="primary",
                icon_custom_emoji_id=E_ID["flag_gb"],
            ),
        ],
    ])

def get_mode_keyboard(
    pending_id: str, lang: str = "ru", is_grayscale: bool = False
) -> InlineKeyboardMarkup:
    """Выбор режима реставрации после получения фото.

    Callback: restore:mode:<mode>:<pending_id>
    Если is_grayscale=True — помечаем "Оживить" звёздочкой как рекомендуемый.
    """
    rows = [
        [InlineKeyboardButton(
            text=t("btn.mode_restore_full", lang),
            callback_data=f"restore:mode:restore_full:{pending_id}",
            style="primary",
            icon_custom_emoji_id=E_ID["star"],
        )],
    ]
    # "только раскрасить" показываем только для ЧБ
    if is_grayscale:
        rows.append([InlineKeyboardButton(
            text=t("btn.mode_colorize", lang),
            callback_data=f"restore:mode:colorize:{pending_id}",
            style="success",
            icon_custom_emoji_id=E_ID["camera"],
        )])
    rows.append([InlineKeyboardButton(
        text=t("btn.mode_upscale_lanczos", lang),
        callback_data=f"restore:mode:upscale_lanczos:{pending_id}",
        style="success",
        icon_custom_emoji_id=E_ID["lightning"],
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def get_repeat_keyboard(orig_mode: str, lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопка под результатом — возврат в главное меню."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=t("btn.back", lang),
                callback_data="back_to_menu",
                style="success",
                icon_custom_emoji_id=E_ID.get("back", E_ID["star"]),
            ),
        ],
    ])


def get_settings_keyboard(
    current_mode: str | None, lang: str = "ru"
) -> InlineKeyboardMarkup:
    """Меню настроек: только режим по умолчанию (radio-style).

    current_mode: 'restore_full' | 'colorize' | 'upscale_lanczos' | None ('спрашивать').
    """
    def mark(active: bool) -> str:
        return "● " if active else "○ "

    cm = str(current_mode) if current_mode else None
    is_ask = cm is None

    buttons = [
        [InlineKeyboardButton(
            text=mark(is_ask) + t("mode.ask", lang),
            callback_data="settings:mode:ask",
            style="primary",
            icon_custom_emoji_id=E_ID["bulb"],
        )],
        [InlineKeyboardButton(
            text=mark(cm == "restore_full") + t("mode.restore_full", lang),
            callback_data="settings:mode:restore_full",
            style="primary",
            icon_custom_emoji_id=E_ID["star"],
        )],
        [InlineKeyboardButton(
            text=mark(cm == "colorize") + t("mode.colorize", lang),
            callback_data="settings:mode:colorize",
            style="primary",
            icon_custom_emoji_id=E_ID["camera"],
        )],
        [InlineKeyboardButton(
            text=mark(cm == "upscale_lanczos") + t("mode.upscale_lanczos", lang),
            callback_data="settings:mode:upscale_lanczos",
            style="primary",
            icon_custom_emoji_id=E_ID["lightning"],
        )],
        [InlineKeyboardButton(
            text=t("btn.back", lang),
            callback_data="back_to_menu",
            style="success",
            icon_custom_emoji_id=E_ID["back"],
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
