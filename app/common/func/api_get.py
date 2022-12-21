from __future__ import annotations

import logging
from calendar import monthrange
from datetime import date
from json import JSONDecodeError

import httpx

from config import ApeksConfig as Apeks
from app.common.exceptions import ApeksApiException


def api_get_request_handler(func):
    """Декоратор для функций, отправляющих GET запрос к API Апекс-ВУЗ"""

    async def wrapper(*args, **kwargs) -> dict:
        endpoint, params = await func(*args, **kwargs)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(endpoint, params=params)
                response.raise_for_status()
            except httpx.RequestError as exc:
                logging.error(
                    f"{func.__name__}. Ошибка при запросе к "
                    f"API Апекс-ВУЗ: {exc.request.url!r}."
                )
            except httpx.HTTPStatusError as exc:
                logging.error(
                    f"{func.__name__}. Произошла ошибка "
                    f"{exc.response.status_code} во время "
                    f"запроса {exc.request.url!r}."
                )
            else:
                try:
                    resp_json = response.json()
                    del params["token"]
                    if resp_json.get("status") == 1:
                        logging.debug(
                            f"{func.__name__}. Запрос успешно выполнен: {params}"
                        )
                        return resp_json
                    else:
                        logging.debug(
                            f"{func.__name__}. Произошла ошибка: "
                            f"{resp_json.get('message')}"
                        )
                        return resp_json
                except JSONDecodeError as error:
                    logging.error(
                        f"{func.__name__}. Ошибка конвертации "
                        f"ответа API Апекс-ВУЗ в JSON: '{error}'"
                    )

    return wrapper


@api_get_request_handler
async def api_get_db_table(
    table_name: str,
    url: str = Apeks.URL,
    token: str = Apeks.TOKEN,
    **kwargs,
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
        **kwargs:
            'filter_name=value' для дополнительных фильтров запроса
    """
    endpoint = f"{url}/api/call/system-database/get"
    params = {"token": token, "table": table_name}
    if kwargs:
        for db_filter, db_value in kwargs.items():
            if type(db_value) in (int, str):
                values = str(db_value)
            else:
                values = [str(val) for val in db_value]
            params[f"filter[{db_filter}][]"] = values
    logging.debug(
        f"Переданы параметры для запроса 'api_get_db_table': к таблице {table_name}"
    )
    return endpoint, params


async def check_api_db_response(response: dict) -> list:
    """
    Проверяет ответ на запрос к БД Апекс-ВУЗ через API.

    Parameters
    ----------
        response: dict
            ответ от сервера

    Returns
    ----------
        list
            список словарей с содержимым ответа API по ключу 'data'
    """
    if not isinstance(response, dict):
        message = "Нет связи с сервером или получен неверный ответ от API Апекс-ВУЗ"
        logging.error(message)
        raise ApeksApiException(message)
    if "status" in response:
        if response.get("status") == 0:
            message = f'Неверный статус ответа API: "{response}"'
            logging.error(message)
            raise ApeksApiException(message)
        else:
            if "data" not in response:
                message = "В ответе API отсутствует ключ 'data'"
                logging.error(message)
                raise ApeksApiException(message)
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


@api_get_request_handler
async def api_get_staff_lessons(
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
            месяц (число от 1 до 12)
        year: int | str,
            год (число 20хх)
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
    logging.debug(
        "Переданы параметры для запроса 'api_get_staff_lessons':"
        f"staff_id: {str(staff_id)}, month: {str(month)}, year: {str(year)}"
    )
    return endpoint, params


async def check_api_staff_lessons_response(response: dict) -> list:
    """
    Проверяет ответ API Апекс-ВУЗ со списком занятий на наличие необходимых
    ключей и корректность данных.

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
        message = "Нет связи с сервером или получен неверный ответ от API Апекс-ВУЗ"
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
        "Проверка 'response' выполнена успешно. Возвращен список по ключу: 'lessons'"
    )
    return lessons


@api_get_request_handler
async def get_lessons(
    year: int,
    month_start: int,
    month_end: int,
    day_start: int = 1,
    day_end: int = None,
    table_name: str = Apeks.TABLES.get("schedule_day_schedule_lessons"),
    url: str = Apeks.URL,
    token: str = Apeks.TOKEN,
):
    """
    Получение списка занятий за указанный период.

    Parameters
    ----------
        year: int
            учебный год (число 20xx).
        month_start: int
            начальный месяц (число 1-12).
        month_end: int
            конечный месяц (число 1-12).
        day_start: int
            начальная дата (число 1-31).
        day_end: int
            конечная дата (число 1-31).
        table_name: str
            имя_таблицы
        url: str
            URL сервера
        token: str
            токен для API
    """
    if not day_end:
        day_end = monthrange(year, month_end)[1]
    endpoint = f"{url}/api/call/system-database/get"
    params = {
        "token": token,
        "table": table_name,
        "filter": f"date between '{date(year, month_start, day_start).isoformat()}' "
        f"and '{date(year, month_end, day_end).isoformat()}'",
    }
    logging.debug(
        "Переданы параметры для запроса 'get_lessons': "
        f"date between '{date(year, month_start, day_start).isoformat()}' "
        f"and '{date(year, month_end, day_end).isoformat()}'"
    )
    return endpoint, params
