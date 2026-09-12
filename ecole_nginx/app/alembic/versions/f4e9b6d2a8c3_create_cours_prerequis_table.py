"""create cours_prerequis table

Revision ID: f4e9b6d2a8c3
Revises: d6a1c4e8b2f7
Create Date: 2026-09-10 00:00:02.000000

"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4e9b6d2a8c3'
down_revision: Union[str, Sequence[str], None] = 'd6a1c4e8b2f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'cours_prerequis',
        sa.Column('id', sa.CHAR(36), primary_key=True, default=uuid.uuid4),
        sa.Column('cours_id', sa.CHAR(36), sa.ForeignKey('cours.id'), nullable=False),
        sa.Column('prerequis_cours_id', sa.CHAR(36), sa.ForeignKey('cours.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cours_id', 'prerequis_cours_id', name='uq_cours_prerequis'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        mysql_engine='InnoDB',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('cours_prerequis')
