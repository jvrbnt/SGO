"""sync offer reference sequence with existing PO references

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-09-24
"""
from typing import Sequence, Union

from alembic import op


revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, Sequence[str], None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        DECLARE
            max_ref integer;
        BEGIN
            SELECT COALESCE(MAX(CAST(substring(reference from '^[0-9]+') AS integer)), 0)
            INTO max_ref
            FROM offers
            WHERE reference ~ '^[0-9]+';

            IF max_ref = 0 THEN
                -- PO_001_2026 is the last existing request document, so the next is 002.
                PERFORM setval('offer_ref_seq', 1, false);
            ELSE
                PERFORM setval('offer_ref_seq', max_ref, true);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    pass