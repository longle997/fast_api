from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm

# specify where is your DB
# The example assumes Python 3.9 and SQLAlchemy 1.4. Other dependencies include FastAPI with uvicorn, asyncpg (PostgreSQL database client for Python's asyncio)
# SQLACHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:password@db/test"
# in case run without docker
SQLACHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost/test"

# Specifying echo=True upon the engine initialization will enable us to see generated SQL queries in the console
async_engine = create_async_engine(
    SQLACHEMY_DATABASE_URL,
    echo=True
)

# you will use sessions to talk to your tables and make queries, but is the engine that is actually implementing things on your db.
# We should disable the "expire on commit" behavior of sessions with expire_on_commit=False. This is because in async settings, we don't want SQLAlchemy to issue new SQL queries to the database when accessing already commited objects.
async_session_local = _orm.sessionmaker(
    bind= async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)
# SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

# To map which table in the db will be related to each class in our files, we will use a SQLAlchemy system called Declarative
Base = _declarative.declarative_base()