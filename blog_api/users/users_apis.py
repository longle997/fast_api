# We will run this file by uvicorn
from starlette.requests import Request
from blog_api import services
from typing import List
from datetime import timedelta

from fastapi import Depends, HTTPException, APIRouter, BackgroundTasks, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from blog_api.schemas import(
    User,
    UserCreated,
)
from blog_api.helper import ACCESS_TOKEN_EXPIRE_DAYS, create_access_token, get_current_user, CREDENTIAL_EXCEPTION, templates
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
async def create_user(
    background_task: BackgroundTasks,
    user:UserCreated,
    db:AsyncSession = Depends(services.get_db)
):
    user_check = await users_services.get_single_user(db, user.email)

    if user_check:
        raise HTTPException(
            status_code=400, detail="User with this infomation is already exist!"
        )
    
    return await users_services.create_user(db, user, background_task)


@router.get("/", response_model=List[User])
async def get_all_user(db:AsyncSession = Depends(services.get_db)):
    data = await users_services.get_all_user(db)
    return data


@router.get("/{user_email}/", response_model=User)
async def get_single_user(user_email:str, db:AsyncSession = Depends(services.get_db)):
    record = await users_services.get_single_user(db, user_email)

    return record


'''
@router.get("/me")
async def read_user_me(current_user: User_db = Depends(get_current_user)):
    if not current_user:
        raise CREDENTIAL_EXCEPTION
    return current_user
'''

# we are using OAuth2PasswordBearer, token form is {"access_token": access_token, "token_type": "bearer"}
# access token is contain expire time
# We only need to create an access token with correct format, jwt tool will handle the rest for us
@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(services.get_db),
):
    user = await users_services.authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise CREDENTIAL_EXCEPTION

    access_token_expire = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = await create_access_token(
        # The important thing to have in mind is that the sub key should have a unique identifier across the entire application, and it should be a string.
        {"sub": user.email},
        access_token_expire
    )

    return {"access_token": access_token, "token_type": "bearer"}

'''
# use this way to interact with Form data, which usually was from html file
@router.post("/login/form")
async def login_for_access_token(
    email: str = Form(...),
    password: str= Form(...),
    db: AsyncSession = Depends(services.get_db),
):
    user = await users_services.authenticate_user(email, password, db)
    if not user:
        raise CREDENTIAL_EXCEPTION

    access_token_expire = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = await create_access_token(
        # The important thing to have in mind is that the sub key should have a unique identifier across the entire application, and it should be a string.
        {"sub": user.email},
        access_token_expire
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/login/form", response_class=HTMLResponse)
async def login_for_access_token(
    request: Request
):
    return templates.TemplateResponse("login.html", {"request": request})
'''

@router.post("/{user_email}/active/{verify_code}")
async def active_user(user_email: str, verify_code: str, db: AsyncSession = Depends(services.get_db)):
    user_check = await users_services.get_single_user(db, user_email)
    if not user_check:
        raise HTTPException(
            status_code=400, detail="User with this infomation does not exist!"
        )
    
    active_check = await users_services.active_user(user_email, verify_code, db)

    if active_check == True:
        return f"User with email= {user_email} is activated!"
    else:
        raise HTTPException(
            status_code=400, detail="Verify code is incorrect!"
        )

@router.post("/changepass")
async def change_user_password(password: str, confirm_password: str, db: AsyncSession = Depends(services.get_db), current_user: User_db = Depends(get_current_user)):
    if not current_user:
        raise CREDENTIAL_EXCEPTION

    if password != confirm_password:
        raise HTTPException(
            status_code=400, detail=f"Confirm password is incorrect, please type it again!"
        )

    status = await users_services.change_user_password(password, db, current_user)

    if status:
        return f"User with email {current_user.email} changed password successfully!"
    else:
        raise HTTPException(
            status_code=400, detail=f"Unable to change password for user with email {current_user.email}!"
        )

@router.post("/{user_email}/forgotpass")
async def forgot_user_password(background_task: BackgroundTasks, user_email: str, db: AsyncSession = Depends(services.get_db)):
    user_check = await users_services.get_single_user(db, user_email)

    if not user_check:
        raise HTTPException(
            status_code=400, detail="User with this infomation does not exist!"
        )
    
    status = await users_services.forgot_password(user_email, db, background_task)

    if status:
        return f"New password was sent to email {user_email}, please use that new password to login. Remember to change your password after login."
    else:
        raise HTTPException(
            status_code=400, detail=f"Fail to send new password to email {user_email}"
        )
