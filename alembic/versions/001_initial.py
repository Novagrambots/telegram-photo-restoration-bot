"""Начальная миграция — таблицы users, channels, upscale_requests

Revision ID: 001_initial
Revises:
Create Date: 2026-04-30
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # enum типы
    upscale_mode_enum = sa.Enum(
        "lanczos_2x", "ai_2x", "ai_4x", "ai_4x_anime",
        name="upscale_mode_enum",
    )
    content_type_enum = sa.Enum(
        "photo", "anime",
        name="content_type_enum",
    )
    request_status_enum = sa.Enum(
        "ok", "timeout", "error", "too_large",
        name="request_status_enum",
    )

    # таблица users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("download_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("language", sa.String(5), nullable=False, server_default="ru"),
        sa.Column(
            "default_mode",
            upscale_mode_enum,
            nullable=False,
            server_default="ai_4x",
        ),
        sa.Column(
            "content_type",
            content_type_enum,
            nullable=False,
            server_default="photo",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("telegram_id"),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    # таблица channels
    op.create_table(
        "channels",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("channel_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("invite_link", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("channel_id"),
    )

    # таблица upscale_requests
    op.create_table(
        "upscale_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("mode", upscale_mode_enum, nullable=False),
        sa.Column("model_used", sa.String(100), nullable=True),
        sa.Column("input_size_kb", sa.Integer(), nullable=True),
        sa.Column("output_size_kb", sa.Integer(), nullable=True),
        sa.Column("input_resolution", sa.String(20), nullable=True),
        sa.Column("output_resolution", sa.String(20), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("queue_wait_ms", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            request_status_enum,
            nullable=False,
            server_default="ok",
        ),
        sa.Column("error_text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_upscale_requests_user_id", "upscale_requests", ["user_id"])


def downgrade() -> None:
    op.drop_table("upscale_requests")
    op.drop_table("channels")
    op.drop_table("users")

    # удаляем enum типы
    sa.Enum(name="request_status_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="content_type_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="upscale_mode_enum").drop(op.get_bind(), checkfirst=True)
