"""add profiles and traceability

Revision ID: b5c1d2e3f4a6
Revises: 9a7d3b4c2f10
Create Date: 2026-05-12 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b5c1d2e3f4a6"
down_revision: Union[str, Sequence[str], None] = "9a7d3b4c2f10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("display_name", sa.String(), nullable=True))
    op.add_column("technicians", sa.Column("display_name", sa.String(), nullable=True))

    op.create_table(
        "traceability_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("offer_id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("request_date", sa.DateTime(), nullable=True),
        sa.Column("acceptance_date", sa.DateTime(), nullable=True),
        sa.Column("delivery_date", sa.DateTime(), nullable=True),
        sa.Column("mina_autoservicio", sa.String(), nullable=True),
        sa.Column("sample_provided", sa.String(), nullable=True),
        sa.Column("verification", sa.String(), nullable=True),
        sa.Column("charge_note", sa.String(), nullable=True),
        sa.Column("conformity", sa.String(), nullable=True),
        sa.Column("observations", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["offer_id"], ["offers.id"]),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("service_id", name="uq_traceability_service_id"),
    )
    op.create_index(op.f("ix_traceability_entries_id"), "traceability_entries", ["id"], unique=False)
    op.create_index(op.f("ix_traceability_entries_offer_id"), "traceability_entries", ["offer_id"], unique=False)
    op.create_index(op.f("ix_traceability_entries_service_id"), "traceability_entries", ["service_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_traceability_entries_service_id"), table_name="traceability_entries")
    op.drop_index(op.f("ix_traceability_entries_offer_id"), table_name="traceability_entries")
    op.drop_index(op.f("ix_traceability_entries_id"), table_name="traceability_entries")
    op.drop_table("traceability_entries")
    op.drop_column("technicians", "display_name")
    op.drop_column("clients", "display_name")
