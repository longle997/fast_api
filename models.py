from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)
from sqlalchemy import orm
from sqlalchemy.sql.schema import ForeignKey
import databases

class User(databases.Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # with this relationship, we can refer post from user and vice versa
    posts = orm.relationship("Post", back_populates="owner")

class Post(databases.Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    date_created = Column(DateTime, default=datetime.utcnow())
    date_last_update = Column(DateTime, default=datetime.utcnow())

    owner = orm.relationship("User", back_populates="posts")