"""Модели базы данных — User, Channel, RestoreRequest"""
import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class RestoreMode(str, enum.Enum):
    """Режимы реставрации фото"""
    restore_full = "restore_full"          # ModelScope old_photo_restoration + DeOldify fallback
    colorize = "colorize"                  # только DeOldify (раскраска)
    upscale_lanczos = "upscale_lanczos"    # PIL LANCZOS x2 без AI


class RequestStatus(str, enum.Enum):
    """Статус запроса на реставрацию"""
    ok = "ok"
    timeout = "timeout"
    error = "error"
    too_large = "too_large"


class User(Base):
    """Пользователь бота"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    # когда первый раз зашёл в бота
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # счётчик обработанных фото
    restored_count: Mapped[int] = mapped_column(Integer, default=0)
    # язык интерфейса: ru / uz / en
    language: Mapped[str] = mapped_column(String(5), default="ru")
    # дефолтный режим реставрации (None = спрашивать каждый раз)
    default_mode: Mapped[RestoreMode | None] = mapped_column(
        Enum(RestoreMode, name="restore_mode_enum"),
        default=RestoreMode.restore_full,
        nullable=True,
    )

    # связь с запросами
    restore_requests: Mapped[list["RestoreRequest"]] = relationship(
        back_populates="user", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} ({self.username})>"


class Channel(Base):
    """Канал/группа для обязательной подписки"""
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # id канала в Telegram (например -1001234567890)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    # название для отображения юзеру
    title: Mapped[str] = mapped_column(String(255))
    # ссылка на канал (для кнопки "Подписаться")
    invite_link: Mapped[str] = mapped_column(String(255))
    # когда добавлен
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Channel {self.channel_id} ({self.title})>"


class RestoreRequest(Base):
    """Запрос на реставрацию фото — лог обработок."""
    __tablename__ = "restore_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    mode: Mapped[RestoreMode] = mapped_column(
        Enum(RestoreMode, name="restore_mode_enum"),
        nullable=False,
    )
    # список моделей через запятую (например "modelscope/old_photo_restoration,leonelhs/deoldify")
    models_used: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # какой Space фактически дал результат (для отладки)
    space_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    input_size_kb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_size_kb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    input_resolution: Mapped[str | None] = mapped_column(String(20), nullable=True)
    output_resolution: Mapped[str | None] = mapped_column(String(20), nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    queue_wait_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, name="request_status_enum"),
        default=RequestStatus.ok,
    )
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="restore_requests")

    def __repr__(self) -> str:
        return f"<RestoreRequest {self.id} user={self.user_id} mode={self.mode} status={self.status}>"
