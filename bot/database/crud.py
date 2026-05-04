"""CRUD операции с базой данных"""
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import (
    Channel,
    RequestStatus,
    RestoreMode,
    RestoreRequest,
    User,
)


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    full_name: str,
    language: str | None = None,
) -> User:
    """Получить юзера или создать нового"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            language=language or "ru",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


async def get_user_language(session: AsyncSession, telegram_id: int) -> str:
    """Получить язык юзера (по умолчанию ru)"""
    result = await session.execute(
        select(User.language).where(User.telegram_id == telegram_id)
    )
    lang = result.scalar_one_or_none()
    return lang or "ru"


async def update_user_language(
    session: AsyncSession, telegram_id: int, language: str
) -> None:
    """Обновить язык юзера"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.language = language
        await session.commit()


async def get_active_channels(session: AsyncSession) -> list[Channel]:
    """Получить все каналы для обязательной подписки"""
    result = await session.execute(select(Channel))
    return list(result.scalars().all())


async def add_channel(
    session: AsyncSession,
    channel_id: int,
    title: str,
    invite_link: str,
) -> Channel:
    """Добавить канал для обязательной подписки"""
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError(f"Канал {channel_id} уже добавлен")

    channel = Channel(
        channel_id=channel_id,
        title=title,
        invite_link=invite_link,
    )
    session.add(channel)
    await session.commit()
    await session.refresh(channel)
    return channel


async def remove_channel(session: AsyncSession, channel_id: int) -> bool:
    """Удалить канал. Возвращает True если удалён"""
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    channel = result.scalar_one_or_none()
    if not channel:
        return False

    await session.delete(channel)
    await session.commit()
    return True


async def get_user_stats(session: AsyncSession) -> dict:
    """Статистика: всего юзеров, за сегодня, обработок, каналов"""
    from sqlalchemy import func as sa_func

    total = await session.execute(select(sa_func.count(User.id)))
    total_users = total.scalar() or 0

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await session.execute(
        select(sa_func.count(User.id)).where(User.created_at >= today)
    )
    today_users = today_result.scalar() or 0

    restored = await session.execute(
        select(sa_func.sum(User.restored_count))
    )
    total_restored = restored.scalar() or 0

    channels = await session.execute(select(sa_func.count(Channel.id)))
    total_channels = channels.scalar() or 0

    return {
        "total_users": total_users,
        "today_users": today_users,
        "total_restored": total_restored,
        "total_channels": total_channels,
    }


async def get_all_user_ids(session: AsyncSession) -> list[int]:
    """Получить все telegram_id юзеров для рассылки"""
    result = await session.execute(select(User.telegram_id))
    return [row[0] for row in result.all()]


async def create_restore_request(
    session: AsyncSession,
    user_id: int,
    mode: RestoreMode,
    status: RequestStatus = RequestStatus.ok,
    models_used: str | None = None,
    space_used: str | None = None,
    input_size_kb: int | None = None,
    output_size_kb: int | None = None,
    input_resolution: str | None = None,
    output_resolution: str | None = None,
    processing_time_ms: int | None = None,
    queue_wait_ms: int | None = None,
    error_text: str | None = None,
) -> RestoreRequest:
    """Создать запись о запросе реставрации."""
    req = RestoreRequest(
        user_id=user_id,
        mode=mode,
        status=status,
        models_used=models_used,
        space_used=space_used,
        input_size_kb=input_size_kb,
        output_size_kb=output_size_kb,
        input_resolution=input_resolution,
        output_resolution=output_resolution,
        processing_time_ms=processing_time_ms,
        queue_wait_ms=queue_wait_ms,
        error_text=error_text,
    )
    session.add(req)
    await session.commit()
    await session.refresh(req)
    return req


async def increment_user_restored_count(
    session: AsyncSession, telegram_id: int
) -> None:
    """+1 к счётчику обработок у юзера."""
    await session.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(restored_count=User.restored_count + 1)
    )
    await session.commit()


async def update_user_default_mode(
    session: AsyncSession, telegram_id: int, mode: RestoreMode | None
) -> None:
    """Установить дефолтный режим. None = "спрашивать каждый раз"."""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.default_mode = mode
        await session.commit()


async def get_restore_stats(session: AsyncSession, days: int = 7) -> dict:
    """Статистика реставраций за N дней (для админки)."""
    from datetime import datetime, timedelta
    from sqlalchemy import func as sa_func

    cutoff = datetime.now() - timedelta(days=days)

    total_q = await session.execute(
        select(sa_func.count(RestoreRequest.id))
        .where(RestoreRequest.created_at >= cutoff)
    )
    total = total_q.scalar() or 0

    ok_q = await session.execute(
        select(sa_func.count(RestoreRequest.id))
        .where(RestoreRequest.created_at >= cutoff)
        .where(RestoreRequest.status == RequestStatus.ok)
    )
    ok = ok_q.scalar() or 0

    timeout_q = await session.execute(
        select(sa_func.count(RestoreRequest.id))
        .where(RestoreRequest.created_at >= cutoff)
        .where(RestoreRequest.status == RequestStatus.timeout)
    )
    timeouts = timeout_q.scalar() or 0

    error_q = await session.execute(
        select(sa_func.count(RestoreRequest.id))
        .where(RestoreRequest.created_at >= cutoff)
        .where(RestoreRequest.status == RequestStatus.error)
    )
    errors = error_q.scalar() or 0

    avg_q = await session.execute(
        select(sa_func.avg(RestoreRequest.processing_time_ms))
        .where(RestoreRequest.created_at >= cutoff)
        .where(RestoreRequest.status == RequestStatus.ok)
    )
    avg_ms = avg_q.scalar()

    by_mode_q = await session.execute(
        select(RestoreRequest.mode, sa_func.count(RestoreRequest.id))
        .where(RestoreRequest.created_at >= cutoff)
        .group_by(RestoreRequest.mode)
    )
    by_mode = {str(row[0]): row[1] for row in by_mode_q.all()}

    return {
        "days": days,
        "total": total,
        "ok": ok,
        "timeouts": timeouts,
        "errors": errors,
        "avg_processing_ms": int(avg_ms) if avg_ms else 0,
        "by_mode": by_mode,
    }
