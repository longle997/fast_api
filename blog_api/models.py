from datetime import datetime
from typing import List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)
from sqlalchemy import orm
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.schema import ForeignKey
from blog_api.databases import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    role = Column(String, default="user")

    # posts_like field is associated with Post model through link_user_post table
    posts_like = orm.relationship("Post", secondary= 'link_user_post')
    # with this relationship, we can refer post from user. SQLAchemy will find relationship between User and Post
    # and that relationship is one to many through owner_email field
    posts = orm.relationship("Post")

class Post(Base):
    __tablename__ = "posts"
    # all about index https://dataschool.com/sql-optimization/how-indexing-works/
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    owner_email = Column(String, ForeignKey("users.email", ondelete='CASCADE'))
    date_created = Column(DateTime, default=datetime.utcnow())
    date_last_update = Column(DateTime, default=datetime.utcnow())

    # like field is associated with User model through link_user_post table
    # and back_populate mean we are explicit User instance can refer to Post instance through posts_like field
    like = orm.relationship("User", back_populates="posts_like", secondary= 'link_user_post', lazy='selectin')
    # use lazy='selectin' to replace selectin_in from service
    comments = orm.relationship("Comments", lazy='selectin')
    # comments = orm.relationship("Comments")

# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_many_to_many_relationships.htm
class Link_User_Post(Base):
    __tablename__ = "link_user_post"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key= True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key= True)

class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    post = Column(Integer, ForeignKey("posts.id", ondelete='CASCADE'))
    name = Column(String)
    body = Column(String)
    date_created = Column(DateTime, default=datetime.utcnow())

    # https://docs.sqlalchemy.org/en/14/orm/self_referential.html#self-referential
    parent_id = Column(Integer, ForeignKey("comments.id"))
    # why lazy='selectin' don't work in self reference model
    children = orm.relationship("Comments", lazy='selectin')
