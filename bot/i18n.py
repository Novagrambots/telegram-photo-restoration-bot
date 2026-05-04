"""Мультиязычность — русский, узбекский, английский
Использование: from bot.i18n import t
  t("start.welcome", lang="ru", name="Иван")
"""

from bot.emojis import E

TRANSLATIONS = {
    # === /start ===
    "start.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет, {{name}}!</b>\n\n"
            f"{E['star']} Я оживляю старые фото — раскрашу чёрно-белые снимки и улучшу качество с помощью AI.\n\n"
            f"{E['pin']} <b>Как пользоваться:</b>\n"
            f"Просто пришли мне старое фото — и я его оживлю! {E['camera']}\n\n"
            "Выбери действие ниже:"
        ),
        "uz": (
            f"{E['bot']} <b>Salom, {{name}}!</b>\n\n"
            f"{E['star']} Men eski rasmlarni jonlantiraman — oq-qora rasmlarni ranglayman va sifatini AI yordamida yaxshilayman.\n\n"
            f"{E['pin']} <b>Qanday foydalanish:</b>\n"
            f"Eski rasmingizni yuboring — men uni jonlantiraman! {E['camera']}\n\n"
            "Quyidagi tugmalardan birini tanlang:"
        ),
        "en": (
            f"{E['bot']} <b>Hello, {{name}}!</b>\n\n"
            f"{E['star']} I bring old photos to life — colorize black-and-white shots and enhance quality with AI.\n\n"
            f"{E['pin']} <b>How to use:</b>\n"
            f"Just send me an old photo — I'll restore it! {E['camera']}\n\n"
            "Choose an action below:"
        ),
    },

    # === Кнопки главного меню ===
    "btn.restore": {
        "ru": "Оживить фото",
        "uz": "Rasmni jonlantirish",
        "en": "Restore photo",
    },
    "btn.settings": {
        "ru": "Настройки",
        "uz": "Sozlamalar",
        "en": "Settings",
    },
    "btn.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "btn.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "btn.back": {
        "ru": "Назад",
        "uz": "Orqaga",
        "en": "Back",
    },
    "btn.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },
    "btn.check_sub": {
        "ru": "Проверить подписку",
        "uz": "Obunani tekshirish",
        "en": "Check subscription",
    },

    # === Профиль ===
    "profile.title": {
        "ru": (
            f"{E['profile']} <b>Твой профиль</b>\n\n"
            f"{E['edit']} Имя: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['camera']} Обработано фото: {{restored_count}}\n"
            f"{E['gear']} Режим: {{default_mode}}\n"
        ),
        "uz": (
            f"{E['profile']} <b>Sizning profilingiz</b>\n\n"
            f"{E['edit']} Ism: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['camera']} Qayta ishlangan rasm: {{restored_count}}\n"
            f"{E['gear']} Rejim: {{default_mode}}\n"
        ),
        "en": (
            f"{E['profile']} <b>Your profile</b>\n\n"
            f"{E['edit']} Name: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['camera']} Photos processed: {{restored_count}}\n"
            f"{E['gear']} Mode: {{default_mode}}\n"
        ),
    },

    # === Помощь ===
    "help.text": {
        "ru": (
            f"{E['book']} <b>Помощь</b>\n\n"
            f"{E['star']} Пришли старое фото — я раскрашу и улучшу его\n"
            f"{E['star']} Режимы: «Оживить» (раскраска + улучшение), «Раскрасить», «Увеличить x2»\n"
            f"{E['star']} Максимальный размер: 10 МБ\n"
            f"{E['star']} Форматы: JPEG, PNG, WEBP\n\n"
            f"{E['plane']} По вопросам: @{{admin_username}}"
        ),
        "uz": (
            f"{E['book']} <b>Yordam</b>\n\n"
            f"{E['star']} Eski rasmni yuboring — uni jonlantirib beraman\n"
            f"{E['star']} Rejimlar: «Jonlantirish», «Faqat ranglash», «Kattalashtirish x2»\n"
            f"{E['star']} Maksimal hajm: 10 MB\n"
            f"{E['star']} Formatlar: JPEG, PNG, WEBP\n\n"
            f"{E['plane']} Savollar uchun: @{{admin_username}}"
        ),
        "en": (
            f"{E['book']} <b>Help</b>\n\n"
            f"{E['star']} Send an old photo — I'll colorize and enhance it\n"
            f"{E['star']} Modes: «Restore» (colorize + enhance), «Colorize only», «Upscale x2»\n"
            f"{E['star']} Max file size: 10 MB\n"
            f"{E['star']} Formats: JPEG, PNG, WEBP\n\n"
            f"{E['plane']} Contact: @{{admin_username}}"
        ),
    },

    # === Подписка ===
    "sub.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет!</b>\n\n"
            f"{E['camera']} Этот бот улучшает фотографии с помощью AI!\n\n"
            f"{E['lock']} <b>Для начала подпишись на каналы ниже:</b>\n\n"
            f"После подписки нажми «{E['check']} Проверить подписку»"
        ),
        "uz": (
            f"{E['bot']} <b>Salom!</b>\n\n"
            f"{E['camera']} Bu bot AI yordamida rasmlarni yaxshilaydi!\n\n"
            f"{E['lock']} <b>Boshlash uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            f"Obuna bo'lgandan keyin «{E['check']} Obunani tekshirish» tugmasini bosing"
        ),
        "en": (
            f"{E['bot']} <b>Hello!</b>\n\n"
            f"{E['camera']} This bot enhances photos using AI!\n\n"
            f"{E['lock']} <b>To start, subscribe to the channels below:</b>\n\n"
            f"After subscribing, tap «{E['check']} Check subscription»"
        ),
    },
    "sub.not_subscribed": {
        "ru": (
            f"{E['cross']} <b>Ты ещё не подписался на все каналы:</b>\n\n"
            f"Подпишись и нажми «{E['check']} Проверить подписку» ещё раз."
        ),
        "uz": (
            f"{E['cross']} <b>Siz hali barcha kanallarga obuna bo'lmadingiz:</b>\n\n"
            f"Obuna bo'ling va «{E['check']} Obunani tekshirish» tugmasini qayta bosing."
        ),
        "en": (
            f"{E['cross']} <b>You haven't subscribed to all channels yet:</b>\n\n"
            f"Subscribe and tap «{E['check']} Check subscription» again."
        ),
    },
    "sub.success": {
        "ru": (
            f"{E['check']} <b>Отлично, {{name}}!</b>\n\n"
            f"Теперь ты можешь пользоваться ботом! {E['star']}\n\n"
            "Отправь фото для улучшения."
        ),
        "uz": (
            f"{E['check']} <b>Ajoyib, {{name}}!</b>\n\n"
            f"Endi siz botdan foydalanishingiz mumkin! {E['star']}\n\n"
            "Yaxshilash uchun rasm yuboring."
        ),
        "en": (
            f"{E['check']} <b>Great, {{name}}!</b>\n\n"
            f"You can now use the bot! {E['star']}\n\n"
            "Send a photo to enhance."
        ),
    },
    "sub.not_required": {
        "ru": f"{E['check']} Подписка не требуется!",
        "uz": f"{E['check']} Obuna talab qilinmaydi!",
        "en": f"{E['check']} No subscription required!",
    },
    "sub.check_alert_fail": {
        "ru": f"{E['cross']} Подпишись на все каналы!",
        "uz": f"{E['cross']} Barcha kanallarga obuna bo'ling!",
        "en": f"{E['cross']} Subscribe to all channels!",
    },
    "sub.check_alert_ok": {
        "ru": f"{E['check']} Подписка подтверждена!",
        "uz": f"{E['check']} Obuna tasdiqlandi!",
        "en": f"{E['check']} Subscription confirmed!",
    },

    # === Ошибки ===
    "error.timeout": {
        "ru": f"{E['clock']} <b>Превышено время ожидания</b>\n\nОбработка заняла слишком долго. Попробуй ещё раз.",
        "uz": f"{E['clock']} <b>Kutish vaqti tugadi</b>\n\nQayta ishlash juda uzoq davom etdi. Qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Request timed out</b>\n\nProcessing took too long. Please try again.",
    },
    "error.rate_limit": {
        "ru": f"{E['clock']} <b>Слишком много запросов!</b>\n\nПодожди {{seconds}} секунд и попробуй снова.",
        "uz": f"{E['clock']} <b>Juda ko'p so'rovlar!</b>\n\n{{seconds}} soniya kuting va qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Too many requests!</b>\n\nWait {{seconds}} seconds and try again.",
    },

    # === Выбор языка ===
    "lang.choose": {
        "ru": f"{E['gear']} <b>Выберите язык:</b>",
        "uz": f"{E['gear']} <b>Tilni tanlang:</b>",
        "en": f"{E['gear']} <b>Choose language:</b>",
    },
    "lang.changed": {
        "ru": f"{E['check']} Язык изменён на русский",
        "uz": f"{E['check']} Til o'zbek tiliga o'zgartirildi",
        "en": f"{E['check']} Language changed to English",
    },

    # === Админ-панель ===
    "admin.title": {
        "ru": f"{E['gear']} <b>Админ-панель</b>\n\nВыбери действие:",
        "uz": f"{E['gear']} <b>Admin panel</b>\n\nAmalni tanlang:",
        "en": f"{E['gear']} <b>Admin panel</b>\n\nChoose an action:",
    },
    "admin.no_access": {
        "ru": f"{E['lock']} У тебя нет доступа к админке.",
        "uz": f"{E['lock']} Sizda admin panelga kirish huquqi yo'q.",
        "en": f"{E['lock']} You don't have access to admin panel.",
    },
    "admin.stats": {
        "ru": (
            f"{E['chart']} <b>Статистика бота</b>\n\n"
            f"{E['users']} Всего юзеров: <b>{{total_users}}</b>\n"
            f"{E['star']} Новых юзеров сегодня: <b>{{today_users}}</b>\n"
            f"{E['camera']} Всего обработок: <b>{{total_restored}}</b>\n"
            f"{E['megaphone']} Каналов: <b>{{total_channels}}</b>"
        ),
        "uz": (
            f"{E['chart']} <b>Bot statistikasi</b>\n\n"
            f"{E['users']} Jami foydalanuvchilar: <b>{{total_users}}</b>\n"
            f"{E['star']} Bugungi yangi foydalanuvchilar: <b>{{today_users}}</b>\n"
            f"{E['camera']} Jami qayta ishlanganlar: <b>{{total_restored}}</b>\n"
            f"{E['megaphone']} Kanallar: <b>{{total_channels}}</b>"
        ),
        "en": (
            f"{E['chart']} <b>Bot statistics</b>\n\n"
            f"{E['users']} Total users: <b>{{total_users}}</b>\n"
            f"{E['star']} New users today: <b>{{today_users}}</b>\n"
            f"{E['camera']} Total processed: <b>{{total_restored}}</b>\n"
            f"{E['megaphone']} Channels: <b>{{total_channels}}</b>"
        ),
    },
    "admin.channels_empty": {
        "ru": f"{E['megaphone']} <b>Каналы</b>\n\nСписок пуст. Добавь канал кнопкой ниже.",
        "uz": f"{E['megaphone']} <b>Kanallar</b>\n\nRo'yxat bo'sh. Quyidagi tugma orqali kanal qo'shing.",
        "en": f"{E['megaphone']} <b>Channels</b>\n\nList is empty. Add a channel using the button below.",
    },
    "admin.channels_title": {
        "ru": f"{E['megaphone']} <b>Каналы для подписки:</b>\n",
        "uz": f"{E['megaphone']} <b>Obuna kanallari:</b>\n",
        "en": f"{E['megaphone']} <b>Subscription channels:</b>\n",
    },
    "admin.add_channel_id": {
        "ru": (
            f"{E['megaphone']} <b>Добавление канала</b>\n\n"
            "Отправь <b>ID канала</b> (например <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Узнать ID: добавь бота @getmyid_bot в канал"
        ),
        "uz": (
            f"{E['megaphone']} <b>Kanal qo'shish</b>\n\n"
            "<b>Kanal ID</b> raqamini yuboring (masalan <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} ID bilish: @getmyid_bot ni kanalga qo'shing"
        ),
        "en": (
            f"{E['megaphone']} <b>Add channel</b>\n\n"
            "Send the <b>channel ID</b> (e.g. <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Get ID: add @getmyid_bot to the channel"
        ),
    },
    "admin.add_channel_title": {
        "ru": f"{E['edit']} Теперь отправь <b>название канала</b>:",
        "uz": f"{E['edit']} Endi <b>kanal nomini</b> yuboring:",
        "en": f"{E['edit']} Now send the <b>channel name</b>:",
    },
    "admin.add_channel_link": {
        "ru": (
            f"{E['link']} Теперь отправь <b>ссылку или юзернейм канала</b>\n\n"
            "Принимаю любой формат:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "uz": (
            f"{E['link']} Endi <b>kanal havolasi yoki username</b> yuboring\n\n"
            "Istalgan formatda:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "en": (
            f"{E['link']} Now send the <b>channel link or username</b>\n\n"
            "Any format accepted:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
    },
    "admin.channel_added": {
        "ru": f"{E['check']} <b>Канал добавлен!</b>",
        "uz": f"{E['check']} <b>Kanal qo'shildi!</b>",
        "en": f"{E['check']} <b>Channel added!</b>",
    },
    "admin.confirm_delete": {
        "ru": f"{E['warning']} <b>Удалить канал?</b>\n\nID: <code>{{channel_id}}</code>\n\nЭто действие нельзя отменить.",
        "uz": f"{E['warning']} <b>Kanalni o'chirishni xohlaysizmi?</b>\n\nID: <code>{{channel_id}}</code>\n\nBu amalni qaytarib bo'lmaydi.",
        "en": f"{E['warning']} <b>Delete channel?</b>\n\nID: <code>{{channel_id}}</code>\n\nThis action cannot be undone.",
    },
    "admin.channel_deleted": {
        "ru": f"{E['check']} Канал удалён!",
        "uz": f"{E['check']} Kanal o'chirildi!",
        "en": f"{E['check']} Channel deleted!",
    },
    "admin.channel_not_found": {
        "ru": f"{E['cross']} Канал не найден",
        "uz": f"{E['cross']} Kanal topilmadi",
        "en": f"{E['cross']} Channel not found",
    },
    "admin.id_not_number": {
        "ru": f"{E['cross']} ID должен быть числом. Попробуй ещё раз:",
        "uz": f"{E['cross']} ID raqam bo'lishi kerak. Qayta urinib ko'ring:",
        "en": f"{E['cross']} ID must be a number. Try again:",
    },
    "admin.title_too_long": {
        "ru": f"{E['cross']} Название слишком длинное (макс 200 символов)",
        "uz": f"{E['cross']} Nom juda uzun (maks 200 belgi)",
        "en": f"{E['cross']} Name is too long (max 200 characters)",
    },
    "admin.link_invalid": {
        "ru": f"{E['cross']} Не удалось распознать ссылку.\nПопробуй ещё:",
        "uz": f"{E['cross']} Havolani aniqlab bo'lmadi.\nQayta urinib ko'ring:",
        "en": f"{E['cross']} Could not parse the link.\nTry again:",
    },

    # === Кнопки админки ===
    "btn.admin_stats": {"ru": "Статистика", "uz": "Statistika", "en": "Statistics"},
    "btn.admin_channels": {"ru": "Каналы", "uz": "Kanallar", "en": "Channels"},
    "btn.admin_home": {"ru": "Главное меню", "uz": "Bosh menyu", "en": "Main menu"},
    "btn.admin_add": {"ru": "Добавить канал", "uz": "Kanal qo'shish", "en": "Add channel"},
    "btn.admin_back": {"ru": "Назад", "uz": "Orqaga", "en": "Back"},
    "btn.admin_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_confirm_del": {"ru": "Да, удалить", "uz": "Ha, o'chirish", "en": "Yes, delete"},
    "btn.admin_cancel_del": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_panel": {"ru": "Админ-панель", "uz": "Admin panel", "en": "Admin panel"},
    "btn.admin_broadcast": {"ru": "Рассылка", "uz": "Xabar yuborish", "en": "Broadcast"},

    # === Рассылка ===
    "admin.broadcast_prompt": {
        "ru": f"{E['plane']} <b>Массовая рассылка</b>\n\nОтправь текст/фото/видео для рассылки.\nПоддерживается HTML.",
        "uz": f"{E['plane']} <b>Ommaviy xabar</b>\n\nYuborish uchun matn/rasm/video yuboring.\nHTML qo'llab-quvvatlanadi.",
        "en": f"{E['plane']} <b>Mass broadcast</b>\n\nSend text/photo/video to broadcast.\nHTML supported.",
    },
    "admin.broadcast_preview": {
        "ru": f"{E['eye']} <b>Предпросмотр</b>\n\nОтправить это сообщение всем юзерам?",
        "uz": f"{E['eye']} <b>Oldindan ko'rish</b>\n\nBu xabarni barcha foydalanuvchilarga yuborishni xohlaysizmi?",
        "en": f"{E['eye']} <b>Preview</b>\n\nSend this message to all users?",
    },
    "admin.broadcast_confirm": {"ru": "Да, отправить", "uz": "Ha, yuborish", "en": "Yes, send"},
    "admin.broadcast_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "admin.broadcast_started": {
        "ru": f"{E['plane']} Рассылка запущена... Ожидай отчёт.",
        "uz": f"{E['plane']} Xabar yuborilmoqda... Hisobotni kuting.",
        "en": f"{E['plane']} Broadcast started... Wait for report.",
    },
    "admin.broadcast_done": {
        "ru": f"{E['chart']} <b>Рассылка завершена!</b>\n\n{E['check']} Доставлено: <b>{{success}}</b>\n{E['cross']} Ошибок: <b>{{failed}}</b>\n{E['users']} Всего: <b>{{total}}</b>",
        "uz": f"{E['chart']} <b>Xabar yuborish tugadi!</b>\n\n{E['check']} Yetkazildi: <b>{{success}}</b>\n{E['cross']} Xatolar: <b>{{failed}}</b>\n{E['users']} Jami: <b>{{total}}</b>",
        "en": f"{E['chart']} <b>Broadcast complete!</b>\n\n{E['check']} Delivered: <b>{{success}}</b>\n{E['cross']} Failed: <b>{{failed}}</b>\n{E['users']} Total: <b>{{total}}</b>",
    },

    # === Описания команд бота (для меню Telegram) ===
    "cmd.start": {
        "ru": "Запустить бота",
        "uz": "Botni boshlash",
        "en": "Start the bot",
    },
    "cmd.menu": {
        "ru": "Главное меню",
        "uz": "Asosiy menyu",
        "en": "Main menu",
    },
    "cmd.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "cmd.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "cmd.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },

    # === Доменные ключи реставратора ===

    "restore.send_photo": {
        "ru": f"{E['camera']} Пришли старое фото — я его оживлю: раскрашу и улучшу качество.",
        "uz": f"{E['camera']} Eski rasmingizni yuboring — men uni ranglayman va sifatini yaxshilayman.",
        "en": f"{E['camera']} Send an old photo — I'll restore it: colorize and enhance quality.",
    },
    "restore.choose_mode": {
        "ru": (
            f"{E['gear']} <b>Что сделать с фото?</b>\n\n"
            f"{E['star']} <b>Оживить</b> — раскрасить и улучшить (рекомендуется)\n"
            f"{E['camera']} <b>Только раскрасить</b> — для чёрно-белых фото\n"
            f"{E['lightning']} <b>Только увеличить</b> — простой ресайз x2 без AI"
        ),
        "uz": (
            f"{E['gear']} <b>Rasm bilan nima qilish kerak?</b>\n\n"
            f"{E['star']} <b>Jonlantirish</b> — ranglash va sifatni yaxshilash (tavsiya etiladi)\n"
            f"{E['camera']} <b>Faqat ranglash</b> — oq-qora rasmlar uchun\n"
            f"{E['lightning']} <b>Faqat kattalashtirish</b> — AI siz oddiy x2 o'lcham o'zgartirish"
        ),
        "en": (
            f"{E['gear']} <b>What should I do with the photo?</b>\n\n"
            f"{E['star']} <b>Restore</b> — colorize and enhance (recommended)\n"
            f"{E['camera']} <b>Colorize only</b> — for black-and-white photos\n"
            f"{E['lightning']} <b>Upscale only</b> — simple x2 resize without AI"
        ),
    },
    "restore.detected_grayscale": {
        "ru": f"{E['camera']} <i>Обнаружено чёрно-белое фото — рекомендую «Оживить».</i>",
        "uz": f"{E['camera']} <i>Oq-qora rasm aniqlandi — «Jonlantirish» tavsiya etiladi.</i>",
        "en": f"{E['camera']} <i>Black-and-white photo detected — I recommend «Restore».</i>",
    },
    "restore.processing": {
        "ru": (
            f"{E['refresh']} <b>Обрабатываю...</b>\n\n"
            f"Модель: <b>{{model_name}}</b>\n"
            f"Это займёт около {{eta}} сек."
        ),
        "uz": (
            f"{E['refresh']} <b>Qayta ishlanmoqda...</b>\n\n"
            f"Model: <b>{{model_name}}</b>\n"
            f"Taxminan {{eta}} soniya davom etadi."
        ),
        "en": (
            f"{E['refresh']} <b>Processing...</b>\n\n"
            f"Model: <b>{{model_name}}</b>\n"
            f"This will take about {{eta}} seconds."
        ),
    },
    "restore.queue_position": {
        "ru": f"{E['clock']} <b>В очереди №{{position}}</b>\n\nПримерное ожидание: ~{{minutes}} мин.",
        "uz": f"{E['clock']} <b>Navbatda №{{position}}</b>\n\nTaxminiy kutish: ~{{minutes}} daq.",
        "en": f"{E['clock']} <b>Queue position #{{position}}</b>\n\nEstimated wait: ~{{minutes}} min.",
    },
    "restore.done": {
        "ru": (
            f"{E['check']} <b>Готово!</b>\n\n"
            f"{E['camera']} {{input_res}} → <b>{{output_res}}</b>\n"
            f"{E['gear']} Модель: <code>{{model}}</code>\n"
            f"{E['clock']} {{seconds}} сек"
        ),
        "uz": (
            f"{E['check']} <b>Tayyor!</b>\n\n"
            f"{E['camera']} {{input_res}} → <b>{{output_res}}</b>\n"
            f"{E['gear']} Model: <code>{{model}}</code>\n"
            f"{E['clock']} {{seconds}} sek"
        ),
        "en": (
            f"{E['check']} <b>Done!</b>\n\n"
            f"{E['camera']} {{input_res}} → <b>{{output_res}}</b>\n"
            f"{E['gear']} Model: <code>{{model}}</code>\n"
            f"{E['clock']} {{seconds}} sec"
        ),
    },
    "restore.fallback_notice": {
        "ru": f"{E['warning']} <i>Основная модель была недоступна — использовалась резервная.</i>",
        "uz": f"{E['warning']} <i>Asosiy model mavjud emas edi — zaxira modeli ishlatildi.</i>",
        "en": f"{E['warning']} <i>Primary model was unavailable — fallback model was used.</i>",
    },
    "restore.promo": {
        "ru": f"\n\n{E['camera']} Оживляй старые фото бесплатно через @{{bot_username}}",
        "uz": f"\n\n{E['camera']} Eski rasmlarni @{{bot_username}} orqali bepul jonlantiring",
        "en": f"\n\n{E['camera']} Restore old photos for free via @{{bot_username}}",
    },
    # === Прогресс обработки (циклически меняется во время работы) ===
    "restore.progress.full_step1": {
        "ru": f"{E['camera']} <b>Шаг 1/3</b>\n\nРаскрашиваю чёрно-белые тона...",
        "uz": f"{E['camera']} <b>1/3-bosqich</b>\n\nOq-qora ranglarni ranglayapman...",
        "en": f"{E['camera']} <b>Step 1/3</b>\n\nColorizing black-and-white tones...",
    },
    "restore.progress.full_step2": {
        "ru": f"{E['star']} <b>Шаг 2/3</b>\n\nУлучшаю детали и резкость...",
        "uz": f"{E['star']} <b>2/3-bosqich</b>\n\nTafsilotlar va aniqlikni yaxshilayapman...",
        "en": f"{E['star']} <b>Step 2/3</b>\n\nEnhancing details and sharpness...",
    },
    "restore.progress.full_step3": {
        "ru": f"{E['refresh']} <b>Шаг 3/3</b>\n\nФинальная обработка цвета...",
        "uz": f"{E['refresh']} <b>3/3-bosqich</b>\n\nRangning yakuniy ishlovi...",
        "en": f"{E['refresh']} <b>Step 3/3</b>\n\nFinal color processing...",
    },
    "restore.progress.colorize_step1": {
        "ru": f"{E['camera']} <b>Шаг 1/2</b>\n\nРаскрашиваю...",
        "uz": f"{E['camera']} <b>1/2-bosqich</b>\n\nRanglayapman...",
        "en": f"{E['camera']} <b>Step 1/2</b>\n\nColorizing...",
    },
    "restore.progress.colorize_step2": {
        "ru": f"{E['refresh']} <b>Шаг 2/2</b>\n\nУсиливаю цвета...",
        "uz": f"{E['refresh']} <b>2/2-bosqich</b>\n\nRanglarni kuchaytiryapman...",
        "en": f"{E['refresh']} <b>Step 2/2</b>\n\nBoosting colors...",
    },
    "restore.progress.cold_start": {
        "ru": f"{E['clock']} <b>Подключаюсь к нейросети...</b>\n\nИногда модель «просыпается» дольше обычного — подожди немного.",
        "uz": f"{E['clock']} <b>Neyron tarmoqqa ulanayapman...</b>\n\nBa'zan model odatdagidan uzoqroq «uyg'onadi» — biroz kuting.",
        "en": f"{E['clock']} <b>Connecting to the neural network...</b>\n\nSometimes the model takes longer to wake up — please wait a bit.",
    },
    "restore.before_caption": {
        "ru": f"{E['camera']} <b>До</b>",
        "uz": f"{E['camera']} <b>Oldin</b>",
        "en": f"{E['camera']} <b>Before</b>",
    },
    "restore.done_short": {
        "ru": f"{E['check']} Готово!",
        "uz": f"{E['check']} Tayyor!",
        "en": f"{E['check']} Done!",
    },
    "restore.session_expired": {
        "ru": f"{E['warning']} Сессия истекла, пришли фото снова",
        "uz": f"{E['warning']} Sessiya tugadi, rasmni qayta yuboring",
        "en": f"{E['warning']} Session expired, please send the photo again",
    },

    # === Названия режимов ===
    "mode.restore_full": {
        "ru": "Оживить (раскраска + улучшение)",
        "uz": "Jonlantirish (ranglash + yaxshilash)",
        "en": "Restore (colorize + enhance)",
    },
    "mode.colorize": {
        "ru": "Только раскрасить",
        "uz": "Faqat ranglash",
        "en": "Colorize only",
    },
    "mode.upscale_lanczos": {
        "ru": "Только увеличить (x2)",
        "uz": "Faqat kattalashtirish (x2)",
        "en": "Upscale only (x2)",
    },
    "mode.ask": {
        "ru": "Спрашивать каждый раз",
        "uz": "Har safar so'rash",
        "en": "Ask every time",
    },

    # === Кнопки режимов ===
    "btn.mode_restore_full": {
        "ru": "Оживить", "uz": "Jonlantirish", "en": "Restore",
    },
    "btn.mode_colorize": {
        "ru": "Раскрасить", "uz": "Ranglash", "en": "Colorize",
    },
    "btn.mode_upscale_lanczos": {
        "ru": "Увеличить x2", "uz": "Kattalashtirish x2", "en": "Upscale x2",
    },
    # === Ошибки доменной части ===
    "error.too_large_file": {
        "ru": f"{E['package']} <b>Файл больше {{max_mb}} МБ</b>\n\nПопробуй фото поменьше.",
        "uz": f"{E['package']} <b>Fayl {{max_mb}} MB dan katta</b>\n\nKichikroq rasm yuboring.",
        "en": f"{E['package']} <b>File is larger than {{max_mb}} MB</b>\n\nTry a smaller photo.",
    },
    "error.processing_failed": {
        "ru": f"{E['cross']} <b>Не удалось обработать</b>\n\nПопробуй ещё раз.",
        "uz": f"{E['cross']} <b>Qayta ishlab bo'lmadi</b>\n\nQayta urinib ko'ring.",
        "en": f"{E['cross']} <b>Failed to process</b>\n\nPlease try again.",
    },
    "error.unsupported_format": {
        "ru": f"{E['warning']} <b>Формат не поддерживается</b>\n\nПринимаются: JPEG, PNG, WEBP.",
        "uz": f"{E['warning']} <b>Format qo'llab-quvvatlanmaydi</b>\n\nQabul qilinadi: JPEG, PNG, WEBP.",
        "en": f"{E['warning']} <b>Unsupported format</b>\n\nAccepted: JPEG, PNG, WEBP.",
    },
    "error.all_models_failed": {
        "ru": f"{E['cross']} <b>Все модели сейчас недоступны</b>\n\nПопробуй через 5–10 минут.",
        "uz": f"{E['cross']} <b>Barcha modellar hozir mavjud emas</b>\n\n5–10 daqiqadan so'ng qayta urinib ko'ring.",
        "en": f"{E['cross']} <b>All models are unavailable right now</b>\n\nPlease try again in 5–10 minutes.",
    },
    "error.send_failed": {
        "ru": f"{E['cross']} <b>Не удалось отправить результат</b>\n\nПопробуй ещё раз.",
        "uz": f"{E['cross']} <b>Natijani yuborib bo'lmadi</b>\n\nQayta urinib ko'ring.",
        "en": f"{E['cross']} <b>Failed to send result</b>\n\nPlease try again.",
    },

    # === Настройки ===
    "settings.title": {
        "ru": (
            f"{E['gear']} <b>Настройки</b>\n\n"
            f"Режим по умолчанию: <b>{{current_mode}}</b>\n\n"
            f"Выбери, какой режим использовать автоматически, либо «Спрашивать»:"
        ),
        "uz": (
            f"{E['gear']} <b>Sozlamalar</b>\n\n"
            f"Standart rejim: <b>{{current_mode}}</b>\n\n"
            f"Avtomatik ishlatiladigan rejimni tanlang yoki «So'rash»:"
        ),
        "en": (
            f"{E['gear']} <b>Settings</b>\n\n"
            f"Default mode: <b>{{current_mode}}</b>\n\n"
            f"Choose which mode to use automatically, or «Ask every time»:"
        ),
    },
    "settings.saved": {
        "ru": f"{E['check']} Сохранено",
        "uz": f"{E['check']} Saqlandi",
        "en": f"{E['check']} Saved",
    },

    # === Очередь ===
    "queue.status": {
        "ru": (
            f"{E['clock']} <b>Очередь обработки</b>\n\n"
            f"Всего задач: <b>{{size}}</b>\n"
            f"{{user_position_line}}"
        ),
        "uz": (
            f"{E['clock']} <b>Qayta ishlash navbati</b>\n\n"
            f"Jami vazifalar: <b>{{size}}</b>\n"
            f"{{user_position_line}}"
        ),
        "en": (
            f"{E['clock']} <b>Processing queue</b>\n\n"
            f"Total tasks: <b>{{size}}</b>\n"
            f"{{user_position_line}}"
        ),
    },
    "queue.your_position": {
        "ru": f"Твоя позиция: <b>{{position}}</b>",
        "uz": f"Sening navbating: <b>{{position}}</b>",
        "en": f"Your position: <b>{{position}}</b>",
    },
    "queue.empty": {
        "ru": f"{E['check']} <b>Очередь пуста</b>\n\nОтправь фото — будет обработано сразу.",
        "uz": f"{E['check']} <b>Navbat bo'sh</b>\n\nRasm yuboring — darhol qayta ishlanadi.",
        "en": f"{E['check']} <b>Queue is empty</b>\n\nSend a photo — it will be processed right away.",
    },

    # === Команды для меню ===
    "cmd.queue": {"ru": "Очередь", "uz": "Navbat", "en": "Queue"},
    "cmd.settings": {"ru": "Настройки", "uz": "Sozlamalar", "en": "Settings"},
    "cmd.restore": {"ru": "Оживить фото", "uz": "Rasmni jonlantirish", "en": "Restore a photo"},
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить перевод по ключу и языку"""
    translations = TRANSLATIONS.get(key, {})
    text = translations.get(lang, translations.get("ru", f"[{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text


def detect_language(language_code: str | None) -> str:
    """Определяет язык по Telegram: ru → русский, uz → узбекский, остальное → английский"""
    if not language_code:
        return "en"
    if language_code.startswith("ru"):
        return "ru"
    if language_code.startswith("uz"):
        return "uz"
    return "en"
