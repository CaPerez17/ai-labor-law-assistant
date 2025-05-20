"""Add fecha_registro to usuarios

Revision ID: 35d4023f0192
Revises: 3e1661d2a6b2
Create Date: 2024-03-20 22:13:24.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35d4023f0192'
down_revision: Union[str, None] = '3e1661d2a6b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Añadir columna fecha_registro a la tabla usuarios
    op.add_column('usuarios',
        sa.Column('fecha_registro', sa.DateTime(), nullable=True)
    )


def downgrade() -> None:
    # Eliminar columna fecha_registro de la tabla usuarios
    op.drop_column('usuarios', 'fecha_registro')
