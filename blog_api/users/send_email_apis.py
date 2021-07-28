from fastapi import APIRouter, BackgroundTasks
from blog_api.users.send_email_services import send_email_async, send_email_background
from fastapi import Response, status

# Initialize app
router = APIRouter(
    prefix="/send-email",
    tags=["send-email api"],
    # dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "User not found"}},
)

@router.get('/send-email/asynchronous/{user_email}')
async def send_email_asynchronous_api(user_email: str):
    # Althought it's async function, but it take time loading when sending email
    await send_email_async('Hello World!', user_email, {'title': 'Coolest title ever', 'name': 'Long Huynh Le'})
    # application will consume a few second to finish send_email_async before return 'Success' response to client
    # that is because, application only waiting for send_email_async then goes to process another request
    # not waiting for send_email_async then return 'Success' response
    return f"Sucessfully send email to {user_email}, please go to your inbox and check!"

@router.get('/send-email/background/{user_email}')
def send_email_background_api(user_email: str,background_tasks: BackgroundTasks):
    # difference with async function, background task and let send_email_background run and return 'Success' response immediately
    send_email_background(background_tasks, 'Hello background task', user_email, {'title': 'Coolest title ever from background task', 'name': 'Long Huynh Le'})
    return f"Sucessfully send email to {user_email}, please go to your inbox and check!"
