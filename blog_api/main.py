# We will run this file by uvicorn
import fastapi
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from blog_api.services import create_db
from blog_api.users import users_apis, send_email_apis
from blog_api.posts import posts_apis
from blog_api.helper import templates

# Initialize app
app = fastapi.FastAPI(
    title="Long Le FastAPI project",
    version="0.0.1"
)

app.mount("/static", StaticFiles(directory="blog_api/static"), name="static")

# Initialize DB
# asyncio.run(create_db())

# include routers
app.include_router(users_apis.router)
app.include_router(posts_apis.router)
app.include_router(send_email_apis.router)

# HOME page
@app.get("/home", response_class=HTMLResponse)
async def test_template(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "signedin": True, "name": "Long Le", "type":"admin"})

'''
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
'''