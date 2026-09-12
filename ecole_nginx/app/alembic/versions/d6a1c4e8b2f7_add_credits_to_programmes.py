"""add credits to programmes

Revision ID: d6a1c4e8b2f7
Revises: b3f7e2a9c5d1
Create Date: 2026-09-10 00:00:01.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6a1c4e8b2f7'
down_revision: Union[str, Sequence[str], None] = 'b3f7e2a9c5d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('programmes', sa.Column('credits', sa.Numeric(4, 1), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('programmes', 'credits')
