"""Переход с upscale на restoration: новые enum, новая таблица restore_requests.

Revision ID: 002_restoration
Revises: 001_initial
Create Date: 2026-05-01
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "002_restoration"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) удалить старую таблицу upscale_requests (с её внешними ключами)
    op.execute("DROP TABLE IF EXISTS upscale_requests CASCADE")

    # 2) удалить колонку content_type у users
    with op.batch_alter_table("users") as batch:
        batch.drop_column("content_type")
        # default_mode → удалим тоже, потом пересоздадим под новый enum
        batch.drop_column("default_mode")

    # 3) удалить старые enum-типы
    op.execute("DROP TYPE IF EXISTS content_type_enum CASCADE")
    op.execute("DROP TYPE IF EXISTS upscale_mode_enum CASCADE")

    # 4) создать новый enum restore_mode_enum
    restore_mode_enum = sa.Enum(
        "restore_full", "colorize", "upscale_lanczos",
        name="restore_mode_enum",
    )
    restore_mode_enum.create(op.get_bind(), checkfirst=True)

    # 5) добавить новый default_mode (nullable=True, default='restore_full')
    op.add_column(
        "users",
        sa.Column(
            "default_mode",
            restore_mode_enum,
            nullable=True,
            server_default="restore_full",
        ),
    )

    # 6) создать таблицу restore_requests
    request_status_enum = sa.Enum(
        "ok", "timeout", "error", "too_large",
        name="request_status_enum",
    )
    # request_status_enum остался от 001 — checkfirst, чтобы не упало
    request_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "restore_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("mode", restore_mode_enum, nullable=False),
        sa.Column("models_used", sa.String(255), nullable=True),
        sa.Column("space_used", sa.String(100), nullable=True),
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
    op.create_index("ix_restore_requests_user_id", "restore_requests", ["user_id"])


def downgrade() -> None:
    # Симметричный откат: drop restore_requests, вернуть upscale_requests + content_type.
    op.execute("DROP TABLE IF EXISTS restore_requests CASCADE")

    with op.batch_alter_table("users") as batch:
        batch.drop_column("default_mode")

    op.execute("DROP TYPE IF EXISTS restore_mode_enum CASCADE")

    upscale_mode_enum = sa.Enum(
        "lanczos_2x", "ai_2x", "ai_4x", "ai_4x_anime",
        name="upscale_mode_enum",
    )
    upscale_mode_enum.create(op.get_bind(), checkfirst=True)

    content_type_enum = sa.Enum(
        "photo", "anime",
        name="content_type_enum",
    )
    content_type_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "default_mode",
            upscale_mode_enum,
            nullable=False,
            server_default="ai_4x",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "content_type",
            content_type_enum,
            nullable=False,
            server_default="photo",
        ),
    )
