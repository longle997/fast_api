import pytest
import sqlalchemy.orm as _orm

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import close_all_sessions
from sqlalchemy import create_engine
from typing import Generator

from blog_api.databases import SQLACHEMY_DATABASE_URL, Base
from blog_api.main import app
from . import helper

SYNC_DATABASE_URL = "postgresql://postgres:password@localhost/test"

@pytest.fixture
def engine():
    engine = create_engine(
        SYNC_DATABASE_URL,
        future=True,
    )

    yield engine

@pytest.fixture
async def async_engine():
    async_engine = create_async_engine(
        SQLACHEMY_DATABASE_URL,
        future=True,
    )

    yield async_engine

# this fixture is used for drop database then create a new one with no data
# in order to avoid insert duplicate data to database
@pytest.fixture
def reset_database(engine) -> None:
    close_all_sessions()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture
async def async_session(async_engine, reset_database):
    async_session_local = _orm.sessionmaker(
        bind= async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    async with async_session_local() as session:
        yield session

@pytest.fixture
async def user_db(async_session: AsyncSession):
    user_recs = await helper.populate_user(async_session)

    return user_recs


# todo investigate this
def create_session_override(
    session: AsyncSession,
):
    async def create_session_():
        session.__verify_override__ = True  # type: ignore
        yield session

    return create_session_


# todo investigate this
@pytest.fixture
def client(async_session: AsyncSession):
    from blog_api.services import get_db

    with TestClient(app, raise_server_exceptions=True) as client_:
        app.dependency_overrides[get_db] = create_session_override(async_session)
        yield client_