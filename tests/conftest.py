import asyncio
from typing import TypeVar, Callable

import pytest
from flask import Response
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from app.app_factory import create_app


T = TypeVar("T")


async def call(f: Callable[[], T]) -> T:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor=None, func=f)


class AsyncTestClient(FlaskClient):
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
    return app


@pytest.fixture()
def client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def async_client(app) -> AsyncTestClient:
    return AsyncTestClient(app, Response, True)
