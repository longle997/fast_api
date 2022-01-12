from datetime import datetime
import operator
from typing import Optional
from enum import Enum
from sqlalchemy.engine import create
from sqlalchemy.sql.expression import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, cast, and_
from sqlalchemy.types import String

from blog_api.models import Post, Link_User_Post, Comments, Base
from blog_api.schemas import PostCreate

DEFAULT_PAGING_SIZE = 100
DEFAULT_PAGING_PAGE_NUMBER = 1

class OperatorEnum(str, Enum):
    AND = "and"
    OR = "or"


async def __validate_like(user_id: int, post_id: int, db: AsyncSession):
    stmt = (
        select(Link_User_Post)
        .where(Link_User_Post.user_id == user_id)
        .where(Link_User_Post.post_id == post_id)
    )
    q = await db.execute(stmt)
    # with scalar() you return result of None
    return q.scalar()


async def searcher(
    base_query: select,
    model: Base,
    search_field: str = None,
    search_value: str = None,
    operation: OperatorEnum = OperatorEnum.OR
):
    filters = []
    filter_list = []

    if search_field is None and search_value is None:
        return base_query

    # https://www.kite.com/python/docs/sqlalchemy.cast
    # attr = CAST(posts.title AS VARCHAR)
    # we wanna take (posts.title AS VARCHAR) part
    attr = cast(getattr(model, search_field), String)

    # split from 1 long string into smaller string
    # example search value = "ahihi1 + ahihi2" => ["ahihi1", "ahihi2"]
    search_value_split = search_value.split("+")
    for item in search_value_split:
        filter_list.append(item.strip())

    for item in filter_list:
        # because attr now equal to "model.search_field", for example "Post.title"
        # so we can use ilike method, which will make our sql statement search for approximate value
        # in this case "model.search_field" will search with approximate value "item"
        # example lower(CAST(posts.title AS VARCHAR)) LIKE lower(:param_1)
        # https://www.kite.com/python/docs/sqlalchemy.sql.operators.ColumnOperators.ilike
        filters.append(attr.ilike(f"%{item}%"))


    if operation == OperatorEnum.OR:
        # add or between sql expression
        filter_expression = or_(*filters)
    else:
        filter_expression = and_(*filters)
    

    base_query = base_query.filter(filter_expression)

    return base_query


async def create_post(db: AsyncSession, user_email: str, post: PostCreate):
    db_post = Post(**post.dict(), owner_email=user_email)
    # add that instance object to your database session.
    db.add(db_post)
    # commit the changes to the database (so that they are saved).
    await db.commit()
    # refresh your instance (so that it contains any new data from the database, like the generated ID).
    await db.refresh(db_post)
    return db_post


async def get_all_posts_from_one_user(db: AsyncSession, user_email: str):
    # old style of SQLAchemy(<1.4)
    # return db.query(Post).filter(Post.owner_email == user_email).all()

    # new style of SQLAchemy(>=1.4)
    stmt = select(Post).filter(Post.owner_email == user_email)
    records = await db.execute(stmt)
    records = records.scalars().all()
    return records


async def get_all_posts(
    db: AsyncSession, 
    size: int = DEFAULT_PAGING_SIZE,
    page: int = DEFAULT_PAGING_PAGE_NUMBER,
    search_field: str = None,
    search_value: str = None,
    operation: OperatorEnum = OperatorEnum.OR
):
    # old style of SQLAchemy(<1.4)
    # return db.query(Post).filter(Post.owner_email == user_email).all()
    # new style of SQLAchemy(>=1.4)
    stmt = select(Post)

    stmt = await searcher(
        stmt,
        Post,
        search_field,
        search_value,
        operation
    )

    # processing pagination for get all post api
    if size:
        stmt = stmt.limit(size)
    if page:
        stmt = stmt.offset(size * (page - 1))

    records = await db.execute(stmt)
    records = records.scalars().all()
    if not records:
        return None
    # Only work around Todo investigate about lazy in model with self reference
    for record in records:
        comments_record = await get_all_comment(record.id, db)
        record.comments = comments_record

    '''
    OlD WAY TO processing pagination for get all post api
    if len(records) < size and page > 1:
        raise ValueError("Number of page is out of range, please choose lower number!")
    else:
        paging_records = []
        # split original list into multiple "smaller list", size of "smaller list" is equal to size agrument
        for i in range(0, len(records), size):
            paging_records.append(records[i : i+size])

        if page > len(paging_records):
            raise ValueError("Number of page is out of range, please choose lower number!")

        # choose which "smaller list" to return
        paging_records = paging_records[page-1]

    return paging_records
    '''

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