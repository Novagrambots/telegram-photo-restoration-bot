"""Конфигурация бота — все настройки из .env"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # токен бота
    bot_token: str

    # юзернейм бота
    bot_username: str = ""

    # PostgreSQL
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "bot_4_upscaler"
    db_user: str = "bot_4_upscaler"
    db_password: str = "changeme"

    # админы бота (через запятую в .env)
    admin_ids: str = ""
    admin_username: str = "admin"

    # URL Local Bot API (Local Bot API на VPS = файлы до 2 ГБ)
    bot_api_url: str = "https://api.telegram.org"

    # лимиты обработки изображений
    max_input_mb: int = 10                       # лимит входного файла (legacy)
    restore_max_input_mb: int = 10               # лимит входа для реставрации
    process_timeout_sec: int = 120
    user_rate_limit_sec: int = 60

    # HuggingFace Spaces
    hf_api_token: str = ""                       # для gradio_client (опционально)
    space_timeout_sec: int = 120                 # таймаут на один Space

    @property
    def admin_id_list(self) -> list[int]:
        """Парсит admin_ids из строки в список int"""
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip()]

    @property
    def db_url(self) -> str:
        """URL для подключения к PostgreSQL через asyncpg"""
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# глобальный экземпляр настроек
settings = Settings()
