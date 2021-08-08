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
from sqlalchemy.sql.schema import ForeignKey
from blog_api.databases import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)

    # with this relationship, we can refer post from user and vice versa
    posts = orm.relationship("Post", secondary= 'link_user_post')

class Post(Base):
    __tablename__ = "posts"
    # all about index https://dataschool.com/sql-optimization/how-indexing-works/
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    owner_email = Column(String, ForeignKey("users.email"))
    date_created = Column(DateTime, default=datetime.utcnow())
    date_last_update = Column(DateTime, default=datetime.utcnow())

    like = orm.relationship("User", secondary= 'link_user_post')

# https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_many_to_many_relationships.htm
class Link_User_Post(Base):
    __tablename__ = "link_user_post"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key= True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key= True)