from sqlalchemy.sql.expression import select
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models import User
from schemas import UserCreated


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db:Session, user:UserCreated):
    db_user = User(email=user.email, hashed_password=hash_password(user.password))
    # register the transactions we want it to do, but it doesn’t actually do it
    db.add(db_user)
    # commits (persists) those changes to the database. session.commit() always calls for session.flush() as part of it
    db.commit()
    db.refresh(db_user)
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
    
    return user