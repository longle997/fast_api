import sqlalchemy
import sqlalchemy.ext.declarative as _declarative
import sqlalchemy.orm as _orm

# specify where is your DB
SQLACHEMY_DATABASE_URL = "postgresql://postgres:password@localhost/test"

# you just telling where is your DB
# engine = sqlalchemy.create_engine(
#     SQLACHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
engine = sqlalchemy.create_engine(
    SQLACHEMY_DATABASE_URL
)

# you will use sessions to talk to your tables and make queries, but is the engine that is actually implementing things on your db.
SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)

# To map which table in the db will be related to each class in our files, we will use a SQLAlchemy system called Declarative
Base = _declarative.declarative_base()