from __future__ import annotations

import logging
from json import JSONDecodeError

import requests

from app.common.exceptions import ApeksApiException
from config import ApeksConfig as Apeks


def apeks_api_db_get(table_name: str, **kwargs) -> dict:
    """
    Запрос к API для получения информации из таблицы базы данных Апекс-ВУЗ
    (имя_таблицы, **фильтр=значение(опционально).
    """
    endpoint = f"{Apeks.URL}/api/call/system-database/get"
    params = {"token": Apeks.TOKEN, "table": table_name}
    if kwargs:
        for db_filter, db_value in kwargs.items():
            params[f"filter[{db_filter}]"] = str(db_value)
    try:
        response = requests.get(endpoint, params=params)
    except ConnectionError as error:
        message = f'Ошибка при запросе к API Апекс-ВУЗ: "{error}"'
        logging.error(message)
        raise ConnectionError(message)
    else:
        try:
            resp_json = response.json()
            logging.debug(f"Запрос успешно выполнен: table_name:{table_name}, {kwargs}")
            return resp_json
        except JSONDecodeError as error:
            logging.error(
                f"Ошибка конвертации ответа " f'API Апекс-ВУЗ в JSON: "{error}"'
            )


def check_api_db_response(response: dict) -> list:
    """Проверка ответа запроса к БД Апекс-ВУЗ через API."""
    if not isinstance(response, dict):
        message = "Ответ API содержит некорректный тип данных (dict expected)"
        logging.error(message)
        raise TypeError(message)
    if "status" in response:
        if response.get("status") == 0:
            message = f'Неверный статус ответа API: "{response}"'
            logging.error(message)
            raise ApeksApiException(message)
        else:
            if "data" not in response:
                message = 'В ответе API отсутствует ключ "data"'
                logging.error(message)
                raise KeyError(message)
            data = response.get("data")
            if not isinstance(response, list):
                message = "Ответ API содержит некорректный тип данных (list expected)"
                logging.error(message)
                raise TypeError(message)
            logging.debug(
                f"Проверка выполнена успешно. Возвращен список по ключу: {data}"
            )
            return response
    else:
        message = f"Отсутствует статус ответа API"
        logging.error(message)
        raise ApeksApiException(message)


def get_disc_list() -> list:
    """Получаем полный список дисциплин из справочника Апекс-ВУЗ"""
    response = apeks_api_db_get("plan_disciplines", level=3)
    return check_api_db_response(response)
