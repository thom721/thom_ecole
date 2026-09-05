"""ajouter_layout_image_a_page_sections

Revision ID: b8e2f4a6c1d3
Revises: f3a7c1d9b4e2
Create Date: 2026-08-29 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8e2f4a6c1d3'
down_revision: Union[str, Sequence[str], None] = 'f3a7c1d9b4e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('page_sections', sa.Column('layout', sa.String(50), nullable=True))
    op.add_column('page_sections', sa.Column('image_url', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('page_sections', 'image_url')
    op.drop_column('page_sections', 'layout')
