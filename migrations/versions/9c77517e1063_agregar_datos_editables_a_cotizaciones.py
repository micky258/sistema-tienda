"""agregar datos editables a cotizaciones

Revision ID: 9c77517e1063
Revises: 11bc1b956ada
Create Date: 2026-09-05 19:55:51.846461

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c77517e1063'
down_revision = '11bc1b956ada'
branch_labels = None
depends_on = None


def upgrade():

    op.add_column(
        'cotizaciones',
        sa.Column(
            'titulo_cotizacion',
            sa.String(length=200),
            nullable=False,
            server_default='COTIZACIÓN DE VENTA'
        )
    )

    op.add_column(
        'cotizaciones',
        sa.Column(
            'mostrar_imagenes',
            sa.Boolean(),
            nullable=False,
            server_default=sa.true()
        )
    )

    op.add_column(
        'cotizaciones',
        sa.Column(
            'responsable_nombre',
            sa.String(length=120),
            nullable=False,
            server_default='Ing. Néstor Huallpa'
        )
    )

    op.add_column(
        'cotizaciones',
        sa.Column(
            'responsable_cargo',
            sa.String(length=120),
            nullable=False,
            server_default='Gerente Comercial'
        )
    )

    op.add_column(
        'cotizaciones',
        sa.Column(
            'responsable_celular',
            sa.String(length=50),
            nullable=False,
            server_default='73741891'
        )
    )

    op.add_column(
        'cotizaciones',
        sa.Column(
            'responsable_email',
            sa.String(length=120),
            nullable=False,
            server_default='redhuall@gmail.com'
        )
    )


def downgrade():

    op.drop_column('cotizaciones', 'responsable_email')
    op.drop_column('cotizaciones', 'responsable_celular')
    op.drop_column('cotizaciones', 'responsable_cargo')
    op.drop_column('cotizaciones', 'responsable_nombre')
    op.drop_column('cotizaciones', 'mostrar_imagenes')
    op.drop_column('cotizaciones', 'titulo_cotizacion')