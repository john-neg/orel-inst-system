from __future__ import annotations

import logging
from json import JSONDecodeError

import requests

from app.common.exceptions import ApeksApiException
from config import ApeksConfig as Apeks




def api_get_request_handler(func):
    """Декоратор для функций, отправляющих GET запрос к API Апекс-ВУЗ"""

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
def api_get_db_table(
    table_name: str, url: str = Apeks.URL, token: str = Apeks.TOKEN, **kwargs
):
    """
    Запрос к API для получения информации из таблицы базы данных Апекс-ВУЗ.

    Parameters
    ----------
    table_name: str
        имя_таблицы
    url: str
        URL сервера
    token: str
        токен для API
    **kwargs: int | str
        'filter_name=value' для дополнительных фильтров запроса
    """
    endpoint = f"{url}/api/call/system-database/get"
    params = {"token": token, "table": table_name}
    if kwargs:
        for db_filter, db_value in kwargs.items():
            params[f"filter[{db_filter}]"] = str(db_value)
    return endpoint, params


@api_get_request_handler
def api_get_staff_lessons(
    staff_id: int | str,
    month: int | str,
    year: int | str,
    url: str = Apeks.URL,
    token: str = Apeks.TOKEN,
):
    """
    Получение списка занятий по id преподавателя за определенный месяц и год.

    Parameters
    ----------
    staff_id: int | str,
        id преподавателя
    month: int | str,
        месяц, 1-12
    year: int | str,
        год
    url: str
        URL сервера
    token: str
        токен для API
    """
    endpoint = f"{url}/api/call/schedule-schedule/staff"
    params = {
        "token": token,
        "staff_id": str(staff_id),
        "month": str(month),
        "year": str(year),
    }
    return endpoint, params


def check_api_db_response(response: dict) -> list:
    """
    Проверка ответа на запрос к БД Апекс-ВУЗ через API.

    Parameters
    ----------
    response: dict
        ответ от сервера

    Returns
    ----------
    list
        список словарей с содержимым поля 'data'
    """
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

    Parameters
    ----------
    response: dict
        ответ от сервера

    Returns
    ----------
    list
        список словарей с содержимым поля 'lessons'
    """
    if not isinstance(response, dict):
        message = "Ответ API содержит некорректный тип данных (dict expected)"
        logging.error(message)
        raise TypeError(message)
    if "data" not in response:
        message = "В ответе API отсутствует ключ 'data'"
        logging.error(message)
        raise ApeksApiException(message)
    data = response.get("data")
    if not isinstance(data, dict):
        message = "Ответ API содержит некорректный тип данных (dict expected)"
        logging.error(message)
        raise TypeError(message)
    if "lessons" not in data:
        message = "В ответе API отсутствует ключ 'lessons'"
        logging.error(message)
        raise ApeksApiException(message)
    lessons = data.get("lessons")
    if not isinstance(lessons, list):
        message = "Ответ API содержит некорректный тип данных (list expected)"
        logging.error(message)
        raise TypeError(message)
    logging.debug(
        "Проверка 'response' выполнена успешно. " "Возвращен список по ключу: 'lessons'"
    )
    return lessons


def get_disciplines(
    table: str = Apeks.tables.get("plan_disciplines"),
    level: int | str = Apeks.DISC_LEVEL,
) -> dict:
    """
    Получение полного списка дисциплин из справочника Апекс-ВУЗ.

    Parameters
    ----------
    table: str
        таблица БД, содержащая перечень дисциплин.
    level: int | str
        уровень дисциплин в учебном плане.

    Returns
    ----------
    dict
        {id: {'full': 'название дисциплины', 'short': 'сокращенное название'}}
    """
    response = check_api_db_response(api_get_db_table(table, level=level))
    disc_dict = {}
    for disc in response:
        disc_dict[int(disc["id"])] = {
            'full': disc.get("name"),
            'short': disc.get("name_short")
        }
    logging.debug("Информация о дисциплинах успешно передана")
    return disc_dict


def get_departments(
    table: str = Apeks.tables.get("state_departments"),
    parent_id: str | int = Apeks.DEPT_ID,
) -> dict:
    """
    Получение информации о кафедрах.

    Parameters
    ----------
    table: str
        таблица БД, содержащая перечень дисциплин.
    parent_id: int | str
        идентификатор для типа подразделений кафедра в базе данных.

    Returns
    ----------
    dict
        {id: {'full': 'название кафедры', 'short': 'сокращенное название'}}
    """
    response = check_api_db_response(api_get_db_table(table, parent_id=parent_id))
    dept_dict = {}
    for dept in response:
        dept_dict[int(dept["id"])] = {
            'full': dept.get("name"),
            'short': dept.get("name_short")
        }
    logging.debug("Информация о кафедрах успешно передана")
    return dept_dict


def get_state_staff(table: str = Apeks.tables.get("state_staff")) -> dict:
    """
    Получение имен преподавателей.

    Parameters
    ----------
    table: str
        таблица БД, содержащая имена преподавателей.

    Returns
    ----------
    dict
        {id: {'full': 'полное имя', 'short': 'сокращенное имя'}}
    """
    staff_dict = {}
    resp = check_api_db_response(api_get_db_table(table))
    for staff in resp:
        family_name = staff.get("family_name") if staff.get("family_name") else "??????"
        first_name = staff.get("name") if staff.get("name") else "??????"
        second_name = staff.get("surname") if staff.get("surname") else "??????"
        staff_dict[int(staff.get("id"))] = {
            'full': f"{family_name} {first_name} {second_name}",
            'short': f"{family_name} {first_name[0]}.{second_name[0]}.",
        }
    logging.debug("Информация о преподавателях успешно передана")
    return staff_dict
