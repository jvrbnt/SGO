"""add possible investigator principals

Revision ID: a7b8c9d0e1f2
Revises: f2a3b4c5d6e7
Create Date: 2026-09-24
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "f2a3b4c5d6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


POSSIBLE_IPS = [
    "Alén Millán, Benito",
    "Buencuerpo Fariña, Jerónimo",
    "Caballero Calero, Olga",
    "Calleja Gómez, Montserrat",
    "Cano Tortajada, Álvaro",
    "Cárabe López, Julio",
    "Cebollada Navarro, Alfonso",
    "Conca Parra, Andrés",
    "Costa Kramer, José L.",
    "Dotor Castilla, Mª Luisa",
    "Garay Ruiz, Diego",
    "García López, Sergio",
    "García Martín, Antonio",
    "García Martínez, Jorge M.",
    "García-Martín, José Miguel",
    "Gil Santos, Eduardo",
    "González Diez, Yolanda",
    "González Sagardoy, Mª Ujué",
    "Isasi Campillo, Miriam",
    "Kosaka Monteiro, Priscila",
    "Llorens Montolio, José M.",
    "Lohani, Ketan",
    "López Yubero, Marina Pilar",
    "Luna Estévez, Mónica",
    "Malvar Vidal, Oscar",
    "Martín González, Marisol",
    "Mobini, Sahba",
    "Molina Fernández, Juan",
    "Moreno Sanabria, Luis",
    "Navajas Hernández, David",
    "Palmero, Ester M.",
    "Ripalda Cobián, José María",
    "Rodríguez Peña, Micaela",
    "Ruz Martínez, José Jaime",
    "San Paulo Hernando, Álvaro",
    "Tamayo Miguel de, Javier",
    "Vicente Manzano, M. Cristina",
]


def upgrade() -> None:
    possible_ips = op.create_table(
        "possible_ips",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_possible_ips_id", "possible_ips", ["id"], unique=False)
    op.create_index("ix_possible_ips_name", "possible_ips", ["name"], unique=False)
    op.bulk_insert(possible_ips, [{"name": name} for name in POSSIBLE_IPS])


def downgrade() -> None:
    op.drop_index("ix_possible_ips_name", table_name="possible_ips")
    op.drop_index("ix_possible_ips_id", table_name="possible_ips")
    op.drop_table("possible_ips")