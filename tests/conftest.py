from unittest.mock import AsyncMock

from httpx import AsyncClient
from app import create_app

import pytest


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


# class MockResponse:
#     @staticmethod
#     def json():
#         return {
#             "status": 1,
#             "data": [
#                 {"id": "1", "name": "first name", "level": "1"},
#                 {"id": "2", "name": "second name", "level": "2"},
#             ],
#         }
#
#
# @pytest.fixture
# async def async_app_client():
#     async with AsyncClient(app=app, base_url='http://test') as client:
#         yield client
#
# # @pytest.fixture(autouse=True)
# # def disable_network_calls(monkeypatch):
# #     def stunted_get():
# #         raise RuntimeError("Network access not allowed during testing!")
# #     monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())
#
#
# @pytest.fixture(autouse=True)
# def no_requests(monkeypatch):
#     """Remove requests.sessions.Session.request for all tests."""
#     monkeypatch.delattr("requests.sessions.Session.request")
#
#
# @pytest.fixture
# def mock_response(monkeypatch):
#     """Requests.get() mocked to return MockResponse.json()."""
#
#     def mock_get(*args, **kwargs):
#         return MockResponse()
#
#     monkeypatch.setattr(requests, "get", mock_get)
#
#
# @pytest.fixture
# def api_response_json():
#     return MockResponse.json()
