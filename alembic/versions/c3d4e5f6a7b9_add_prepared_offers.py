"""add prepared offers

Revision ID: c3d4e5f6a7b9
Revises: b2c3d4e5f6a8
Create Date: 2026-10-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b9"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prepared_offers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("reference", sa.String(), nullable=False, unique=True),
        sa.Column("service_name", sa.String(), nullable=False),
        sa.Column("hours", sa.Float(), nullable=False),
        sa.Column("consumed_hours", sa.Float(), nullable=False, server_default="0"),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("claimed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_prepared_offers_email", "prepared_offers", ["email"])


def downgrade() -> None:
    op.drop_index("ix_prepared_offers_email", table_name="prepared_offers")
    op.drop_table("prepared_offers")
