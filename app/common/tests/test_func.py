import pytest
import requests

from app.common.exceptions import ApeksApiException
from app.common.func import apeks_api_db_get, check_api_db_response


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
        del response['data']

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
        response['data'] = {'some': 'dict'}
        try:
            result = check_api_db_response(response)
        except TypeError:
            pass
        else:
            assert not result, (
                f"Проверьте что функция {self.func_name} "
                'возвращает ошибку при неверном типе данных "data"'
            )
