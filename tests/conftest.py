import asyncio
from typing import Callable, TypeVar

from flask import Response
from flask_login import FlaskLoginClient
import pytest
import pytest_asyncio
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine
from werkzeug.test import TestResponse

from app import create_app
from app.core.db.auth_models import Users

T = TypeVar("T")


async def call(f: Callable[[], T]) -> T:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor=None, func=f)


class AsyncTestClient(FlaskLoginClient):
    """A facade for the flask test client."""

    async def get(self, *args, **kwargs) -> TestResponse:
        parent = super()
        return await call(lambda: parent.get(*args, **kwargs))

    async def post(self, *args, **kwargs) -> TestResponse:
        parent = super()
        return await call(lambda: parent.post(*args, **kwargs))

    async def delete(self, *args, **kwargs) -> TestResponse:
        parent = super()
        return await call(lambda: parent.delete(*args, **kwargs))

    async def put(self, *args, **kwargs) -> TestResponse:
        parent = super()
        return await call(lambda: parent.put(*args, **kwargs))


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    yield app


@pytest.fixture()
def client(app) -> FlaskLoginClient:
    app.test_client_class = FlaskLoginClient
    return app.test_client()


@pytest.fixture()
def async_client(app) -> AsyncTestClient:
    return AsyncTestClient(app, Response, True)


class AuthActions():
    def __init__(self, client, username='TestUser', password='TestPass'):
        self.client = client
        self.username = username
        self.password = password

    def create(self):
        with self.client.application.app_context():
            permissions = Per
            test_user = Users(username=self.username, password=self.password)
            test_user.save()

    def login(self):
        return self.client.post(
            '/login',
            data={'username': self.username, 'password': self.password}
        )

    def logout(self):
        return self.client.get('/logout')

# Define client and other fixtures here ...


@pytest.fixture
def auth(async_client):
    return AuthActions(async_client)


@pytest.fixture(scope="function")
async def test_session() -> Session:
    async_engine = create_async_engine(
        "sqlite://",
        poolclass=StaticPool,
        future=True,
    )
    async_session = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        async with async_engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)

        yield session

    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)
