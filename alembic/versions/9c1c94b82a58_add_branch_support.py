"""add_branch_support

Revision ID: 9c1c94b82a58
Revises: 52002974ff6a
Create Date: 2026-02-16 21:38:18.314035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c1c94b82a58'
down_revision: Union[str, None] = '52002974ff6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create branches table
    op.create_table(
        'branches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('is_main_branch', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_branches_id'), 'branches', ['id'], unique=False)
    op.create_index(op.f('ix_branches_code'), 'branches', ['code'], unique=True)
    op.create_index(op.f('ix_branches_is_active'), 'branches', ['is_active'], unique=False)
    
    # Create user_branches association table (many-to-many)
    op.create_table(
        'user_branches',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('branch_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'branch_id')
    )
    
    # Add primary_branch_id to users table
    op.add_column('users', sa.Column('primary_branch_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_primary_branch', 'users', 'branches', ['primary_branch_id'], ['id'])
    
    # Seed a "Main Branch" for existing single-branch schools (backward compatibility)
    # This ensures existing schools continue working without changes
    op.execute("""
        INSERT INTO branches (name, code, address, is_main_branch, is_active)
        VALUES ('Main Branch', 'MAIN', 'Main Campus', 1, 1)
    """)
    
    # Assign all existing users to the Main Branch
    op.execute("""
        UPDATE users
        SET primary_branch_id = (SELECT id FROM branches WHERE code = 'MAIN' LIMIT 1)
        WHERE role IN ('branch_admin', 'branch_principal')
    """)


def downgrade() -> None:
    # Remove foreign key and column from users
    op.drop_constraint('fk_users_primary_branch', 'users', type_='foreignkey')
    op.drop_column('users', 'primary_branch_id')
    
    # Drop association table
    op.drop_table('user_branches')
    
    # Drop branches table
    op.drop_index(op.f('ix_branches_is_active'), table_name='branches')
    op.drop_index(op.f('ix_branches_code'), table_name='branches')
    op.drop_index(op.f('ix_branches_id'), table_name='branches')
    op.drop_table('branches')
