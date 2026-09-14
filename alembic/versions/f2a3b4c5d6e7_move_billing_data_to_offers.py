"""move billing data from clients to offers

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-09-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, Sequence[str], None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("offers", sa.Column("investigador_principal", sa.String(), nullable=True))
    op.add_column("offers", sa.Column("cuenta_interna", sa.String(), nullable=True))
    op.add_column("offers", sa.Column("codigo_proyecto", sa.String(), nullable=True))
    op.execute(sa.text("""
        UPDATE offers
        SET investigador_principal = clients.investigador_principal,
            cuenta_interna = clients.cuenta_interna,
            codigo_proyecto = clients.codigo_proyecto
        FROM clients
        WHERE offers.client_id = clients.id
    """))
    op.drop_column("clients", "investigador_principal")
    op.drop_column("clients", "cuenta_interna")
    op.drop_column("clients", "codigo_proyecto")


def downgrade() -> None:
    op.add_column("clients", sa.Column("investigador_principal", sa.String(), nullable=True))
    op.add_column("clients", sa.Column("cuenta_interna", sa.String(), nullable=True))
    op.add_column("clients", sa.Column("codigo_proyecto", sa.String(), nullable=True))
    op.execute(sa.text("""
        UPDATE clients
        SET investigador_principal = latest.investigador_principal,
            cuenta_interna = latest.cuenta_interna,
            codigo_proyecto = latest.codigo_proyecto
        FROM (
            SELECT DISTINCT ON (client_id) client_id, investigador_principal,
                cuenta_interna, codigo_proyecto
            FROM offers
            ORDER BY client_id, created_at DESC
        ) AS latest
        WHERE clients.id = latest.client_id
    """))
    op.drop_column("offers", "investigador_principal")
    op.drop_column("offers", "cuenta_interna")
    op.drop_column("offers", "codigo_proyecto")