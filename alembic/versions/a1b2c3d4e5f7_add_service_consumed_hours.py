"""add consumed hours to services

Revision ID: a1b2c3d4e5f7
Revises: d0e1f2a3b4c5
Create Date: 2026-10-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f7"
down_revision: Union[str, Sequence[str], None] = "d0e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("services", sa.Column("consumed_hours", sa.Float(), nullable=False, server_default="0"))
    # Services already marked as done are assumed to have consumed all their hours.
    op.execute("UPDATE services SET consumed_hours = hours WHERE status = 'done'")


def downgrade() -> None:
    op.drop_column("services", "consumed_hours")
