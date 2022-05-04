from __future__ import annotations

import logging
from http import HTTPStatus
from json import JSONDecodeError
from pprint import pprint


import requests

from app.common.exceptions import ApeksApiException
from config import FlaskConfig, ApeksConfig as Apeks


def apeks_api_db_request(table_name: str, **kwargs) -> list:
    """
    Запрос к API для получения информации из таблицы базы данных Апекс-ВУЗ
    (имя_таблицы, **фильтр=значение(опционально).
    """
    params = {"token": Apeks.TOKEN, "table": table_name}
    if kwargs:
        for sql_filter, sql_value in kwargs.items():
            params[f"filter[{sql_filter}]"] = str(sql_value)
    try:
        response = requests.get(
            Apeks.URL + "/api/call/system-database/get", params=params
        )
    except ConnectionError as error:
        message = f'Ошибка при запросе к API Апекс-ВУЗ: "{error}"'
        logging.error(message)
        raise ConnectionError(message)
    else:
        try:
            resp_json = response.json()
        except JSONDecodeError as error:
            logging.error(f'Ошибка конвертации ответа '
                          f'API Апекс-ВУЗ в JSON: "{error}"')
        else:
            if not isinstance(resp_json, dict):
                message = "Ответ API содержит некорректный тип данных (dict expected)"
                logging.error(message)
                raise TypeError(message)
            if "status" in resp_json:
                if resp_json.get('status') == 0:
                    if resp_json.get('message'):
                        message = f'API вернул сообщение "{resp_json.get("message")}"'
                        logging.error(message)
                        raise ApeksApiException(message)
                else:
                    if "data" not in resp_json:
                        message = 'В ответе API отсутствует ключ "data"'
                        logging.error(message)
                        raise ApeksApiException(message)
                    data = resp_json.get("data")
                    if not isinstance(data, list):
                        message = "Ответ API содержит некорректный тип данных (list expected)"
                        logging.error(message)
                        raise TypeError(message)
                    logging.debug(
                        f"Запрос успешно выполнен: table_name:{table_name}, {kwargs}"
                    )
                    return data


def get_disc_list() -> list:
    """Получаем полный список дисциплин из справочника Апекс-ВУЗ"""
    return apeks_api_db_request("plan_disciplines", level=3, id=570)


# pprint(get_disc_list())
