from __future__ import annotations

import logging
from collections import OrderedDict

from cache import AsyncTTL
from phpserialize import loads

from app.common.func.api_get import check_api_db_response, api_get_db_table
from config import ApeksConfig as Apeks


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
    logging.debug(f"Передана информация о названии организации")
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
        logging.debug(f"Передана информация о руководителе")
        return chief_data


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
