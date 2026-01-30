"""add_index_and_ai_column

Revision ID: 6a26fa45dd7b
Revises: 
Create Date: 2026-01-30 17:02:25.436121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a26fa45dd7b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Add Index to speed up full_name search
    op.create_index('ix_users_full_name', 'users', ['full_name'])
    
    # 2. Add new column for the AI project (Preparation for Project 2)
    op.add_column('users', sa.Column('ai_summary', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'ai_summary')
    op.drop_index('ix_users_full_name', table_name='users')
