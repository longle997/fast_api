import os
import time
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
load_dotenv('.env')

# create a .env file to store sessitive data
# then load and read data from it, don't commit .env file
class Envs:
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME = os.getenv('MAIL_FROM_NAME')

# to be able to use this feature, you'll need to
# allow less secure apps on your gmail account
# turn off two-factor authentication enabled.
# or create application-specific passwords.
conf = ConnectionConfig(
    MAIL_USERNAME= Envs.MAIL_USERNAME,
    MAIL_PASSWORD= Envs.MAIL_PASSWORD,
    MAIL_FROM= Envs.MAIL_FROM,
    MAIL_PORT= Envs.MAIL_PORT,
    MAIL_SERVER= Envs.MAIL_SERVER,
    MAIL_FROM_NAME= Envs.MAIL_FROM_NAME,
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER='blog_api/templates'
)

async def send_email_async(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        # In the send email functions, since we are using Jinja templates, the argument should be template_body = body, otherwise it will give validation errors
        template_body=body,
        subtype='html'
    )

    fm = FastMail(conf)
    
    time.sleep(60)

    await fm.send_message(message, template_name='email.html')


def send_email_background(backgound_tasks: BackgroundTasks, subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=body,
        subtype='html'
    )

    fm = FastMail(conf)

    backgound_tasks.add_task(
        fm.send_message, message, template_name='email.html'
    )