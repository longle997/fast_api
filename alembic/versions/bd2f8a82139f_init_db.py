"""init db

Revision ID: bd2f8a82139f
Revises: 
Create Date: 2021-06-27 16:09:07.085439

"""
from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.sql.schema import Column, ForeignKey
from models import User, Post


# revision identifiers, used by Alembic.
revision = 'bd2f8a82139f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('email', sa.String, unique=True, index=True),
        sa.Column('hashed_password', sa.String),
        sa.Column('is_active', sa.Boolean, default=True),
    )
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('title', sa.String, index=True),
        sa.Column('content', sa.String, index=True),
        sa.Column('date_created', sa.DateTime, default=datetime.now()),
        sa.Column('date_last_update', sa.DateTime, default=datetime.now()),
    )
    op.add_column('users',
        Column('post_id', sa.Integer, ForeignKey('posts.id'))
    )
    op.add_column('posts',
        Column('owner_id', sa.Integer, ForeignKey('users.id')),
    )


def downgrade():
    pass
