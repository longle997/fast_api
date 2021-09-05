# We will run this file by uvicorn
import fastapi
from fastapi import Request
from fastapi.param_functions import Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from blog_api.models import User
from blog_api.users import users_apis, send_email_apis
from blog_api.posts import posts_apis
from blog_api.helper import get_current_user, templates, oauth2_scheme
# from blog_api.posts import posts_apis
# from blog_api.users import users_apis, send_email_apis

# Initialize app
app = fastapi.FastAPI(
    title="Long Le FastAPI project",
    version="0.0.1"
)

app.mount("/static", StaticFiles(directory="blog_api/static"), name="static")

# Initialize DB
# asyncio.run(create_db())

# include routers
app.include_router(
    users_apis.router,
    prefix=users_apis.PREFIX,
    tags=users_apis.TAGS
)
app.include_router(
    posts_apis.router,
    prefix=posts_apis.PREFIX,
    tags=posts_apis.TAGS
)
app.include_router(
    send_email_apis.router,
    prefix=send_email_apis.PREFIX,
    tags=send_email_apis.TAGS
)

# HOME page
@app.get("/home", response_class=HTMLResponse)
async def test_template(request: Request, current_user: User = Depends(get_current_user)):
    signed_in = False

    if current_user:
        signed_in = True
        return templates.TemplateResponse("home.html", {"request": request, "signedin": signed_in, "name": current_user.email, "type":"Customer"})
    else:
        return templates.TemplateResponse("home.html", {"request": request, "signedin": signed_in})

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