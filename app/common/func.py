from __future__ import annotations

import logging
from json import JSONDecodeError

import requests

from app.common.exceptions import ApeksApiException
from config import ApeksConfig as Apeks


def api_get_request_handler(func):
    """Функция декоратор для GET запросов к API Апекс-ВУЗ"""

    def wrapper(*args, **kwargs) -> dict:
        endpoint, params = func(*args, **kwargs)
        try:
            response = requests.get(endpoint, params=params)
        except ConnectionError as error:
            message = f"{func.__name__}. Ошибка при запросе к API Апекс-ВУЗ: '{error}'"
            logging.error(message)
            raise ConnectionError(message)
        else:
            try:
                resp_json = response.json()
                del params["token"]
                logging.debug(f"{func.__name__}. Запрос успешно выполнен: {params}")
                return resp_json
            except JSONDecodeError as error:
                logging.error(
                    f"{func.__name__}. Ошибка конвертации "
                    f"ответа API Апекс-ВУЗ в JSON: '{error}'"
                )

    return wrapper


@api_get_request_handler
def api_get_db_table(table_name: str, **kwargs):
    """
    Запрос к API для получения информации из таблицы базы данных Апекс-ВУЗ
    (имя_таблицы, **фильтр=значение(опционально).
    """
    endpoint = f"{Apeks.URL}/api/call/system-database/get"
    params = {"token": Apeks.TOKEN, "table": table_name}
    if kwargs:
        for db_filter, db_value in kwargs.items():
            params[f"filter[{db_filter}]"] = str(db_value)
    return endpoint, params


@api_get_request_handler
def api_get_staff_lessons(
    staff_id: int | str,
    month: int | str,
    year: int | str,
):
    """
    Получаем список занятий по id преподавателя
    за определенный месяц и год.
    """
    endpoint = f"{Apeks.URL}/api/call/schedule-schedule/staff"
    params = {
        "token": Apeks.TOKEN,
        "staff_id": str(staff_id),
        "month": str(month),
        "year": str(year),
    }
    return endpoint, params


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
                message = "В ответе API отсутствует ключ 'data'"
                logging.error(message)
                raise KeyError(message)
            data = response.get("data")
            if not isinstance(data, list):
                message = "Ответ API содержит некорректный тип данных (list expected)"
                logging.error(message)
                raise TypeError(message)
            logging.debug(
                "Проверка 'response' выполнена успешно. "
                "Возвращен список по ключу: 'data'"
            )
            return data
    else:
        message = f"Отсутствует статус ответа API"
        logging.error(message)
        raise ApeksApiException(message)


def check_api_staff_lessons_response(response: dict) -> list:
    """
    Проверяем ответ API Апекс-ВУЗ со списком занятий
    на наличие необходимых ключей и корректность данных.
    """
    if not isinstance(response, dict):
        message = "Ответ API содержит некорректный тип данных (dict expected)"
        raise TypeError(message)
    if "data" not in response:
        message = "В ответе API отсутствует ключ 'data'"
        raise ApeksApiException(message)
    data = response.get("data")
    if not isinstance(data, dict):
        message = "Ответ API содержит некорректный тип данных (dict expected)"
        raise TypeError(message)
    if "lessons" not in data:
        message = "В ответе API отсутствует ключ 'lessons'"
        raise ApeksApiException(message)
    lessons = data.get("lessons")
    if not isinstance(lessons, list):
        message = "Ответ API содержит некорректный тип данных (list expected)"
        raise TypeError(message)
    return lessons


def get_disc_list() -> list:
    """
    Получение полного списка дисциплин из справочника Апекс-ВУЗ
    [{id': id,
    'name': Название,
    'name_short': Сокращенное название}].
    """
    response = api_get_db_table(Apeks.tables.get("plan_disciplines"), level=3)
    return check_api_db_response(response)


def get_departments() -> dict:
    """
    Получение информации о кафедрах
    {id:[name, short_name]}.
    """
    dept_dict = {}
    resp = check_api_db_response(
        api_get_db_table("state_departments", parent_id=Apeks.DEPT_ID)
    )
    for dept in resp:
        dept_dict[dept["id"]] = [dept.get("name"), dept.get("name_short")]
    return dept_dict
