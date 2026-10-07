"""add email verification to clients

Revision ID: d4e5f6a7b8c0
Revises: c3d4e5f6a7b9
Create Date: 2026-10-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4e5f6a7b8c0"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Accounts that already exist are considered verified.
    op.add_column("clients", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.alter_column("clients", "email_verified", server_default=None)
    op.add_column("clients", sa.Column("email_verification_hash", sa.String(), nullable=True))
    op.add_column("clients", sa.Column("email_verification_expires", sa.DateTime(), nullable=True))
    op.add_column("clients", sa.Column("verification_poll_hash", sa.String(), nullable=True))
    op.create_index("ix_clients_email_verification_hash", "clients", ["email_verification_hash"])


def downgrade() -> None:
    op.drop_index("ix_clients_email_verification_hash", table_name="clients")
    op.drop_column("clients", "verification_poll_hash")
    op.drop_column("clients", "email_verification_expires")
    op.drop_column("clients", "email_verification_hash")
    op.drop_column("clients", "email_verified")
