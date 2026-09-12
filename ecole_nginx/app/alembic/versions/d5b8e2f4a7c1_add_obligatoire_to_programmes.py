"""add obligatoire to programmes

Revision ID: d5b8e2f4a7c1
Revises: c8f3a6d9b1e4
Create Date: 2026-09-10 00:00:06.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5b8e2f4a7c1'
down_revision: Union[str, Sequence[str], None] = 'c8f3a6d9b1e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('programmes', sa.Column('obligatoire', sa.Boolean(), nullable=True, server_default=sa.true()))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('programmes', 'obligatoire')
