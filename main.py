# We will run this file by uvicorn
import fastapi
import services
import time
from starlette.requests import Request

from users import users_apis, send_email_apis
from posts import posts_apis

# Initialize app
app = fastapi.FastAPI()

# Initialize DB
services.create_db()

# include routers
app.include_router(users_apis.router)
app.include_router(posts_apis.router)
app.include_router(send_email_apis.router)


# @app.post("/users/", response_model=User)
# def create_user(
#     user:UserCreated, db:orm.Session = Depends(services.get_db)
# ):
#     user_check = services.get_user_by_email(db, user.email)

#     if user_check:
#         raise HTTPException(
#             status_code=400, detail="User with this infomation is already exist!"
#         )
    
#     return services.create_user(db, user)


# @app.get("/users/", response_model=List[User])
# def get_all_user(db:orm.Session = Depends(services.get_db)):
#     data = services.get_all_user(db)
#     return data


# @app.get("/users/{user_email}/", response_model=User)
# def get_single_user(user_email:str, db:orm.Session = Depends(services.get_db), token: str = Depends(oauth2_scheme)):
#     return services.get_single_user(db, user_email)


# @app.post("/{user_email}/posts/", response_model=Post)
# def create_post(user_email: str, post:PostCreate, db:orm.Session = Depends(services.get_db)):
#     user_check = services.get_single_user(db, user_email)
#     if not user_check:
#         raise HTTPException(
#             status_code=400, detail=f"User with email {user_email} is not exsit!"
#         )
    
#     return services.create_post(db, user_email, post)


# @app.get("/{user_email}/posts/", response_model=List[Post])
# def get_all_post(user_email: str, db: orm.Session = Depends(services.get_db)):
#     user_check = services.get_single_user(db, user_email)

#     if not user_check:
#         raise HTTPException(
#             status_code=400, detail=f"User with id = {user_email} is not exsit!"
#         )

#     return services.get_all_posts(db, user_email)


# @app.get("/{user_email}/posts/{post_id}", response_model=Post)
# def get_post_single(user_email: str, post_id: int, db: orm.Session = Depends(services.get_db)):
#     user_check = services.get_single_user(db, user_email)

#     if not user_check:
#         raise HTTPException(
#             status_code=400, detail=f"User with id = {user_email} is not exsit!"
#         )

#     record = services.get_post_single(db, user_email, post_id)

#     if not record:
#         raise HTTPException(
#             status_code=400, detail=f"Post with id = {post_id} is not exsit!"
#         )
    
#     return record

# test add middleware to (app / all functions)
# this middleware will receive request before target_function
@app.middleware("http")
async def add_process_time_to_header(request: Request, target_function):
    start_time = time.time()
    # pass that request to target_function
    response = await target_function(request)
    # receive response and edit it
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    # return/send to client
    return response
