from http import HTTPStatus

import pytest

from app.common.exceptions import ApeksApiException
from app.common.func import api_get_db_table, check_api_db_response
from config import ApeksConfig as Apeks


class MockResponseGET:
    def __init__(self, url, params=None, http_status=HTTPStatus.OK, **kwargs):
        assert url.startswith(Apeks.URL), (
            "Проверьте, что вы делаете запрос на правильный "
            "ресурс API для запроса к API Апекс-ВУЗ."
        )
        assert params is not None, (
            "Проверьте, что передали параметры `params` для запроса "
            "статуса домашней работы"
        )
        assert "table_name" in params, (
            "Проверьте, что в параметрах `params` для запроса " "передали `table_name`"
        )
        self.status_code = http_status

    # def json(self):
    #     data = {
    #         "homeworks": [],
    #         "current_date": self.random_timestamp
    #     }
    #     return data


class TestApiGetApeksDb:
    """Тесты для функции 'apeks_api_db_get'."""

    func_name = "apeks_api_db_get"

    def test_get_returns_json(self, mock_response):
        result = api_get_db_table("some_table")
        print(result)
        assert result["status"] == 1

    # def test_get_500_api_answer(self, monkeypatch, api_response_json):
    #     def mock_500_response_get(*args, **kwargs):
    #         response = MockResponseGET(
    #             *args, http_status=HTTPStatus.INTERNAL_SERVER_ERROR, **kwargs
    #         )
    #
    #         response.json = api_response_json
    #         return response
    #
    #     monkeypatch.setattr(requests, 'get', mock_500_response_get)
    #
    #     try:
    #         print(apeks_api_db_get('some_table'))
    #     except:
    #         pass
    #     else:
    #         assert False, (
    #             f'Убедитесь, что в функции `{self.func_name}` обрабатываете ситуацию, '
    #             'когда API возвращает код, отличный от 200'
    #         )


class TestCheckApiResponse:
    """Тесты для функции 'check_api_db_response'."""

    func_name = "check_api_db_response"

    def test_check_api_good_response(self, api_response_json):
        result = check_api_db_response(api_response_json)
        assert result == api_response_json.get(
            "data"
        ), f'Функция {self.func_name} вернула неверный ответ "data"'
        assert isinstance(
            result, list
        ), f"Функция {self.func_name} должна возвращать список"

        print(api_response_json)

    def test_check_response_wrong_type(self, api_response_json):
        response = [api_response_json]

        with pytest.raises(TypeError) as exc_info:
            check_api_db_response(response)

        assert exc_info.type == TypeError, (
            f"Проверьте что функция {self.func_name} "
            'возвращает ошибку при неверном типе данных "response"'
        )

    def test_check_no_status_answer(self, api_response_json):
        response = api_response_json
        del response["status"]

        try:
            result = check_api_db_response(response)
        except ApeksApiException:
            pass
        else:
            assert result, (
                f"Проверьте что функция {self.func_name} "
                'возвращает ошибку при отсутствии "status" в ответе'
            )

    def test_check_zero_status_answer(self, api_response_json):
        response = api_response_json
        response["status"] = 0
        try:
            result = check_api_db_response(response)
        except ApeksApiException:
            pass
        else:
            assert result, (
                f"Проверьте что функция {self.func_name} "
                'возвращает ошибку при ответе "status: 0"'
            )

    def test_check_data_not_in_answer(self, api_response_json):
        response = api_response_json
        del response["data"]

        try:
            result = check_api_db_response(response)
        except KeyError:
            pass
        else:
            assert result, (
                f"Проверьте что функция {self.func_name} "
                'возвращает ошибку при отсутствии "data" в ответе'
            )

    def test_check_data_is_list(self, api_response_json):
        response = api_response_json
        response["data"] = {"some": "dict"}
        try:
            result = check_api_db_response(response)
        except TypeError:
            pass
        else:
            assert not result, (
                f"Проверьте что функция {self.func_name} "
                'возвращает ошибку при неверном типе данных "data"'
            )
