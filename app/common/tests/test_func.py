import requests

from app.common.func import apeks_api_db_request


# class MockResponseApiGet:
#     @staticmethod
#     def json():
#         return {"status": 1,
#                 "data": [
#                     {"id": "1",
#                      "name": "first name",
#                      "level": "1"},
#                     {"id": "2",
#                      "name": "second name",
#                      "level": "2"},
#                 ]}
#
#
# #{"status": 0, "message": "Нет доступа к указанной таблице."}


def test_apeks_api_db_request(api_good_json):
    # def mock_apeks_api_db_request(*args, **kwargs):
    #     return MockResponseApiGet()

    func_name = 'apeks_api_db_request'

    # monkeypatch.setattr(requests, "get", api_good_json)

    # try:
    #     apeks_api_db_request()
    # except TypeError:
    #     pass
    # else:
    #     assert False, (f'Убедитесь, что функция "{func_name}" возвращает ошибку '
    #                    'при отсутствии обязательного параметра "table_name"')

    result = apeks_api_db_request('test')
    assert result[0]["name"] == "first name"
