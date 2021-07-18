from sqlalchemy.sql.expression import select
from sqlalchemy.orm import Session

from models import Post
from schemas import PostCreate


def create_post(db: Session, user_email: str, post: PostCreate):
    db_post = Post(**post.dict(), owner_email=user_email)
    # add that instance object to your database session.
    db.add(db_post)
    # commit the changes to the database (so that they are saved).
    db.commit()
    # refresh your instance (so that it contains any new data from the database, like the generated ID).
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
