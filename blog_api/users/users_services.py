import json
import redis, string, random
from datetime import timedelta
from sqlalchemy.sql.expression import select, update
from sqlalchemy.orm import Session
from sqlalchemy import update
from passlib.context import CryptContext
from fastapi import BackgroundTasks

from blog_api.models import User
from blog_api.schemas import UserCreated
from blog_api.users.send_email_services import send_email_background


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# config redis client, in order to interact with redis
redis_client = redis.Redis(host="localhost", port=6379, db=0)

def _random_string():
    letters = string.digits
    return (''.join(random.choice(letters) for i in range(10)))

def create_user(db:Session, user:UserCreated, background_task: BackgroundTasks):
    db_user = User(email=user.email, hashed_password=hash_password(user.password))
    # register the transactions we want it to do, but it doesn’t actually do it
    db.add(db_user)
    # commits (persists) those changes to the database. session.commit() always calls for session.flush() as part of it
    db.commit()
    db.refresh(db_user)

    random_str = _random_string()
    redis_client.set(user.email, random_str)
    redis_client.expire(user.email, timedelta(minutes=5))

    send_email_background(background_task, "Verifycation Account Email!", user.email, {'title': "Verifycation Account Email!", 'code': f'{random_str}'})

    return db_user

def get_all_user(db:Session):
    stmt = select(User)
    return db.execute(stmt).scalars().all()

def get_single_user(db:Session, email:str):
    # this only create a query string
    stmt = select(User).filter(User.email == email)
    # execute query and return the record
    return db.execute(stmt).scalar()

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(user_email: str, password: str, db: Session):
    user = get_single_user(db, user_email)
    
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if user.is_active == False:
        return False
    
    return user

def active_user(user_email: str, verify_code: int, db: Session):
    user_code = json.loads(redis_client.get(user_email))

    if user_code == verify_code:
        stmt = (
            update(User).
            where(User.email == user_email).
            values(is_active=True)
        )
        db.execute(stmt)
        db.commit()
        return True
    else:
        return False