# We will run this file by uvicorn
import services
from typing import List

from fastapi import Depends, HTTPException, APIRouter

from sqlalchemy import orm
from schemas import(
    Post,
    PostCreate
)
from users import users_services
from . import posts_services

# Initialize app
router = APIRouter(
    prefix="/posts",
    tags=["posts api"],
    # dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "User not found"}}
)


@router.post("/{user_email}/posts/", response_model=Post)
def create_post(user_email: str, post:PostCreate, db:orm.Session = Depends(services.get_db)):
    user_check = users_services.get_single_user(db, user_email)
    if not user_check:
        raise HTTPException(
            status_code=400, detail=f"User with email {user_email} is not exsit!"
        )
    
    return posts_services.create_post(db, user_email, post)


@router.get("/{user_email}/posts/", response_model=List[Post])
def get_all_post(user_email: str, db: orm.Session = Depends(services.get_db)):
    user_check = users_services.get_single_user(db, user_email)

    if not user_check:
        raise HTTPException(
            status_code=400, detail=f"User with id = {user_email} is not exsit!"
        )

    return posts_services.get_all_posts(db, user_email)


@router.get("/{user_email}/posts/{post_id}", response_model=Post)
def get_post_single(user_email: str, post_id: int, db: orm.Session = Depends(services.get_db)):
    user_check = users_services.get_single_user(db, user_email)

    if not user_check:
        raise HTTPException(
            status_code=400, detail=f"User with id = {user_email} is not exsit!"
        )

    record = posts_services.get_post_single(db, user_email, post_id)

    if not record:
        raise HTTPException(
            status_code=400, detail=f"Post with id = {post_id} is not exsit!"
        )
    
    return record
