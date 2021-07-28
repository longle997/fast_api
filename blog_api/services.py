from blog_api import databases

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_db():
    # To actually create the tables on our database, we will need the declarative Base we just created and the engine
    # This is when SQLAlchemy will actually do something in our database
    return databases.Base.metadata.create_all(bind=databases.engine)

# We need to have an independent database session/connection (SessionLocal) per request, use the same session through all the request and then close it after the request is finished.
# And then a new session will be created for the next request.
def get_db():
    # Only the code prior to and including the yield statement is executed before sending a response:
    db = databases.SessionLocal()
    try:
        # The yield statement suspends function’s execution and sends a value back to the caller, but retains enough state to enable function to resume where it is left off. When resumed, the function continues execution immediately after the last yield run. This allows its code to produce a series of values over time, rather than computing them at once and sending them back like a list.
        yield db
    # The code following the yield statement is executed after the response has been delivered
    finally:
        db.close()
