"""ajouter_image_url_a_facultes

Revision ID: e5a8c2f4b7d9
Revises: d7f3a1c5e9b2
Create Date: 2026-08-29 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5a8c2f4b7d9'
down_revision: Union[str, Sequence[str], None] = 'd7f3a1c5e9b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('facultes', sa.Column('image_url', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('facultes', 'image_url')
