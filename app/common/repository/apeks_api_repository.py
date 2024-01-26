import functools
import logging
from json import JSONDecodeError

import httpx

from ..common.exceptions import ApeksApiException
from .abstract_repository import AbstractApiRepository


class ApeksApiRepository(AbstractApiRepository):
    """Класс для запросов к API АпексВУЗ."""

    @staticmethod
    def request_handler(method):
        """Декоратор для проверки корректности запросов к API Апекс-ВУЗ"""

        @functools.wraps(method)
        async def wrapper(*args, **kwargs):
            self, *_ = args
            message = f"{self.__class__.__name__}.{method.__name__} - "
            try:
                response = await method(*args, **kwargs)
                response.raise_for_status()
                if "Forbidden (#403)" in response.text:
                    message += f"Ошибка авторизации API АпексВУЗ"
                    logging.error(message)
                    raise ApeksApiException(message)
                response = response.json()
                params = kwargs.get("params", {})
                if "token" in params:
                    del params["token"]
                if "status" not in response:
                    message += (
                        f"Отсутствует статус ответа API: '{response}'. "
                        f"Параметры: {params}"
                    )
                    logging.error(message)
                    raise ApeksApiException(message)
                elif response["status"] != 1:
                    message += (
                        f"Неверный статус ответа API: '{response}'. "
                        f"Параметры: {params}"
                    )
                    logging.error(message)
                    raise ApeksApiException(message)
                elif "data" not in response:
                    message = "В ответе API Апекс-ВУЗ отсутствуют данные ('data')"
                    logging.error(message)
                    raise ApeksApiException(message)
                return response.get("data")
            except httpx.HTTPError as error:
                message += (
                    f"Произошла ошибка при запросе к API Апекс-ВУЗ: "
                    f"{error.__class__.__name__} - '{error}'"
                )
                logging.error(message + f" {error.request.url!r}")
                raise ApeksApiException(message)
            except JSONDecodeError as error:
                message += f"Ошибка конвертации ответа API Апекс-ВУЗ в JSON: '{error}'"
                logging.error(message)
                raise ApeksApiException(message)

        return wrapper

    @request_handler
    async def get(self, endpoint: str, params: dict) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, params=params)
        return response

    @request_handler
    async def post(self, endpoint: str, params: dict, data: dict) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint, params=params, data=data)
        return response

    async def put(self, endpoint: str, params: dict, data: dict):
        raise ApeksApiException("API АпексВУЗ не поддерживает метод PUT")

    async def patch(self, endpoint: str, params: dict, data: dict):
        raise ApeksApiException("API АпексВУЗ не поддерживает метод PATCH")

    @request_handler
    async def delete(self, endpoint: str, params: dict) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            response = await client.delete(endpoint, params=params)
        return response

    @staticmethod
    def data_processor(table_data, dict_key: str = "id") -> dict:
        """
        Преобразует полученные данные из таблиц БД Апекс-ВУЗ.

        Parameters
        ----------
            table_data
                данные таблицы, содержащей список словарей в формате JSON
            dict_key: str
                название поля значения которого станут ключами словаря
                по умолчанию - 'id'

        Returns
        -------
            dict
                {id: {keys: values}}.
        """
        data = {}
        for d_val in table_data:
            key_val = d_val.get(dict_key)
            if key_val:
                data[int(key_val)] = d_val
        logging.debug(f"Обработаны данные. Ключ: {dict_key}")
        return data
