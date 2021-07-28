"""change owner_id to owner_email

Revision ID: 65762bc32088
Revises: 002f7b2209f0
Create Date: 2021-07-16 15:37:21.235705

"""
from sqlalchemy.sql.schema import ForeignKey
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65762bc32088'
down_revision = '002f7b2209f0'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column(
        'posts', 'owner_id'
    )
    op.add_column('posts',
        sa.Column('owner_email', sa.String, ForeignKey('users.email'))
    )


def downgrade():
    pass
