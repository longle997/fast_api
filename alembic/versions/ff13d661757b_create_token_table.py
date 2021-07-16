"""create token table

Revision ID: ff13d661757b
Revises: 65762bc32088
Create Date: 2021-07-16 20:04:44.809312

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ff13d661757b'
down_revision = '65762bc32088'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'token',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('access_token', sa.String),
        sa.Column('token_type', sa.String),
    )

def downgrade():
    op.drop_table('token')
