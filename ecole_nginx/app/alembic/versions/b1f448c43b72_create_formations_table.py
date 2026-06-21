"""create_formations_table

Revision ID: b1f448c43b72
Revises: 28c8993626d0
Create Date: 2026-05-16 15:52:50.993651

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b1f448c43b72'
down_revision: Union[str, Sequence[str], None] = '28c8993626d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'formations',
        sa.Column('id',               sa.Integer(),     primary_key=True, index=True),
        sa.Column('niveau',           sa.String(100),   nullable=False),
        sa.Column('titre',            sa.String(255),   nullable=False),
        sa.Column('duree',            sa.String(50),    nullable=True),
        sa.Column('couleur',          sa.String(20),    nullable=True, server_default='#3b82f6'),
        sa.Column('image_url',        sa.String(500),   nullable=True),
        sa.Column('description',      sa.Text(),        nullable=True),
        sa.Column('matieres',         sa.JSON(),        nullable=True),
        sa.Column('nb_eleves_classe', sa.String(20),    nullable=True),
        sa.Column('taux_reussite',    sa.String(20),    nullable=True),
        sa.Column('nb_debouches',     sa.String(20),    nullable=True),
        sa.Column('debouches',        sa.JSON(),        nullable=True),
        sa.Column('ordre',            sa.Integer(),     nullable=True, server_default='0'),
        sa.Column('is_published',     sa.Boolean(),     nullable=True, server_default=sa.text('1')),
        sa.Column('created_at',       sa.DateTime(),    nullable=True),
        sa.Column('updated_at',       sa.DateTime(),    nullable=True),
        mysql_collate='utf8mb4_unicode_ci',
        mysql_charset='utf8mb4',
        mysql_engine='InnoDB'
    )


def downgrade() -> None:
    op.drop_table('formations')
