"""init_db

Revision ID: 98a9ae1b9778
Revises: 
Create Date: 2021-08-07 17:47:19.222054

"""
from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.schema import ForeignKey


# revision identifiers, used by Alembic.
revision = '98a9ae1b9778'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    user_table = op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('email', sa.String, unique=True, index=True),
        sa.Column('hashed_password', sa.String),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('role', sa.String, default="user"),
    )
    op.create_table(
        'posts',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('title', sa.String, index=True),
        sa.Column('content', sa.String, index=True),
        sa.Column('date_created', sa.DateTime, default=datetime.now()),
        sa.Column('date_last_update', sa.DateTime, default=datetime.now()),
    )
    op.add_column('posts',
        sa.Column('owner_email', sa.String, ForeignKey('users.email', ondelete='CASCADE'))
    )
    op.create_table(
        'link_user_post',
        sa.Column('user_id', sa.Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('post_id', sa.Integer, ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True)
    )
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('post', sa.Integer, ForeignKey('posts.id', ondelete='CASCADE')),
        sa.Column('name', sa.String, index=True),
        sa.Column('body', sa.String),
        sa.Column('date_created', sa.DateTime, default=datetime.now()),
        sa.Column('parent_id', sa.Integer, ForeignKey('comments.id', ondelete='CASCADE')),
    )
    op.bulk_insert(user_table,
        [
            {
                'id': 0,
                'email': 'Admin@company.com',
                'hashed_password': '$2b$12$o7KXV0ltCWEvYaukPFcqo.xQXM2zMD7nowBSQfw466hwNzBz5685q',
                'is_active': True,
                'role': 'admin'
            }
        ]
    )


def downgrade():
    pass
