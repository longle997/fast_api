import databases

from sqlalchemy.sql.expression import select
from sqlalchemy.sql.roles import UsesInspection
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models import Post, User
from schemas import PostCreate, UserCreated


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_db():
    # To actually create the tables on our database, we will need the declarative Base we just created and the engine
    # This is when SQLAlchemy will actually do something in our database
    return databases.Base.metadata.create_all(bind=databases.engine)

def get_db():
    db = databases.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_by_email(db:Session, email:str):
    return db.query(User).filter(User.email == email).first()

def create_user(db:Session, user:UserCreated):
    db_user = User(email=user.email, hashed_password=hash_password(user.password))
    # register the transactions we want it to do, but it doesn’t actually do it
    db.add(db_user)
    # commits (persists) those changes to the database. session.commit() always calls for session.flush() as part of it
    db.commit()
    # db.refresh(db_user)
    return db_user

def get_all_user(db:Session):
    return db.query(User).all()

def get_single_user(db:Session, email:str):
    # this only create a query string
    stmt = db.query(User).filter(User.email == email)
    # execute query and return the first record
    user = stmt.first()
    # another way to do it
    # list = db.execute(list)
    # user = list.scalars().first()
    return user

def create_post(db: Session, user_email: str, post: PostCreate):
    db_post = Post(**post.dict(), owner_email=user_email)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_all_posts(db: Session, user_email: str):
    # old style of SQLAchemy(<1.4)
    # return db.query(Post).filter(Post.owner_email == user_email).all()

    # new style of SQLAchemy(>=1.4)
    stmt = select(Post).filter(Post.owner_email == user_email)
    records = (db.execute(stmt)).scalars().all()
    return records

def get_post_single(db: Session, user_email: str, post_id: int):
    stmt = select(Post).filter(Post.owner_email == user_email, Post.id == post_id)
    return (db.execute(stmt)).scalar()

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