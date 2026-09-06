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
    with op.batch_alter_table('cotizaciones', schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                'titulo_cotizacion',
                sa.String(length=200),
                nullable=False,
                server_default='COTIZACIÓN DE VENTA'
            )
        )

        batch_op.add_column(
            sa.Column(
                'mostrar_imagenes',
                sa.Boolean(),
                nullable=False,
                server_default=sa.true()
            )
        )

        batch_op.add_column(
            sa.Column(
                'responsable_nombre',
                sa.String(length=120),
                nullable=False,
                server_default='Ing. Néstor Huallpa'
            )
        )

        batch_op.add_column(
            sa.Column(
                'responsable_cargo',
                sa.String(length=120),
                nullable=False,
                server_default='Gerente Comercial'
            )
        )

        batch_op.add_column(
            sa.Column(
                'responsable_celular',
                sa.String(length=50),
                nullable=False,
                server_default='73741891'
            )
        )

        batch_op.add_column(
            sa.Column(
                'responsable_email',
                sa.String(length=120),
                nullable=False,
                server_default='redhuall@gmail.com'
            )
        )


def downgrade():
    with op.batch_alter_table('cotizaciones', schema=None) as batch_op:

        batch_op.drop_column('responsable_email')
        batch_op.drop_column('responsable_celular')
        batch_op.drop_column('responsable_cargo')
        batch_op.drop_column('responsable_nombre')
        batch_op.drop_column('mostrar_imagenes')
        batch_op.drop_column('titulo_cotizacion')