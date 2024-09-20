import json
import logging

from config import ApeksConfig as Apeks
from .api_get import api_get_db_table, check_api_db_response
from ..services.apeks_db_state_departments_service import get_db_apeks_state_departments_service


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
    response = list(
        await check_api_db_response(
            await api_get_db_table(table, setting="system.ou.name")
        )
    )
    logging.debug(f"Передана информация о названии организации")
    return response[0].get("value")


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

    response = list(
        await check_api_db_response(
            await api_get_db_table(table, setting="system.head.chief")
        )
    )
    value = response[0].get("value")

    if value:
        chief_data = json.loads(value)
        name = chief_data.get("name").split()
        if len(name) >= 3:
            chief_data["name_short"] = f"{name[1][0]}.{name[2][0]}. {name[0]}"
        logging.debug(f"Передана информация о руководителе")
        return chief_data

async def get_departments(department_filter):
    """Временная функция для получения списка подразделений."""
    departments_service = get_db_apeks_state_departments_service()
    departments = await departments_service.get_departments(department_filter=department_filter)
    return {int(dept_id): value for dept_id, value in departments.items()}

