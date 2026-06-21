"""ajouter_table

Revision ID: f2d97f76ba00
Revises: 1df4933c7bf7
Create Date: 2026-03-02 17:38:49.335512

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2d97f76ba00'
down_revision: Union[str, Sequence[str], None] = '1df4933c7bf7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # === categories ===
    op.create_table(
        'categories',
        sa.Column('id',         sa.Integer(),     primary_key=True, index=True),
        sa.Column('name',       sa.String(100),   nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(),    nullable=True),
        sa.Column('updated_at', sa.DateTime(),    nullable=True),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB'
    )

    # === events ===
    op.create_table(
        'events',
        sa.Column('id',           sa.Integer(),                          primary_key=True, index=True),
        sa.Column('title',        sa.String(255),                        nullable=False),
        sa.Column('description',  sa.Text(),                             nullable=True),
        sa.Column('location',     sa.String(255),                        nullable=True),
        sa.Column('start_date',   sa.DateTime(),                         nullable=False),
        sa.Column('end_date',     sa.DateTime(),                         nullable=True),
        sa.Column('image_url',    sa.String(500),                        nullable=True),
        sa.Column('audience',     sa.Enum('public','classe','professeurs'), nullable=True),
        sa.Column('is_published', sa.Boolean(),                          nullable=True),
        sa.Column('category_id',  sa.Integer(),                          nullable=True),
        sa.Column('created_at',   sa.DateTime(),                         nullable=True),
        sa.Column('updated_at',   sa.DateTime(),                         nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB'
    )

    # === news ===
    op.create_table(
        'news',
        sa.Column('id',           sa.Integer(),                          primary_key=True, index=True),
        sa.Column('title',        sa.String(255),                        nullable=False),
        sa.Column('content',      sa.Text(),                             nullable=True),
        sa.Column('image_url',    sa.String(500),                        nullable=True),
        sa.Column('audience',     sa.Enum('public','classe','professeurs'), nullable=True),
        sa.Column('is_published', sa.Boolean(),                          nullable=True),
        sa.Column('published_at', sa.DateTime(),                         nullable=True),
        sa.Column('category_id',  sa.Integer(),                          nullable=True),
        sa.Column('created_at',   sa.DateTime(),                         nullable=True),
        sa.Column('updated_at',   sa.DateTime(),                         nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('news')
    op.drop_table('events')
    op.drop_table('categories')
