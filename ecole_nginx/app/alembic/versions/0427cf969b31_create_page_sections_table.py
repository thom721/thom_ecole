"""create_page_sections_table

Revision ID: 0427cf969b31
Revises: 92c34921c4ae
Create Date: 2026-05-16 16:18:16.720983

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0427cf969b31'
down_revision: Union[str, Sequence[str], None] = '92c34921c4ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'page_sections',
        sa.Column('id',          sa.Integer(),     primary_key=True, index=True),
        sa.Column('page',        sa.String(50),    nullable=False, index=True),
        sa.Column('section_key', sa.String(50),    nullable=False),
        sa.Column('titre',       sa.String(255),   nullable=True),
        sa.Column('sous_titre',  sa.String(255),   nullable=True),
        sa.Column('description', sa.Text(),        nullable=True),
        sa.Column('is_visible',  sa.Boolean(),     nullable=True, server_default=sa.text('1')),
        sa.Column('ordre',       sa.Integer(),     nullable=True, server_default='0'),
        sa.Column('items',       sa.JSON(),        nullable=True),
        sa.Column('created_at',  sa.DateTime(),    nullable=True),
        sa.Column('updated_at',  sa.DateTime(),    nullable=True),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB'
    )


def downgrade() -> None:
    op.drop_table('page_sections')
