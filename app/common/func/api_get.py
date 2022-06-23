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
from app.common.func.app_core import data_processor
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
        **kwargs: int | str | tuple[int | str] | list[int | str]
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
        "Проверка 'response' выполнена успешно. Возвращен список по ключу: 'lessons'"
    )
    return lessons


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


@AsyncTTL(time_to_live=60, maxsize=1024)
async def get_plan_disciplines(
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


async def get_plan_education_specialties() -> dict:
    """
    Получение групп специальностей.

    Returns
    ----------
        dict
            {speciality_id: speciality_name}
    """

    request = data_processor(
        await check_api_db_response(
            await api_get_db_table(
                Apeks.TABLES.get("plan_education_specialties"),
            )
        )
    )
    specialties = {}
    for i in request:
        specialties[i] = request[i].get("name")
    logging.debug(
        "Информация о специальностях 'plan_education_specialties' успешно передана"
    )
    return specialties


async def get_education_plans(
    education_specialty_id: int | str, year: int | str = 0
) -> dict:
    """
    Получение списка планов по указанной специальности.

    Parameters
    ----------
        education_specialty_id: int | str
            id специальности из таблицы 'plan_education_specialties'.
        year: int | str
            год начала обучения по плану (по умолчанию 0 = все)

    Returns
    ----------
        dict
            {plan_id: plan_name}
    """

    education_plans = data_processor(
        await check_api_db_response(
            await api_get_db_table(
                Apeks.TABLES.get("plan_education_plans"),
                data_type="plan",
                education_specialty_id=education_specialty_id,
                active="1",
            )
        )
    )

    plans = {}
    if year == 0:
        for plan in education_plans:
            plans[plan] = education_plans[plan].get("name")
    else:
        plans_dates = data_processor(
            await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("plan_semesters"),
                    education_plan_id=[*education_plans],
                    # Параметры для получения года начала обучения
                    course="1",
                    semester="1",
                )
            ),
            "education_plan_id",
        )
        for plan in education_plans:
            if education_plans[plan].get("custom_start_year") == str(year):
                plans[plan] = education_plans[plan].get("name")
            elif education_plans[plan].get("custom_start_year") is None:
                if plans_dates.get(plan).get("start_date").split("-")[0] == str(year):
                    plans[plan] = education_plans[plan].get("name")
    logging.debug(
        "Список учебных планов по специальности "
        f"{education_specialty_id} успешно передан"
    )
    return plans


async def get_plan_curriculum_disciplines(
    education_plan_id: int | str, disc_filter: bool = True, **kwargs
) -> dict:
    """
    Получение данных о дисциплинах учебного плана

    Parameters
    ----------
        education_plan_id: int | str
            id учебного плана
        disc_filter: bool
            фильтр удаляет блоки, части блоков и группы дисциплин. Если True,
            то остаются только фактически изучаемые дисциплины.
        **kwargs
            дополнительные фильтры (например department_id)

    Returns
    ----------
        dict
            {curriculum_discipline_id: {'code': code,
                                        'name': name,
                                        'department_id': department_id
                                        'level': value
                                        'left_node: value}}
    """

    def disc_name(discipline_id: int) -> str:
        for discipline in disciplines_list:
            if discipline.get("id") == discipline_id:
                return discipline.get("name")

    disciplines_list = await check_api_db_response(
        await api_get_db_table(Apeks.TABLES.get("plan_disciplines"))
    )
    plan_disciplines = await check_api_db_response(
        await api_get_db_table(
            Apeks.TABLES.get("plan_curriculum_disciplines"),
            education_plan_id=education_plan_id,
            **kwargs,
        )
    )
    disciplines = {}
    for disc in plan_disciplines:
        disciplines[int(disc.get("id"))] = {
            "code": disc.get("code"),
            "name": disc_name(disc.get("discipline_id")),
            "department_id": disc.get("department_id"),
            "level": disc.get("level"),
            "type": disc.get("type"),
            "left_node": disc.get("left_node"),
        }
    if disc_filter:
        for disc in [*disciplines]:
            if str(disciplines[disc].get("level")) != str(Apeks.DISC_LEVEL) or str(
                disciplines[disc].get("type")
            ) == str(Apeks.DISC_TYPE):
                del disciplines[disc]
    logging.debug(
        f"Передана информация о дисциплинах " f"education_plan_id: {education_plan_id}"
    )
    return disciplines


async def get_plan_discipline_competencies(
    curriculum_discipline_id: tuple[int | str] | list[int | str],
) -> dict:
    """
    Получение данных о связях дисциплин и компетенций учебного плана

    Parameters
    ----------
        curriculum_discipline_id: int | str
            id учебной дисциплины плана

    Returns
    ----------
        dict
            {curriculum_discipline_id: []}
    """

    response = await check_api_db_response(
        await api_get_db_table(
            Apeks.TABLES.get("plan_curriculum_discipline_competencies"),
            curriculum_discipline_id=curriculum_discipline_id,
        )
    )
    discipline_competencies = {}
    for res in response:
        disc_id = int(res.get("curriculum_discipline_id"))
        comp_id = int(res.get("competency_id"))
        discipline_competencies.setdefault(disc_id, []).append(comp_id)

    logging.debug(
        f"Передана информация о компетенциях учебных дисциплин {curriculum_discipline_id}"
    )
    return discipline_competencies


