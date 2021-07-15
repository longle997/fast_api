from sqlalchemy.sql.expression import select
from sqlalchemy.sql.roles import UsesInspection
import databases
from sqlalchemy.orm import Session
from models import Post, User
from schemas import PostCreate, UserCreated

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
    fake_hashed_password = user.password + "hash_password"
    db_user = User(email=user.email, hashed_password= fake_hashed_password)
    # register the transactions we want it to do, but it doesn’t actually do it
    db.add(db_user)
    # commits (persists) those changes to the database. session.commit() always calls for session.flush() as part of it
    db.commit()
    # db.refresh(db_user)
    return db_user

def get_all_user(db:Session):
    return db.query(User).all()

def get_single_user(db:Session, id:int):
    # this only create a query string
    stmt = db.query(User).filter(User.id == id)
    # execute query and return the first record
    user = stmt.first()
    # another way to do it
    # list = db.execute(list)
    # user = list.scalars().first()
    return user

def create_post(db: Session, user_id: int, post: PostCreate):
    db_post = Post(**post.dict(), owner_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_all_posts(db: Session, user_id: int):
    # old style of SQLAchemy(<1.4)
    # return db.query(Post).filter(Post.owner_id == user_id).all()

    # new style of SQLAchemy(>=1.4)
    stmt = select(Post).filter(Post.owner_id == user_id)
    records = (db.execute(stmt)).scalars().all()
    return records

def get_post_single(db: Session, user_id: int, post_id: int):
    stmt = select(Post).filter(Post.owner_id == user_id, Post.id == post_id)
    return (db.execute(stmt)).scalar()