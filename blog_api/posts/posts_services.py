from datetime import datetime
from typing import Optional
from sqlalchemy.engine import create
from sqlalchemy.sql.expression import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from blog_api.models import Post, Link_User_Post, Comments
from blog_api.schemas import PostCreate


async def __validate_like(user_id: int, post_id: int, db: AsyncSession):
    stmt = (
        select(Link_User_Post)
        .where(Link_User_Post.user_id == user_id)
        .where(Link_User_Post.post_id == post_id)
    )
    q = await db.execute(stmt)
    # with scalar() you return result of None
    return q.scalar()


async def create_post(db: AsyncSession, user_email: str, post: PostCreate):
    db_post = Post(**post.dict(), owner_email=user_email)
    # add that instance object to your database session.
    db.add(db_post)
    # commit the changes to the database (so that they are saved).
    await db.commit()
    # refresh your instance (so that it contains any new data from the database, like the generated ID).
    db.refresh(db_post)
    return db_post


async def get_all_posts_from_one_user(db: AsyncSession, user_email: str):
    # old style of SQLAchemy(<1.4)
    # return db.query(Post).filter(Post.owner_email == user_email).all()

    # new style of SQLAchemy(>=1.4)
    stmt = select(Post).filter(Post.owner_email == user_email)
    records = await db.execute(stmt)
    records = records.scalars().all()
    return records

async def get_all_posts(db: AsyncSession):
    # old style of SQLAchemy(<1.4)
    # return db.query(Post).filter(Post.owner_email == user_email).all()

    # new style of SQLAchemy(>=1.4)
    stmt = select(Post)
    records = await db.execute(stmt)
    records = records.scalars().all()
    if not records:
        return None
    # Only work around Todo investigate about lazy in model with self reference
    for record in records:
        comments_record = await get_all_comment(record.id, db)
        record.comments = comments_record

    return records


async def get_post_single(db: AsyncSession, post_id: int):
    stmt = select(Post).filter(Post.id == post_id)
    q = await db.execute(stmt)
    record: Post = q.scalar()

    if not record:
        return None

    # Only work around Todo investigate about lazy in model with self reference
    comments_record = await get_all_comment(post_id, db)
    record.comments = comments_record

    return record

async def update_post(post_id: int, post_data: PostCreate, db: AsyncSession):
    if not (patch_data := post_data.dict(exclude_unset=True)):
        raise ValueError("No changes submitted.")
    post_record: Post = await db.get(Post, post_id)

    if post_data.title:
        post_record.title = post_data.title
    
    if post_data.content:
        post_record.content = post_data.content

    post_record.date_last_update = datetime.now()

    await db.commit()

    return post_record

async def delete_post(post_id: int, db: AsyncSession):
    stmt = (
        delete(Post)
        .where(Post.id == post_id)
    )
    await db.execute(stmt)
    await db.commit()

    return True

async def create_post_like(user_id: int, post_id: int, db: AsyncSession):
    like_check = await __validate_like(user_id, post_id, db)
    if like_check:
        stmt = (
            delete(Link_User_Post)
            .where(Link_User_Post.user_id == user_id)
            .where(Link_User_Post.post_id == post_id)
        )
        await db.execute(stmt)
        await db.commit()
        return False

    like = Link_User_Post(user_id = user_id, post_id = post_id)
    db.add(like)
    await db.commit()

    return True

async def create_post_comment(user_email: str, post_id: int, body: str, parent_id: Optional[int], db: AsyncSession):
    new_comment = Comments(
        name = user_email,
        post = post_id,
        body = body,
        parent_id = parent_id
    )

    if parent_id:
        parent_comment: Comments = await get_single_comment(parent_id, db)
        parent_comment.children.append(new_comment)

        await db.commit()
        return True
    
    db.add(new_comment)
    await db.commit()
    # await db.refresh(new_comment)

    return new_comment

async def get_all_comment(post_id: int, db: AsyncSession):
    # Comments.parent_id == None because we just wanna get parent contain children, not parent and children at the same level
    stmt = select(Comments).filter(Comments.post == post_id, Comments.parent_id == None).options(selectinload(Comments.children))
    q = await db.execute(stmt)
    record = q.scalars().all()

    return record

async def get_single_comment(comment_id: int, db: AsyncSession):
    stmt = select(Comments).filter(Comments.id == comment_id)
    q = await db.execute(stmt)
    record = q.scalar_one()

    return record

async def update_comment(comment_id: int, commnent_body: str, db: AsyncSession):
    record: Comments = await db.get(Comments, comment_id)

    record.body = commnent_body

    await db.commit()

    return record

async def delete_comment(comment_id: int, db: AsyncSession):
    stmt = delete(Comments).filter(Comments.id == comment_id)

    await db.execute(stmt)
    await db.commit()

    return True


# async def get_post_like(post_id: int, db: AsyncSession):
#     stmt = (
#         select(Post)
#         .where(Post.id == post_id)
#     ).options(selectinload(Post.like))

#     q = await db.execute(stmt)
#     record: Post = q.scalar()

#     return record.like