from __future__ import annotations

import logging
from calendar import monthrange
from collections import OrderedDict
from datetime import date
from json import JSONDecodeError

import httpx
from cache import AsyncTTL
from phpserialize import loads

from app.common.exceptions import ApeksApiException
from config import ApeksConfig as Apeks


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
                    logging.debug(f"{func.__name__}. Запрос успешно выполнен: {params}")
                    return resp_json
                except JSONDecodeError as error:
                    logging.error(
                        f"{func.__name__}. Ошибка конвертации "
                        f"ответа API Апекс-ВУЗ в JSON: '{error}'"
                    )

    return wrapper


@api_get_request_handler
async def api_get_db_table(
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
    logging.debug(
        "Переданы параметры для запроса 'api_get_db_table': " f"к таблице {table_name}"
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


def data_processor(table_data: list, dict_key: str = "id") -> dict:
    """
    Преобразует полученные данные из таблиц БД Апекс-ВУЗ.

    Parameters
    ----------
        table_data: list
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
        data[int(d_val.get(dict_key))] = d_val
    logging.debug(f"Обработаны данные. Ключ: {dict_key}")
    return data


@AsyncTTL(time_to_live=60, maxsize=1024)
async def get_organization_name(
    table: str = Apeks.TABLES.get("system_settings"),
) -> str:
    """
    Получение полного названия образовательной организации.

    Parameters
    ----------
        table: str
            таблица БД, содержащая системные сведения о ВУЗе.

    Returns
    ----------
        str
            название
    """
    response = await check_api_db_response(
        await api_get_db_table(table, setting="system.ou.name")
    )
    return response[0].get("value")


@AsyncTTL(time_to_live=360, maxsize=1024)
async def get_organization_chief_info(
    table: str = Apeks.TABLES.get("system_settings"),
) -> dict:
    """
    Получение данных о руководителе образовательной организации.

    Parameters
    ----------
        table: str
            таблица БД, содержащая системные сведения о ВУЗе.

    Returns
    ----------
        dict
            {'name': 'Фамилия Имя Отчество',
             'position': 'должность',
             'specialRank': 'id',
             'name_short': 'И.О. Фамилия'}
    """

    response = await check_api_db_response(
        await api_get_db_table(table, setting="system.head.chief")
    )
    value = response[0].get("value")

    if value:
        chief_data = dict(
            loads(value.encode(), decode_strings=True, array_hook=OrderedDict)
        )
        name = chief_data.get("name").split()
        if len(name) >= 3:
            chief_data["name_short"] = f"{name[1][0]}.{name[2][0]}. {name[0]}"
        return chief_data


@AsyncTTL(time_to_live=360, maxsize=1024)
async def get_rank_name(
    rank_id: int | str, table: str = Apeks.TABLES.get("state_special_ranks")
) -> list:
    """
    Получение названий званий.

    :param rank_id: id звания
    :param table: название таблицы 'state_special_ranks'
    :return: list [name, name_short]
    """
    response = await check_api_db_response(await api_get_db_table(table, id=rank_id))
    name = response[0].get("name")
    name_short = response[0].get("name_short")
    return [name, name_short]


@AsyncTTL(time_to_live=60, maxsize=1024)
async def get_disciplines(
    table: str = Apeks.TABLES.get("plan_disciplines"),
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
    response = await check_api_db_response(await api_get_db_table(table, level=level))
    disc_dict = {}
    for disc in response:
        disc_dict[int(disc["id"])] = {
            "full": disc.get("name"),
            "short": disc.get("name_short"),
        }
    logging.debug("Информация о дисциплинах успешно передана")
    return disc_dict


@AsyncTTL(time_to_live=360, maxsize=1024)
async def get_departments(
    table: str = Apeks.TABLES.get("state_departments"),
    parent_id: str | int = Apeks.DEPT_ID,
) -> dict:
    """
    Получение информации о кафедрах.

    Parameters
    ----------
        table:str
            таблица БД, содержащая перечень дисциплин.
        parent_id: int | str
            идентификатор для типа подразделений кафедра в базе данных.

    Returns
    ----------
        dict
            {id: {'full': 'название кафедры', 'short': 'сокращенное название'}}
    """
    response = await check_api_db_response(
        await api_get_db_table(table, parent_id=parent_id)
    )
    dept_dict = {}
    for dept in response:
        dept_dict[int(dept["id"])] = {
            "full": dept.get("name"),
            "short": dept.get("name_short"),
        }
    logging.debug("Информация о кафедрах успешно передана")
    return dept_dict


@AsyncTTL(time_to_live=60, maxsize=1024)
async def get_state_staff(table: str = Apeks.TABLES.get("state_staff")) -> dict:
    """
    Получение имен преподавателей.

    Parameters
    ----------
        table:str
            таблица БД, содержащая имена преподавателей.

    Returns
    ----------
        dict
            {id: {'full': 'полное имя', 'short': 'сокращенное имя'}}
    """
    staff_dict = {}
    resp = await check_api_db_response(await api_get_db_table(table))
    for staff in resp:
        family_name = staff.get("family_name") if staff.get("family_name") else "??????"
        first_name = staff.get("name") if staff.get("name") else "??????"
        second_name = staff.get("surname") if staff.get("surname") else "??????"
        staff_dict[int(staff.get("id"))] = {
            "full": f"{family_name} {first_name} {second_name}",
            "short": f"{family_name} {first_name[0]}.{second_name[0]}.",
        }
    logging.debug("Информация о преподавателях успешно передана")
    return staff_dict


@api_get_request_handler
async def get_lessons(
    year: int,
    month_start: int,
    month_end: int,
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
        table_name: str
            имя_таблицы
        url: str
            URL сервера
        token: str
            токен для API
    """
    first_day = 1
    last_day = monthrange(year, month_end)[1]
    endpoint = f"{url}/api/call/system-database/get"
    params = {
        "token": token,
        "table": table_name,
        "filter": f"date between '{date(year, month_start, first_day).isoformat()}' "
        f"and '{date(year, month_end, last_day).isoformat()}'",
    }
    logging.debug(
        "Переданы параметры для запроса 'get_lessons': "
        f"date between '{date(year, month_start, first_day).isoformat()}' "
        f"and '{date(year, month_end, last_day).isoformat()}'"
    )
    return endpoint, params


async def get_plan_curriculum_disciplines(education_plan_id: int | str) -> dict:
    """
    Получение данных о дисциплинах учебного плана

    Parameters
    ----------
        education_plan_id: int | str
            id учебного плана

    Returns
    ----------
        dict
            {curriculum_discipline_id: [disc_code, disc_name]}
    """

    def disc_name(discipline_id):
        for discipline in disciplines_list:
            if discipline.get("id") == discipline_id:
                return discipline.get("name")

    disciplines = {}
    disciplines_list = await check_api_db_response(
        await api_get_db_table(Apeks.TABLES.get("plan_disciplines"))
    )
    plan_disciplines = await check_api_db_response(
        await api_get_db_table(
            Apeks.TABLES.get("plan_curriculum_disciplines"),
            education_plan_id=education_plan_id,
        )
    )
    for disc in plan_disciplines:
        if str(disc.get("level")) == str(Apeks.DISC_LEVEL) and not str(
            disc.get("type")
        ) == str(Apeks.DISC_TYPE):
            disciplines[int(disc.get("id"))] = [
                disc.get("code"),
                disc_name(disc.get("discipline_id")),
            ]
    return disciplines


async def get_plan_work_programs(disciplines_list: list) -> dict:
    """
    Получение рабочих программ плана

    Parameters
    ----------
        disciplines_list: list
            список дисциплин учебного плана

    Returns
    ----------
        dict
            {work_program_id: {disc_code: disc_name}}
    """
    wp_data = []
    for disc_id in disciplines_list:
        response = await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("mm_work_programs"),
                    curriculum_discipline_id=disc_id,
                )
            )
        wp_data += response
    return data_processor(wp_data)
