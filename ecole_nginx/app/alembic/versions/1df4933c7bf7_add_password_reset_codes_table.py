"""add password_reset_codes table

Revision ID: 1df4933c7bf7
Revises: 62c8bf64ad57
Create Date: 2026-02-23 07:32:15.531233

"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1df4933c7bf7'
down_revision: Union[str, Sequence[str], None] = '62c8bf64ad57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'password_reset_codes',
        # sa.Column('id',         sa.Integer(),     nullable=False, autoincrement=True),
        sa.Column('id', sa.String(36), primary_key=True, default=uuid.uuid4),
        sa.Column('email',      sa.String(255),   nullable=False),
        sa.Column('code',       sa.String(6),     nullable=False),
        sa.Column('used',       sa.Boolean(),     nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(),    nullable=False),
        sa.Column('created_at', sa.DateTime(),    nullable=True,  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_password_reset_codes_email', 'password_reset_codes', ['email'])

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_password_reset_codes_email', table_name='password_reset_codes')
    op.drop_table('password_reset_codes')
 
