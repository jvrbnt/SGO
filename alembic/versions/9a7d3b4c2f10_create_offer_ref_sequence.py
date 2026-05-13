"""create offer reference sequence

Revision ID: 9a7d3b4c2f10
Revises: c603ec6addeb
Create Date: 2026-05-12 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9a7d3b4c2f10"
down_revision: Union[str, Sequence[str], None] = "c603ec6addeb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the sequence used for concurrency-safe offer references."""
    op.execute("CREATE SEQUENCE IF NOT EXISTS offer_ref_seq START WITH 1 INCREMENT BY 1")
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

            IF max_ref > 0 THEN
                PERFORM setval('offer_ref_seq', max_ref, true);
            ELSE
                PERFORM setval('offer_ref_seq', 1, false);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    """Drop the offer reference sequence."""
    op.execute("DROP SEQUENCE IF EXISTS offer_ref_seq")
