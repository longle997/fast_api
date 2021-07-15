# We will run this file by uvicorn

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy import orm
from sqlalchemy.orm.session import Session
import services

from typing import List

from schemas import(
    User,
    UserCreated,
    Post,
    PostCreate
)

# Initialize app
app = fastapi.FastAPI()

# Initialize DB
services.create_db()

@app.post("/users/", response_model=User)
def create_user(user:UserCreated, db:orm.Session = Depends(services.get_db)):
    user_check = services.get_user_by_email(db, user.email)

    if user_check:
        raise HTTPException(
            status_code=400, detail="User with this infomation is already exist!"
        )
    
    return services.create_user(db, user)

@app.get("/users/", response_model=List[User])
def get_all_user(db:orm.Session = Depends(services.get_db)):
    data = services.get_all_user(db)
    return data

@app.get("/users/{user_id}/", response_model=User)
def get_single_user(user_id:int, db:orm.Session = Depends(services.get_db)):
    return services.get_single_user(db, user_id)

@app.post("/{user_id}/posts/", response_model=Post)
def create_post(user_id: int, post:PostCreate, db:orm.Session = Depends(services.get_db)):
    user_check = services.get_single_user(db, user_id)
    if not user_check:
        raise HTTPException(
            status_code=400, detail=f"User with id {user_id} is not exsit!"
        )
    
    return services.create_post(db, user_id, post)

@app.get("/{user_id}/posts/", response_model=List[Post])
def get_all_post(user_id: int, db: orm.Session = Depends(services.get_db)):
    user_check = services.get_single_user(db, user_id)

    if not user_check:
        raise HTTPException(
            status_code=400, detail=f"User with id = {user_id} is not exsit!"
        )

    return services.get_all_posts(db, user_id)

@app.get("/{user_id}/posts/{post_id}", response_model=Post)
def get_post_single(user_id: int, post_id: int, db: Session = Depends(services.get_db)):
    user_check = services.get_single_user(db, user_id)

    if not user_check:
        raise HTTPException(
            status_code=400, detail=f"User with id = {user_id} is not exsit!"
        )

    record = services.get_post_single(db, user_id, post_id)

    if not record:
        raise HTTPException(
            status_code=400, detail=f"Post with id = {post_id} is not exsit!"
        )
    
    return record