async def get_work_programs_data(
    sections: bool = False,
    fields: bool = False,
    signs: bool = False,
    competencies: bool = False,
    **kwargs: int | str | tuple[int | str] | list[int | str],
) -> dict:
    """
    Получение информации о рабочих программах.

    Parameters
    ----------
        sections: bool
            если True то запрашивается также информация о целях и задачах,
            месте в структуре ООП из таблицы 'mm_sections'
        fields: bool
            если True то запрашивается также информация о полях программ
            из таблицы 'mm_work_programs_data'
        signs: bool
            если True то запрашивается также информация о согласовании программ
            из таблицы 'mm_work_programs_signs'
        competencies: bool
            если True то запрашивается также информация о компетенциях для
            программы и уровнях сформированности компетенций
            из таблиц 'mm_competency_levels', 'mm_work_programs_competencies_data'
        **kwargs: int | str | tuple[int | str] | list[int | str]:
            параметры для запроса (поле или несколько полей таблицы mm_work_programs)
            Например: curriculum_discipline_id=value, id=[list]

    Returns
    ----------
        dict
            {id: {"id": value,
                  "curriculum_discipline_id": value,
                  "name": value,
                  "description": value,
                  "authors": value,
                  "reviewers_int": value,
                  "reviewers_ext": value,
                  "date_create": value,
                  "date_approval": value,
                  "date_department": value,
                  "document_department": value,
                  "date_methodical": value,
                  "document_methodical": value",
                  "date_academic": value,
                  "document_academic": value,
                  "status": value,
                  "user_id": value,
                  "settings": "[]",
                  "sections": {"purposes": value,
                               "tasks": value,
                               "place_in_structure": value,
                               "knowledge": value,
                               "skills": value,
                               "abilities": value,
                               "ownerships": value}
                  "fields": {id: value},
                  "signs": {user_id: timestamp},
                  "competencies_data": {comp_id: {field_id: value}}
                  "competency_levels": {level_id: {'abilities': value,
                                                   'control_type_id': value,
                                                   'knowledge': value,
                                                   'level1': value,
                                                   'level2': value,
                                                   'level3': value,
                                                   'ownerships': value
                                                   'semester_id': value}}
    """
    wp_data = data_processor(
        await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("mm_work_programs"), **kwargs)
        )
    )
    for wp in wp_data:
        wp_data[wp]["sections"] = {}
        wp_data[wp]["fields"] = {}
        wp_data[wp]["signs"] = {}
        wp_data[wp]["competencies_data"] = {}
        wp_data[wp]["competency_levels"] = {}

    wp_list = [wp_data[wp].get("id") for wp in wp_data]

    if wp_list:
        if sections:
            sections_data = await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("mm_sections"),
                    work_program_id=wp_list,
                )
            )
            for sect in sections_data:
                wp_id = int(sect.get("work_program_id"))
                not_include = {"id", "work_program_id"}
                items = [item for item in [*sect] if item not in not_include]
                for item in items:
                    wp_data[wp_id]["sections"][item] = sect.get(item)

        if fields:
            field_data = await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("mm_work_programs_data"),
                    work_program_id=wp_list,
                )
            )
            for field in field_data:
                wp_id = int(field.get("work_program_id"))
                field_id = int(field.get("field_id"))
                data = field.get("data")
                wp_data[wp_id]["fields"][field_id] = data

        if signs:
            signs_data = await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("mm_work_programs_signs"),
                    work_program_id=wp_list,
                )
            )
            for sign in signs_data:
                wp_id = int(sign.get("work_program_id"))
                user_id = int(sign.get("user_id"))
                wp_data[wp_id]["signs"][user_id] = sign.get("timestamp")

        if competencies:
            competencies_fields = await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("mm_work_programs_competencies_fields"),
                )
            )
            comp_fields = {}
            for field in competencies_fields:
                comp_fields[field.get("id")] = field.get("code")
            comp_data = await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("mm_work_programs_competencies_data"),
                    work_program_id=wp_list,
                )
            )
            for data in comp_data:
                wp_id = int(data.get("work_program_id"))
                comp_id = int(data.get("competency_id"))
                field = comp_fields.get(data.get("field_id"))
                if not wp_data[wp_id]["competencies_data"].get(comp_id):
                    wp_data[wp_id]["competencies_data"][comp_id] = {}
                wp_data[wp_id]["competencies_data"][comp_id][field] = data.get("value")

            comp_levels = await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("mm_competency_levels"),
                    work_program_id=wp_list,
                )
            )
            for level in comp_levels:
                wp_id = int(level.get("work_program_id"))
                level_id = int(level.get("level"))
                not_include = {"id", "work_program_id"}
                items = [item for item in [*level] if item not in not_include]
                for item in items:
                    if not wp_data[wp_id]["competency_levels"].get(level_id):
                        wp_data[wp_id]["competency_levels"][level_id] = {}
                    wp_data[wp_id]["competency_levels"][level_id][item] = level.get(
                        item
                    )

    logging.debug("Передана информация о рабочих программах " f"дисциплин {wp_list}")
    return wp_data
