"""add user creation tracking

Revision ID: 002_add_user_creation_tracking
Revises: 001_initial_migration
Create Date: 2026-07-23 08:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from app.models.base import GUID

# revision identifiers, used by Alembic.
revision: str = '002_add_user_creation_tracking'
down_revision: Union[str, Sequence[str], None] = '001_initial_migration'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('users')]

    if 'created_by_app_id' not in columns:
        op.add_column('users', sa.Column('created_by_app_id', GUID(), sa.ForeignKey('applications.id', ondelete='SET NULL'), nullable=True))
    if 'creation_source' not in columns:
        op.add_column('users', sa.Column('creation_source', sa.String(), nullable=False, server_default='PORTAL_ADMIN'))

    indexes = [idx['name'] for idx in inspector.get_indexes('users')]
    if 'ix_users_created_by_app_id' not in indexes:
        op.create_index(op.f('ix_users_created_by_app_id'), 'users', ['created_by_app_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_index(op.f('ix_users_created_by_app_id'))
        batch_op.drop_column('creation_source')
        batch_op.drop_column('created_by_app_id')
