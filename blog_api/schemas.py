from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str

    class Config:
        # Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict, but an ORM model (or any other arbitrary object with attributes).
        orm_mode = True

class PostCreate(PostBase):
    pass

class UserBase(BaseModel):
    email: str

    class Config:
        orm_mode = True

class UserCreated(UserBase):
    password: str

class CommentsBase(BaseModel):
    id: int
    name: str
    body: str
    date_created: datetime

    class Config:
        orm_mode = True

class Comments(CommentsBase):
    children: Optional[List[CommentsBase]] = Field(
        None,
        title="Comments",
    )

    class Config:
        orm_mode = True

class Post(PostBase):
    id: int
    owner_email: str
    title: str
    content: str
    date_created: datetime
    date_last_update: datetime
    like: List[UserBase]
    comments: List[Comments]

    # change default behaviour of BaseModel
    class Config:
        # by default pydantic will lazy loading, which is not load the orm (orm_mode=False)
        # if we wanna refer to owner => post.owner
        # with this config => fetch orm field also
        orm_mode = True

class User(BaseModel):
    id: Optional[int] = Field(
        None,
        title="ID of User",
    )
    email: str
    is_active: Optional[bool] = Field(
        None,
        title="Active status of User",
    )
    role: Optional[str] = Field(
        None,
        title="Role of User",
    )
    posts: Optional[List[PostBase]] = Field(
        None,
        title="Posts belong to User",
    )
    posts_like: Optional[List[PostBase]] = Field(
        None,
        title="Posts was like by User",
    )

    class Config:
        # Pydantic's orm_mode will tell the Pydantic model to read the data even if it is not a dict, but an ORM model (or any other arbitrary object with attributes).
        orm_mode=True