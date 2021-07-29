"""remove a column

Revision ID: 56546d66bb41
Revises: bd2f8a82139f
Create Date: 2021-07-15 21:56:03.888235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '56546d66bb41'
down_revision = 'bd2f8a82139f'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    op.drop_column('users', 'post_id')
