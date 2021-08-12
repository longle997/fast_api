import json
from pydantic.errors import IntegerError
import redis, string, random
from datetime import timedelta

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi import BackgroundTasks, HTTPException
from pydantic.error_wrappers import ValidationError

from blog_api.models import User
from blog_api.schemas import UserCreated
from blog_api.users.send_email_services import send_email_background


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# config redis client, in order to interact with redis
redis_client = redis.Redis(host="redis", port=6379, db=0)

def _random_string():
    letters = string.digits
    letters += string.ascii_lowercase
    return (''.join(random.choice(letters) for _ in range(8)))

async def create_user(db:AsyncSession, user:UserCreated, background_task: BackgroundTasks):
    # workaround by adding posts field to User intance, because when response model validate this instance, it will require posts field
    db_user = User(email=user.email, hashed_password=hash_password(user.password), posts=[], posts_like=[])
    # register the transactions we want it to do, but it doesn’t actually do it
    db.add(db_user)
    # commits (persists) those changes to the database. session.commit() always calls for session.flush() as part of it
    await db.commit()
    random_str = _random_string()
    redis_client.set(user.email, random_str)
    redis_client.expire(user.email, timedelta(minutes=60))

    try:
        send_email_background(
            background_task, 
            "Verifycation Account Email!", 
            user.email, 
            {
                'title': "Verifycation Account Email!", 
                'code': f'{random_str}',
                'message': 'Verification code only valid for 5 minutes, so let\'s hurry up!',
                'password': None
            }
        )
    except ValidationError:
        raise HTTPException(
            status_code=400, detail=f"Email {user.email} is invalid, please use another one!"
        )

    return db_user

async def get_all_user(db:AsyncSession):
    # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html Preventing Implicit IO when Using AsyncSession
    # for relationship loading, eager loading should be applied.
    stmt = select(User).options(selectinload(User.posts), selectinload(User.posts_like))
    # stmt = select(User)
    # we await session.execute() that will execute the query and hold the results. The scalars() method provides access to the results.
    record = await db.execute(stmt)
    records = record.scalars().all()
    return records

async def get_single_user(db:AsyncSession, email:str):
    # this only create a query string
    stmt = select(User).filter(User.email == email).options(selectinload(User.posts_like), selectinload(User.posts))
    # stmt = select(User).filter(User.email == email)
    # execute query and return the record
    record = await db.execute(stmt)
    return record.scalar()

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user(user_email: str, password: str, db: AsyncSession):
    user = await get_single_user(db, user_email)
    
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if user.is_active == False:
        return False
    
    return user

async def active_user(user_email: str, verify_code: str, db: AsyncSession):
    user_code = redis_client.get(user_email).decode("utf-8")

    if user_code == verify_code:
        stmt = (
            update(User).
            where(User.email == user_email).
            values(is_active=True)
        )
        await db.execute(stmt)
        await db.commit()
        return True
    else:
        return False

async def change_user_password(password: str, db: AsyncSession, current_user: User):

    stmt = (
        update(User)
        .where(User.email == current_user.email)
        .values(hashed_password = hash_password(password))
    )

    try:
        await db.execute(stmt)
        await db.commit()
        return True
    except IntegerError:
        return False

async def forgot_password(user_email: str, db: AsyncSession, background_task: BackgroundTasks):
    random_password = _random_string()
    new_hashed_password = hash_password(random_password)

    try:
        send_email_background(
            background_task,
            "Forgot password email!",
            user_email,
            {
                'title': "Forgot password email!", 
                'password': f'{random_password}',
                'message': 'This email was sent after you submit forgot password, please use that new password to login. Remember to change your password after login.',
                'code': None
            }
        )
    except ValidationError:
        raise HTTPException(
            status_code=400, detail=f"Email {user_email} is invalid, please use another one!"
        )

    stmt = (
        update(User)
        .where(User.email == user_email)
        .values(hashed_password = new_hashed_password)
    )

    try:
        await db.execute(stmt)
        await db.commit()
        return True
    except IntegerError:
        return False

async def verify_user(user_email: str, db: AsyncSession):
    user_check = await get_single_user(db, user_email)

    if not user_check:
        raise HTTPException(
            status_code=400, detail=f"User with id = {user_email} is not exsit!"
        )
