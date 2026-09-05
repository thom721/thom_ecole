"""create_videos_table

Revision ID: f9c3b6a1d8e4
Revises: e5a8c2f4b7d9
Create Date: 2026-08-30 09:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9c3b6a1d8e4'
down_revision: Union[str, Sequence[str], None] = 'e5a8c2f4b7d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'videos',
        sa.Column('id',           sa.CHAR(36),    primary_key=True),
        sa.Column('titre',        sa.String(255), nullable=False),
        sa.Column('source',       sa.String(255), nullable=True),
        sa.Column('youtube_url',  sa.String(500), nullable=False),
        sa.Column('is_published', sa.Boolean(),   nullable=True, server_default=sa.text('1')),
        sa.Column('created_at',   sa.DateTime(),  nullable=True),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB'
    )


def downgrade() -> None:
    op.drop_table('videos')
