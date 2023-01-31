from __future__ import annotations

import logging

from config import ApeksConfig as Apeks
from .api_get import check_api_db_response, api_get_db_table


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
    rank_name = [name, name_short]
    logging.debug(f"Передана информация о специальном звании")
    return rank_name


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
            {id: {'full': 'полное имя',
                  'short': 'сокращенное имя',
                  'user_id': user_id}}
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
            "user_id": staff.get("user_id"),
        }
    logging.debug("Информация о преподавателях успешно передана")
    return staff_dict
