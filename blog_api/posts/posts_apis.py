# We will run this file by uvicorn
from typing import List, Optional

from fastapi import Depends, HTTPException, APIRouter, Security
from fastapi.security import HTTPBearer
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST

from blog_api.schemas import(
    PostCreate
)
from blog_api.models import User as User_db
from blog_api import services
from blog_api.users import users_services
from blog_api.posts import posts_services
from blog_api.helper import CREDENTIAL_EXCEPTION, get_current_user, test_scope
from blog_api.schemas import Post, Comments
from blog_api.exceptions import ItemDoesNotExsit

PREFIX = "/posts"
TAGS = ["posts api"]
# Initialize app
router = APIRouter()

async def __validate_post_by_id(db: AsyncSession, post_id: int):
    post_check = await posts_services.get_post_single(db, post_id)
    if not post_check:
        ItemDoesNotExsit(f"Post with ID {post_id} does not exsit!")

# Security is actually a subclass of Depends
# You can use Security to declare dependencies (just like Depends), but Security also receives a parameter scopes with a list of scopes (strings).
@router.post("")
async def create_post(
    post:PostCreate,
    current_user: User_db = Security(get_current_user, scopes=["admin", "user"]),
    db:AsyncSession = Depends(services.get_db)
):
    if not current_user:
        raise CREDENTIAL_EXCEPTION
    await users_services.verify_user(current_user.email, db)
    
    return await posts_services.create_post(db, current_user.email, post)


@router.get("", response_model=List[Post])
async def get_all_post(db: AsyncSession = Depends(services.get_db)):
    return await posts_services.get_all_posts(db)


@router.get("/{user_email}/posts/")
async def get_all_posts_from_one_user(user_email: str, db: AsyncSession = Depends(services.get_db)):
    await users_services.verify_user(user_email, db)

    return await posts_services.get_all_posts_from_one_user(db, user_email)


@router.get("/{post_id}", response_model=Post)
async def get_post_single(post_id: int, db: AsyncSession = Depends(services.get_db)):

    record = await posts_services.get_post_single(db, post_id)

    if not record:
        ItemDoesNotExsit(f"Post with id = {post_id} is not exsit!")

    return record


@router.patch("/{post_id}", response_model=Post)
async def update_post(
    post_id: int,
    post_data: PostCreate,
    current_user: User_db = Security(get_current_user, scopes=["admin", "user"]),
    db: AsyncSession = Depends(services.get_db)
):

    post_record: Post = await get_post_single(post_id, db)

    if post_record.owner_email != current_user.email:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="you are not allow to modify this post!"
        )
    
    record = await posts_services.update_post(post_id, post_data, db)
    
    return record


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User_db = Security(get_current_user, scopes=["admin", "user"]),
    db: AsyncSession = Depends(services.get_db)
):
    post_record: Post = await get_post_single(post_id, db)

    if post_record.owner_email != current_user.email:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="you are not allow to modify this post!"
        )

    status = await posts_services.delete_post(current_user.email, post_id, db)

    if status:
        return f"Delete Post with id {post_id} successfully!"
    else:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Can not delete this post!"
    )


@router.post("/{post_id}/like")
async def create_post_like(
    post_id: int,
    current_user: User_db = Security(get_current_user, scopes=["admin", "user"]),
    db: AsyncSession = Depends(services.get_db)
):
    if not current_user:
        raise CREDENTIAL_EXCEPTION
    
    # validate post by id
    await get_post_single(post_id, db)

    status = await posts_services.create_post_like(current_user.id, post_id, db)
    if status:
        return f"User with email {current_user.email} was like post with id {post_id}!"
    else:
        return f"User with email {current_user.email} was unlike post with id {post_id}!"


@router.post("/{post_id}/comment", status_code=201)
async def create_post_comment(
    post_id: int,
    body: str,
    parent_id: Optional[int] = None,
    current_user: User_db = Security(get_current_user, scopes=["admin", "user"]),
    db: AsyncSession = Depends(services.get_db)
):
    
        # validate post by id
    await get_post_single(post_id, db)

    if not current_user:
        raise CREDENTIAL_EXCEPTION

    try:
        status = await posts_services.create_post_comment(current_user.email, post_id, body, parent_id, db)
    except NoResultFound:
        ItemDoesNotExsit(f"Comment with ID {parent_id} was not found!")

    if status:
        return f"User with email {current_user.email} was comment post with id {post_id}!"
    else:
        raise HTTPException(
            status_code=400,
            detail="Unable to create comment for this post"
        )


@router.get("/{post_id}/comment")
async def get_all_comments(
    post_id: int,
    db: AsyncSession = Depends(services.get_db)
):
    record = await posts_services.get_all_comment(post_id, db)

    return record


@router.patch("/{post_id}/comment/{comment_id}", response_model=Comments)
async def update_comment(
    post_id: int,
    comment_id: int,
    comment_body: str,
    current_user: User_db = Security(get_current_user, scopes=["admin", "user"]),
    db: AsyncSession = Depends(services.get_db)
):
    if not current_user:
        raise CREDENTIAL_EXCEPTION

    # validate post by id
    await get_post_single(post_id, db)

    try:
        await posts_services.get_single_comment(comment_id, db)
    except NoResultFound:
        ItemDoesNotExsit(f"Comment with ID {comment_id} was not found!")

    if not comment_body:
        raise ValueError("No changes submitted.")

    record = await posts_services.update_comment(comment_id, comment_body, db)

    return record


@router.delete("/{post_id}/comment/{comment_id}", status_code=200)
async def delete_comment(
    post_id: int,
    comment_id: int,
    current_user: User_db = Security(get_current_user, scopes=["admin", "user"]),
    db: AsyncSession = Depends(services.get_db)
):
    if not current_user:
        raise CREDENTIAL_EXCEPTION

    # validate post by id
    await get_post_single(post_id, db)

    try:
        await posts_services.get_single_comment(comment_id, db)
    except NoResultFound:
        ItemDoesNotExsit(f"Comment with ID {comment_id} was not found!")

    status = await posts_services.delete_comment(comment_id, db)

    if status:
        return f"Successfully delete comment with ID = {comment_id}"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unable to delete comment with ID = {comment_id}"
        )

# @router.get("/{user_email}/posts/{post_id}/like")
# async def get_post_like(
#     user_email: str,
#     post_id: int,
#     db: AsyncSession = Depends(services.get_db)
# ):
#     record = await posts_services.get_post_like(post_id, db)

#     return record if record else 0