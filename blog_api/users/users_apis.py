# We will run this file by uvicorn
from blog_api import services
from typing import List
from datetime import timedelta

from fastapi import Depends, HTTPException, APIRouter, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import orm

from blog_api.schemas import(
    User,
    UserCreated,
)
from blog_api.helper import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user, CREDENTIAL_EXCEPTION
from blog_api.models import User as User_db
from blog_api.users import users_services

# Initialize app
router = APIRouter(
    prefix="/users",
    tags=["users api"],
    # dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "User not found"}}
)


@router.post("/", response_model=User)
def create_user(
    background_task: BackgroundTasks,
    user:UserCreated,
    db:orm.Session = Depends(services.get_db)
):
    user_check = users_services.get_single_user(db, user.email)

    if user_check:
        raise HTTPException(
            status_code=400, detail="User with this infomation is already exist!"
        )
    
    return users_services.create_user(db, user, background_task)


@router.get("/", response_model=List[User])
def get_all_user(db:orm.Session = Depends(services.get_db)):
    data = users_services.get_all_user(db)
    return data


@router.get("/{user_email}/", response_model=User)
def get_single_user(user_email:str, db:orm.Session = Depends(services.get_db)):
    return users_services.get_single_user(db, user_email)


@router.get("/me")
async def read_user_me(current_user: User_db = Depends(get_current_user)):
    return current_user


# we are using OAuth2PasswordBearer, token form is {"access_token": access_token, "token_type": "bearer"}
# access token is contain expire time
# We only need to create an access token with correct format, jwt tool will handle the rest for us
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: orm.Session = Depends(services.get_db)):
    user = users_services.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise CREDENTIAL_EXCEPTION

    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        # The important thing to have in mind is that the sub key should have a unique identifier across the entire application, and it should be a string.
        {"sub": user.email},
        access_token_expire
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("{user_email}/active/{verify_code}")
def active_user(user_email: str, verify_code: int, db: orm.Session = Depends(services.get_db)):
    user_check = users_services.get_single_user(db, user_email)
    if not user_check:
        raise HTTPException(
            status_code=400, detail="User with this infomation does not exist!"
        )
    
    active_check = users_services.active_user(user_email, verify_code, db)

    if active_check == True:
        return f"User with email= {user_email} is activated!"
    else:
        raise HTTPException(
            status_code=400, detail="Verify code is incorrect!"
        )