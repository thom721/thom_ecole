"""staff_system_role

Revision ID: fe9259fd440a
Revises: 67554ae79df6
Create Date: 2026-09-09 16:44:31.182751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe9259fd440a'
down_revision = '67554ae79df6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Élargissement manuel de l'ENUM MySQL (jamais détecté par l'autogenerate,
    # même limitation que chaque epic depuis l'Épic 1) — voir plan Épic 23.
    op.alter_column('users', 'system_role',
        existing_type=sa.Enum('student', 'teacher', 'admin', name='systemrole'),
        type_=sa.Enum('student', 'teacher', 'admin', 'staff', name='systemrole'),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column('users', 'system_role',
        existing_type=sa.Enum('student', 'teacher', 'admin', 'staff', name='systemrole'),
        type_=sa.Enum('student', 'teacher', 'admin', name='systemrole'),
        existing_nullable=False,
    )
