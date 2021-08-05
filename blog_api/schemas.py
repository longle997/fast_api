from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from pydantic.class_validators import validator

from sqlalchemy.sql.sqltypes import Boolean

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    owner_email: str
    date_created: datetime
    date_last_update: datetime

    # change default behaviour of BaseModel
    class Config:
        # by default pydantic will lazy loading, which is not load the orm (orm_mode=False)
        # if we wanna refer to owner => post.owner
        # with this config => fetch orm field also
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserCreated(UserBase):
    password: str

class User(UserBase):
    id: Optional[int] = Field(
        None,
        title="ID of User",
    )
    is_active: Optional[bool] = Field(
        None,
        title="Actice status of User",
    )
    posts: Optional[List[Post]] = Field(
        None,
        title="Posts belong to User",
    )

    class Config:
        # Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict, but an ORM model (or any other arbitrary object with attributes).
        orm_mode=True