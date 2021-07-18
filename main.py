# We will run this file by uvicorn
import fastapi
from . import services
import time
from starlette.requests import Request

from .users import users_apis, send_email_apis
from .posts import posts_apis

# Initialize app
app = fastapi.FastAPI(
    title="Long Le FastAPI project",
    version="0.0.1"
)

# Initialize DB
services.create_db()

# include routers
app.include_router(users_apis.router)
app.include_router(posts_apis.router)
app.include_router(send_email_apis.router)

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
