import json
import logging

from config import ApeksConfig as Apeks
from .api_get import check_api_db_response, api_get_db_table


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


async def get_departments(
    table: str = Apeks.TABLES.get("state_departments"),
    department_filter=None,
) -> dict:
    """
    Получение информации о подразделениях.

    :param table: Название таблицы БД, содержащей список подразделений.
    :param department_filter: Тип подразделения (department, kafedra, faculty, other).
    :return: dict {'Название группы':
        {id: {'full': 'полное название', 'short': 'сокращенное название'}}}
    """
    state_departments = await check_api_db_response(
        await api_get_db_table(table)
    )

    filters = {
        "department": Apeks.DEPT_TYPES["0"],
        "kafedra": Apeks.DEPT_TYPES["1"],
        "faculty": Apeks.DEPT_TYPES["2"],
        "other": "Иные",
    }

    # Получаем id групп подразделений по типам, и группы подразделений
    groups_by_type = {}
    departments_groups = {}
    for dept in state_departments:
        if dept.get("type"):
            if dept.get("contains_staff") == "0":
                dept_type = Apeks.DEPT_TYPES[dept.get("type")]
            else:
                dept_type = "Иные"
            group_type = groups_by_type.setdefault(dept_type, [])
            group_type.append(dept.get("id"))
        else:
            parent_id = dept.get("parent_id") or "Other"
            group = departments_groups.setdefault(parent_id, [])
            group.append(dept)

    if departments_groups.get("Other"):
        groups_by_type["Иные"] = ["Other"]

    dept_dict = {}
    for group_type in groups_by_type:
        for group_id in groups_by_type[group_type]:
            dept_group = departments_groups.get(group_id)
            if dept_group:
                for dept in dept_group:
                    dept_dict[int(dept["id"])] = {
                        "full": dept.get("name"),
                        "short": dept.get("name_short"),
                        "type": group_type,
                    }

    logging.debug("Информация о подразделениях успешно передана")

    if filters.get(department_filter):
        return dict(
            filter(
                lambda x: x[1]["type"] == filters.get(department_filter),
                dept_dict.items(),
            )
        )
    else:
        return dept_dict
