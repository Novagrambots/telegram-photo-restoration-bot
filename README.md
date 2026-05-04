# Telegram Photo Restoration Bot

Telegram-бот, который оживляет старые фотографии: раскрашивает чёрно-белые снимки и улучшает качество через бесплатные модели HuggingFace Spaces (DeOldify + ModelScope) и пост-обработку PIL.

## Возможности

- Автоматическое определение чёрно-белых фото (анализ насыщенности через PIL).
- Очередь обработки с прогресс-апдейтами в реальном времени.
- Превью «До / После» отдельной media-group.
- Мультиязычность: русский, узбекский, английский.
- Админ-панель: статистика, обязательные подписки на каналы, рассылка.
- Telegram-кастомные премиум-эмодзи.
- Local Bot API сервер для отдачи файлов до 2 ГБ.

## Режимы

| Режим | Pipeline | Время |
|-------|----------|-------|
| Оживить (полная реставрация) | DeOldify → ModelScope → PIL Enhance | ~60–80 сек |
| Только раскрасить | DeOldify → PIL Enhance | ~30–40 сек |
| Только увеличить (×2) | Pillow LANCZOS | ~1 сек |

## Стек

- Python 3.12, Aiogram 3.x
- SQLAlchemy 2.x async + asyncpg, PostgreSQL 16
- Alembic для миграций
- gradio_client для вызова HuggingFace Spaces
- Pillow для пост-обработки и Lanczos-апскейла
- Docker Compose: `bot`, `postgres`, `bot-api` (Local Bot API), `autoheal`

## Архитектура

```
bot/
  config.py          — настройки из .env (pydantic-settings)
  main.py            — точка входа
  i18n.py            — переводы ru/uz/en
  emojis.py          — кастомные премиум-эмодзи
  database/          — SQLAlchemy модели и CRUD
  handlers/          — Telegram хэндлеры (start, restore, settings, queue, admin)
  middlewares/       — rate limit, проверка подписки
  keyboards/         — inline-клавиатуры
  services/
    restorer.py      — клиент к HuggingFace Spaces + PIL post-process
    queue_manager.py — очередь задач, параллельные воркеры, прогресс
  utils/             — установка команд меню
alembic/             — миграции БД
```

## Деплой

```bash
git clone https://github.com/<your_user>/<this_repo>.git
cd <this_repo>
cp .env.example .env
# заполнить BOT_TOKEN, ADMIN_IDS, DB_PASSWORD, BOT_USERNAME, HF_API_TOKEN

docker compose up -d --build
docker compose exec bot alembic upgrade head
docker compose logs -f bot
```

## Переменные окружения

| Переменная | Назначение |
|-----------|------------|
| `BOT_TOKEN` | Токен от @BotFather |
| `BOT_USERNAME` | Юзернейм бота без `@` (для рекламной подписи) |
| `API_ID` / `API_HASH` | my.telegram.org — для Local Bot API |
| `ADMIN_IDS` | Telegram ID админов через запятую |
| `ADMIN_USERNAME` | Юзернейм для блока «Связь» в /help |
| `DB_*` | PostgreSQL connection |
| `BOT_API_PORT` | Внешний порт Local Bot API (по умолчанию 8085) |
| `HF_API_TOKEN` | Токен HuggingFace (опционально, для приватных Spaces) |
| `MAX_INPUT_MB` | Лимит входного файла |
| `USER_RATE_LIMIT_SEC` | Минимальный интервал между запросами на юзера |
| `SPACE_TIMEOUT_SEC` | Таймаут на один HuggingFace Space |

## Команды бота

```
/start      — приветствие и главное меню
/menu       — открыть главное меню
/restore    — отправить фото на реставрацию
/profile    — мой профиль (количество обработанных фото)
/settings   — выбор режима по умолчанию
/queue      — статус очереди обработки
/help       — справка
/language   — сменить язык
```

## Лицензия

MIT
