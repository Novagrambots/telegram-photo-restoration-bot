# bot_4_upscaler

Telegram-бот для увеличения разрешения фотографий с помощью AI (Real-ESRGAN ncnn-vulkan).

## Стек

- Python 3.11
- Aiogram 3.x
- SQLAlchemy 2.x + asyncpg + PostgreSQL
- Real-ESRGAN ncnn-vulkan v0.2.0
- Pillow
- Docker + docker-compose

## Режимы апскейла

| Режим | Описание |
|-------|----------|
| 2x Lanczos | Быстрое увеличение без AI (PIL) |
| 2x AI | Real-ESRGAN x2plus |
| 4x AI | Real-ESRGAN x4plus (по умолчанию) |
| 4x AI Anime | Real-ESRGAN x4plus-anime |

## Деплой

```bash
cp .env.example .env
# заполнить .env

docker compose up -d
```

## Структура

```
bot/
  config.py          — настройки из .env
  i18n.py            — переводы ru/uz/en
  emojis.py          — премиум-эмодзи
  main.py            — точка входа
  database/          — модели и CRUD
  handlers/          — Telegram хэндлеры
  middlewares/       — подписка, rate limit
  keyboards/         — inline клавиатуры
  services/          — бизнес-логика (upscaler, queue)
  utils/             — утилиты (команды меню)
```
