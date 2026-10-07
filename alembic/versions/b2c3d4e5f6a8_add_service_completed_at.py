"""add completed_at to services

Revision ID: b2c3d4e5f6a8
Revises: a1b2c3d4e5f7
Create Date: 2026-10-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a8"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("services", sa.Column("completed_at", sa.DateTime(), nullable=True))
    op.execute("UPDATE services SET completed_at = NOW() WHERE status = 'done'")


def downgrade() -> None:
    op.drop_column("services", "completed_at")
