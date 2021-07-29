"""remove post_id column

Revision ID: 002f7b2209f0
Revises: 56546d66bb41
Create Date: 2021-07-16 09:02:02.936809

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002f7b2209f0'
down_revision = '56546d66bb41'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('users', 'post_id')


def downgrade():
    pass
