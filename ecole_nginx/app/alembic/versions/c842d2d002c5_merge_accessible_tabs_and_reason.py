"""merge_accessible_tabs_and_reason

Revision ID: c842d2d002c5
Revises: a1b2c3d4e5f6, a1c5e9b7d3f2
Create Date: 2026-06-29 13:23:48.120126

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c842d2d002c5'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f6', 'a1c5e9b7d3f2')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
