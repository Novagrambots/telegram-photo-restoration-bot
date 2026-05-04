"""Переименование users.download_count → users.restored_count.

Revision ID: 003_rename_download_count
Revises: 002_restoration
Create Date: 2026-05-04
"""
from typing import Sequence, Union

from alembic import op


revision: str = "003_rename_download_count"
down_revision: Union[str, None] = "002_restoration"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "download_count", new_column_name="restored_count")


def downgrade() -> None:
    op.alter_column("users", "restored_count", new_column_name="download_count")
