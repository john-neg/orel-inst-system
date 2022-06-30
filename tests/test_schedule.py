import pytest
import httpx
from pytest_httpx import HTTPXMock

from app import create_app

# def test_request_example(client):
#     urls = ['/schedule']
#     for url in urls:
#         try:
#             response = client.get(url)
#         except Exception as e:
#             assert False, f'''Страница `{url}` работает неправильно. Ошибка: `{e}`'''
#         assert response.status_code != 404, f'Страница `{url}` не найдена, проверьте этот адрес в *urls.py*'
#         assert response.status_code == 200, (
#             f'Ошибка {response.status_code} при открытиии `{url}`. Проверьте ее view-функцию'
#         )

from app import create_app


@pytest.mark.asyncio
async def test_something_async(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json=[{"key1": "value1", "key2": "value2"}])

    async with httpx.AsyncClient() as client:
        response = await client.get("https://test_url")
        assert response.json() == [{"key1": "value1", "key2": "value2"}]


# def test_home_page(client):
#     """
#     GIVEN a Flask application configured for testing
#     WHEN the '/' page is requested (GET)
#     THEN check that the response is valid
#     """
#
#     # Create a test client using the Flask application configured for testing
#     response = client.get('/')
#     assert response.status_code == 200
#     assert b"Evgeny Semenov" in response.data
#     assert b"Flask User Management Example!" in response.data
#     # assert b"Need an account?" in response.data
#     # assert b"Existing user?" in response.data
