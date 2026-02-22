"""Manual profile fields

Revision ID: 59f8f47ed882
Revises: 9400fce0d339
Create Date: 2026-02-22 14:54:03.179282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59f8f47ed882'
down_revision: Union[str, None] = '9400fce0d339'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # super_admins table only exists in the master registry.
    # Tenant databases don't have it, so skip this migration for them.
    if inspector.has_table('super_admins'):
        op.add_column('super_admins', sa.Column('phone', sa.String(length=20), nullable=True))
        op.add_column('super_admins', sa.Column('position', sa.String(length=100), nullable=True))
        op.add_column('super_admins', sa.Column('location', sa.String(length=200), nullable=True))
        op.add_column('super_admins', sa.Column('state', sa.String(length=200), nullable=True))
        op.add_column('super_admins', sa.Column('pin', sa.String(length=20), nullable=True))
        op.add_column('super_admins', sa.Column('zip', sa.String(length=20), nullable=True))
        op.add_column('super_admins', sa.Column('tax_no', sa.String(length=50), nullable=True))
        op.add_column('super_admins', sa.Column('facebook_url', sa.String(length=255), nullable=True))
        op.add_column('super_admins', sa.Column('twitter_url', sa.String(length=255), nullable=True))
        op.add_column('super_admins', sa.Column('github_url', sa.String(length=255), nullable=True))
        op.add_column('super_admins', sa.Column('dribbble_url', sa.String(length=255), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if inspector.has_table('super_admins'):
        op.drop_column('super_admins', 'dribbble_url')
        op.drop_column('super_admins', 'github_url')
        op.drop_column('super_admins', 'twitter_url')
        op.drop_column('super_admins', 'facebook_url')
        op.drop_column('super_admins', 'tax_no')
        op.drop_column('super_admins', 'zip')
        op.drop_column('super_admins', 'pin')
        op.drop_column('super_admins', 'state')
        op.drop_column('super_admins', 'location')
        op.drop_column('super_admins', 'position')
        op.drop_column('super_admins', 'phone')
