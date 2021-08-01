from sqlalchemy.sql.expression import select
from sqlalchemy.ext.asyncio import AsyncSession

from blog_api.models import Post
from blog_api.schemas import PostCreate


async def create_post(db: AsyncSession, user_email: str, post: PostCreate):
    db_post = Post(**post.dict(), owner_email=user_email)
    # add that instance object to your database session.
    db.add(db_post)
    # commit the changes to the database (so that they are saved).
    await db.commit()
    # refresh your instance (so that it contains any new data from the database, like the generated ID).
    db.refresh(db_post)
    return db_post


async def get_all_posts(db: AsyncSession, user_email: str):
    # old style of SQLAchemy(<1.4)
    # return db.query(Post).filter(Post.owner_email == user_email).all()

    # new style of SQLAchemy(>=1.4)
    stmt = select(Post).filter(Post.owner_email == user_email)
    records = await db.execute(stmt)
    records = records.scalars().all()
    return records


async def get_post_single(db: AsyncSession, user_email: str, post_id: int):
    stmt = select(Post).filter(Post.owner_email == user_email, Post.id == post_id)
    q = await db.execute(stmt)
    record = q.scalar()
    return record
