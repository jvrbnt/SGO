"""add generated documents

Revision ID: d8e9f0a1b2c3
Revises: b5c1d2e3f4a6
Create Date: 2026-05-12 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d8e9f0a1b2c3"
down_revision: Union[str, Sequence[str], None] = "b5c1d2e3f4a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "generated_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("document_type", sa.String(), nullable=False),
        sa.Column("file_format", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("sha256", sa.String(), nullable=False),
        sa.Column("offer_id", sa.Integer(), nullable=True),
        sa.Column("invoice_id", sa.Integer(), nullable=True),
        sa.Column("created_by_technician_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_technician_id"], ["technicians.id"]),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"]),
        sa.ForeignKeyConstraint(["offer_id"], ["offers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_generated_documents_id"), "generated_documents", ["id"], unique=False)
    op.create_index(op.f("ix_generated_documents_invoice_id"), "generated_documents", ["invoice_id"], unique=False)
    op.create_index(op.f("ix_generated_documents_offer_id"), "generated_documents", ["offer_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_generated_documents_offer_id"), table_name="generated_documents")
    op.drop_index(op.f("ix_generated_documents_invoice_id"), table_name="generated_documents")
    op.drop_index(op.f("ix_generated_documents_id"), table_name="generated_documents")
    op.drop_table("generated_documents")
