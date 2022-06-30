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

# @pytest.mark.asyncio
# async def test_something_async(httpx_mock: HTTPXMock):
#     httpx_mock.add_response(json=[{"status": "1", "data": [{'id': '1', 'name': 'test'}])
#
#     async with httpx.AsyncClient() as client:
#         response = await client.get("https://test_url")
#         assert response.json() == [{"key1": "value1", "key2": "value2"}]
from common.func.api_get import api_get_staff_lessons


@pytest.mark.asyncio
async def test_something_async(httpx_mock: HTTPXMock):
    httpx_mock.add_response(json={'status': 1,
                                  'data': {
                                   'lessons': [{'id': 62524,
                                     'schedule_id': 198,
                                     'discipline_id': 44,
                                     'class_type_id': None,
                                     'control_type_id': 2,
                                     'date': '04.07.2022',
                                     'lesson_time_id': 5,
                                     'topic_code': '',
                                     'topic_name': '',
                                     'classroom_id': 45,
                                     'group_id': 16,
                                     'subgroup_id': None,
                                     'flow': None,
                                     'is_empty': 0,
                                     'self_work': 0,
                                     'skip_classroom_check': 0,
                                     'fixed': 1,
                                     'journal_lesson_id': 46545,
                                     'discipline': 'Основы профессиональной деятельности',
                                     'classroom': 'Г/415',
                                     'remote': 0,
                                     'class_type_name': 'зач.',
                                     'staffIds': ['98', '58', '32'],
                                     'superflowGroupsIds': [],
                                     'superflowSubgroupsIds': [],
                                     'staffNames': ['п/п-к Кузнецова И.И.',
                                      'п/п-к Белевский Р.А.',
                                      'п-к Семенов Е.Ю.'],
                                     'lessonTime': '14:50 - 16:20',
                                     'groupName': '21о2г'}],
                                      }})

    response = await api_get_staff_lessons(staff_id=32, month=7, year=2022)
    assert response == {'status': 1,
                                  'data': {
                                   'lessons': [{'id': 62524,
                                     'schedule_id': 198,
                                     'discipline_id': 44,
                                     'class_type_id': None,
                                     'control_type_id': 2,
                                     'date': '04.07.2022',
                                     'lesson_time_id': 5,
                                     'topic_code': '',
                                     'topic_name': '',
                                     'classroom_id': 45,
                                     'group_id': 16,
                                     'subgroup_id': None,
                                     'flow': None,
                                     'is_empty': 0,
                                     'self_work': 0,
                                     'skip_classroom_check': 0,
                                     'fixed': 1,
                                     'journal_lesson_id': 46545,
                                     'discipline': 'Основы профессиональной деятельности',
                                     'classroom': 'Г/415',
                                     'remote': 0,
                                     'class_type_name': 'зач.',
                                     'staffIds': ['98', '58', '32'],
                                     'superflowGroupsIds': [],
                                     'superflowSubgroupsIds': [],
                                     'staffNames': ['п/п-к Кузнецова И.И.',
                                      'п/п-к Белевский Р.А.',
                                      'п-к Семенов Е.Ю.'],
                                     'lessonTime': '14:50 - 16:20',
                                     'groupName': '21о2г'}],
                                      }}





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
