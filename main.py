# We will run this file by uvicorn

from datetime import timedelta
import fastapi
import services
from typing import List
from uuid import uuid4

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status

from sqlalchemy import orm
from sqlalchemy.orm.session import Session
from schemas import(
    User,
    UserCreated,
    Post,
    PostCreate
)
from helper import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, oauth2_scheme, get_current_user, CREDENTIAL_EXCEPTION
from models import User as User_db

# Initialize app
app = fastapi.FastAPI()

# Initialize DB
services.create_db()


@app.post("/users/", response_model=User)
def create_user(
    user:UserCreated, db:orm.Session = Depends(services.get_db)
):
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


@app.get("/users/{user_email}/", response_model=User)
def get_single_user(user_email:str, db:orm.Session = Depends(services.get_db), token: str = Depends(oauth2_scheme)):
    return services.get_single_user(db, user_email)


@app.post("/{user_email}/posts/", response_model=Post)
def create_post(user_email: str, post:PostCreate, db:orm.Session = Depends(services.get_db)):
    user_check = services.get_single_user(db, user_email)
    if not user_check:
        raise HTTPException(
            status_code=400, detail=f"User with email {user_email} is not exsit!"
        )
    
    return services.create_post(db, user_email, post)


@app.get("/{user_email}/posts/", response_model=List[Post])
def get_all_post(user_email: str, db: orm.Session = Depends(services.get_db)):
    user_check = services.get_single_user(db, user_email)

    if not user_check:
        raise HTTPException(
            status_code=400, detail=f"User with id = {user_email} is not exsit!"
        )

    return services.get_all_posts(db, user_email)


@app.get("/{user_email}/posts/{post_id}", response_model=Post)
def get_post_single(user_email: str, post_id: int, db: Session = Depends(services.get_db)):
    user_check = services.get_single_user(db, user_email)

    if not user_check:
        raise HTTPException(
            status_code=400, detail=f"User with id = {user_email} is not exsit!"
        )

    record = services.get_post_single(db, user_email, post_id)

    if not record:
        raise HTTPException(
            status_code=400, detail=f"Post with id = {post_id} is not exsit!"
        )
    
    return record

@app.get("/users/me")
async def read_user_me(current_user: User_db = Depends(get_current_user)):
    return current_user


# we are using OAuth2PasswordBearer, token form is {"access_token": access_token, "token_type": "bearer"}
# access token is contain expire time
# We only need to create an access token with correct format, jwt tool will handle the rest for us
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(services.get_db)):
    user = services.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise CREDENTIAL_EXCEPTION

    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        # The important thing to have in mind is that the sub key should have a unique identifier across the entire application, and it should be a string.
        {"sub": user.email},
        access_token_expire
    )

    return {"access_token": access_token, "token_type": "bearer"}
