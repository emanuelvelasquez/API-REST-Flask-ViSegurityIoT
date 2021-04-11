"""empty message

Revision ID: 87e3bfbc9635
Revises: 
Create Date: 2021-01-15 03:30:52.173153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87e3bfbc9635'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('eventos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('evento', sa.String(length=30), nullable=True),
    sa.Column('hora', sa.DateTime(), nullable=True),
    sa.Column('path', sa.String(length=100), nullable=True),
    sa.Column('revisado', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('funciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('funcion', sa.String(length=30), nullable=True),
    sa.Column('corriendo', sa.Boolean(), nullable=True),
    sa.Column('inicio', sa.Integer(), nullable=True),
    sa.Column('fin', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('medionotificaciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=True),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=True),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('usuarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=60), nullable=True),
    sa.Column('username', sa.String(length=60), nullable=True),
    sa.Column('id_telegram', sa.String(length=50), nullable=True),
    sa.Column('nombre', sa.String(length=60), nullable=True),
    sa.Column('apellido', sa.String(length=60), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_usuarios_apellido'), 'usuarios', ['apellido'], unique=False)
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True)
    op.create_index(op.f('ix_usuarios_id_telegram'), 'usuarios', ['id_telegram'], unique=False)
    op.create_index(op.f('ix_usuarios_nombre'), 'usuarios', ['nombre'], unique=False)
    op.create_index(op.f('ix_usuarios_username'), 'usuarios', ['username'], unique=True)
    op.create_table('usuarionotificacion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=True),
    sa.Column('medionotificacion_id', sa.Integer(), nullable=True),
    sa.Column('notificado', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['medionotificacion_id'], ['medionotificaciones.id'], ),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('usuarionotificacion')
    op.drop_index(op.f('ix_usuarios_username'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_nombre'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_id_telegram'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_email'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_apellido'), table_name='usuarios')
    op.drop_table('usuarios')
    op.drop_table('roles')
    op.drop_table('medionotificaciones')
    op.drop_table('funciones')
    op.drop_table('eventos')
    # ### end Alembic commands ###