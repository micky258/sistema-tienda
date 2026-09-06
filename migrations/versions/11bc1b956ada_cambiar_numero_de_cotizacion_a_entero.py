"""cambiar numero de cotizacion a entero

Revision ID: 11bc1b956ada
Revises:
Create Date: 2026-03-04 03:52:29.501763
"""

from alembic import op


revision = '11bc1b956ada'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Se conserva numero como texto.
    # El modelo actual utiliza String(10).
    pass


def downgrade():
    pass