from __future__ import annotations

import logging

import requests
from openpyxl import load_workbook

from app.main.func import db_filter_req
from common.classes.EducationPlan import EducationPlanCompetencies, \
    EducationPlanIndicators
from common.func.api_delete import api_delete_from_db_table
from common.func.api_get import (
    get_work_programs_data,
    get_plan_curriculum_disciplines,
    check_api_db_response,
    api_get_db_table,
    get_plan_discipline_competencies,
)
from common.func.api_post import api_add_to_db_table
from common.func.app_core import xlsx_iter_rows, xlsx_normalize, data_processor
from config import ApeksConfig as Apeks


def comps_file_processing(file: str) -> list:
    """
    Обработка загруженного файла c компетенциями.

    Parameters
    ----------
        file: str
            полный путь к файлу со списком компетенций

    Returns
    -------
        list
            нормализованный список компетенций из файла без первой строки
    """

    wb = load_workbook(file)
    ws = wb.active
    ws = xlsx_normalize(ws, Apeks.COMP_REPLACE_DICT)
    comps = list(xlsx_iter_rows(ws))
    del comps[0]
    return comps


async def get_plan_competency_instance(plan_id: int | str) -> EducationPlanCompetencies:
    """
    Возвращает экземпляр класса 'EducationPlanCompetencies' с
    данными, необходимыми для работы приложения 'plans'
    """
    plan_disciplines = await get_plan_curriculum_disciplines(plan_id, disc_filter=False)
    plan = EducationPlanCompetencies(
        education_plan_id=plan_id,
        plan_education_plans=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("plan_education_plans"), id=plan_id)
        ),
        plan_curriculum_disciplines=plan_disciplines,
        plan_competencies=data_processor(
            await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("plan_competencies"), education_plan_id=plan_id
                )
            )
        ),
        discipline_competencies=await get_plan_discipline_competencies(
            [*plan_disciplines]
        ),
    )
    return plan


async def get_plan_indicator_instance(plan_id: int | str) -> EducationPlanIndicators:
    """
    Возвращает экземпляр класса 'EducationPlanIndicators' с
    данными, необходимыми для работы модуля Матрица с индикаторами
    приложения 'plans'.
    """
    plan_disciplines = await get_plan_curriculum_disciplines(plan_id)
    work_programs_data = await get_work_programs_data(
        curriculum_discipline_id=[*plan_disciplines], competencies=True)
    plan = EducationPlanIndicators(
        education_plan_id=plan_id,
        plan_education_plans=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("plan_education_plans"), id=plan_id)
        ),
        plan_curriculum_disciplines=plan_disciplines,
        plan_competencies=data_processor(
            await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("plan_competencies"), education_plan_id=plan_id
                )
            )
        ),
        discipline_competencies=await get_plan_discipline_competencies(
            [*plan_disciplines]
        ),
        work_programs_data=work_programs_data
    )
    return plan




async def plan_competency_add(
    education_plan_id: int | str,
    code: str,
    description: str,
    left_node: int | str,
    right_node: int | str,
    level: int | str = 1,
    table_name: str = Apeks.TABLES.get("plan_competencies"),
) -> dict:
    """
    Добавление компетенции в учебный план.

    Parameters
    ----------
        education_plan_id: int | str
            id учебного плана
        code: str
            код компетенции
        description: str
            описание компетенции
        left_node: int | str
            начальная граница сортировки
        right_node: int | str
            конечная граница сортировки
        level: int | str = 1
            код уровня компетенции
        table_name: str
            имя таблицы в БД
    """

    response = await api_add_to_db_table(
        table_name,
        education_plan_id=education_plan_id,
        code=code,
        description=description,
        level=level,
        left_node=left_node,
        right_node=right_node,
    )
    if response.get("status") == 1:
        logging.debug(
            f"Добавлена компетенция {code} в учебный план: {education_plan_id}."
        )
    else:
        logging.debug(
            f"Компетенция {code} не добавлена в учебный план: {education_plan_id}."
        )
    return response


async def discipline_competency_add(
    curriculum_discipline_id: int | str,
    competency_id: int | str,
    table_name: str = Apeks.TABLES.get("plan_curriculum_discipline_competencies"),
) -> dict:
    """Добавление компетенции в учебный план.

    Parameters
    ----------
        curriculum_discipline_id: int | str,
            id дисциплины учебного плана
        competency_id: int | str
            id компетенции учебного плана
        table_name: str
            имя таблицы в БД
    """
    response = await api_add_to_db_table(
        table_name,
        curriculum_discipline_id=curriculum_discipline_id,
        competency_id=competency_id,
    )
    if response.get("status") == 1:
        logging.debug(
            f"Добавлена связь дисциплины ({curriculum_discipline_id}) "
            f"и компетенции ({competency_id})."
        )
    else:
        logging.debug(
            f"Не удалось добавить связь дисциплины ({curriculum_discipline_id}) "
            f"и компетенции ({competency_id})."
        )
    return response


async def plan_competencies_del(
    education_plan_id: int | str,
    table_name: str = Apeks.TABLES.get("plan_competencies"),
) -> dict:
    """
    Удаление данных о компетенциях из учебного плана.

    Parameters
    ----------
        education_plan_id: int | str
            id учебного плана
        table_name: str
            имя таблицы в БД
    """

    response = await api_delete_from_db_table(
        table_name,
        education_plan_id=education_plan_id,
    )
    if response.get("status") == 1:
        logging.debug(
            f"Удалены сведения о компетенциях из учебного плана: {education_plan_id}."
        )
    else:
        logging.debug(
            "Не удалось удалить сведения о компетенциях "
            f"из учебного плана: {education_plan_id}."
        )
    return response


async def plan_disciplines_competencies_del(
    curriculum_discipline_id: int | str | tuple[int | str] | list[int | str],
    table_name: str = Apeks.TABLES.get("plan_curriculum_discipline_competencies"),
) -> dict:
    """
    Удаление данных о связях компетенций с дисциплинами из учебного плана.

    Parameters
    ----------
        curriculum_discipline_id: int | str | tuple[int | str] | list[int | str]
            id учебной дисциплины плана
        table_name: str
            имя таблицы в БД
    """

    response = await api_delete_from_db_table(
        table_name,
        curriculum_discipline_id=curriculum_discipline_id,
    )
    if response.get("status") == 1:
        logging.debug(
            f"Удалены сведения о связях компетенций "
            f"с дисциплинами учебного плана: {curriculum_discipline_id}."
        )
    else:
        logging.debug(
            "Не удалось удалить сведения о связях компетенций "
            f"с дисциплинами учебного плана: {curriculum_discipline_id}."
        )
    return response


async def work_programs_competencies_del(
    work_program_id: int | str | tuple[int | str] | list[int | str],
    table_name: str = Apeks.TABLES.get("mm_work_programs_competencies_data"),
) -> dict:
    """
    Удаление данных о компетенциях из рабочих программ.

    Parameters
    ----------
        work_program_id: int | str | tuple[int | str] | list[int | str]
            id рабочей программы
        table_name: str
            имя таблицы в БД
    """

    response = await api_delete_from_db_table(
        table_name,
        work_program_id=work_program_id,
    )
    if response.get("status") == 1:
        logging.debug(
            f"Удалены сведения о компетенциях из рабочих программ: {work_program_id}."
        )
    else:
        logging.debug(
            "Не удалось удалить сведения о компетенциях "
            f"из рабочих программ: {work_program_id}."
        )
    return response


async def plan_competencies_data_delete(
    plan_id: int | str,
    plan_disciplines: list | tuple | dict,
    plan_comp: bool = True,
    relations: bool = True,
    work_program: bool = True,
) -> str:
    """
    Удаляет данные о компетенциях и связях дисциплин и компетенций из
    учебного плана и рабочих программ.

    Parameters
    ----------
        plan_id: int | str
            id учебного плана
        plan_disciplines: list | tuple | dict
            id дисциплин учебного плана
        plan_comp: bool
            удалять компетенции
        relations: bool
            удалять связи
        work_program: bool
            удалять из рабочих программ

    Returns
    -------
        str
            сведения о количестве удаленных элементов
    """
    message = ["Произведена очистка компетенций. ", "Количество удаленных записей: "]
    if work_program:
        work_programs_data = await get_work_programs_data(
            curriculum_discipline_id=[*plan_disciplines]
        )
        wp_resp = await work_programs_competencies_del(
            work_program_id=[*work_programs_data]
        )
        message.append(f"в рабочих программах - {wp_resp.get('data')},")
    if relations:
        disc_resp = await plan_disciplines_competencies_del(
            curriculum_discipline_id=[*plan_disciplines]
        )
        message.append(f"связей с дисциплинами - {disc_resp.get('data')},")
    if plan_comp:
        plan_resp = await plan_competencies_del(education_plan_id=plan_id)
        message.append(f"компетенций плана - {plan_resp.get('data')}.")
    return " ".join(message)











def disciplines_comp_load(curriculum_discipline_id, competency_id):
    """Загрузка связи дисциплины с компетенцией"""
    params = {"token": Apeks.TOKEN}
    data = {
        "table": "plan_curriculum_discipline_competencies",
        "fields[curriculum_discipline_id]": curriculum_discipline_id,
        "fields[competency_id]": competency_id,
    }
    requests.post(Apeks.URL + "/api/call/system-database/add", params=params, data=data)


def disciplines_wp_clean(work_program_id):
    """Удаление записей о компетенциях в РП"""
    params = {
        "token": Apeks.TOKEN,
        "table": "mm_work_programs_competencies_data",
        "filter[work_program_id]": work_program_id,
    }
    requests.delete(Apeks.URL + "/api/call/system-database/delete", params=params)


def disciplines_comp_del(curriculum_discipline_id):
    """Удаление связей дисциплины и компетенций"""
    params = {
        "token": Apeks.TOKEN,
        "table": "plan_curriculum_discipline_competencies",
        "filter[curriculum_discipline_id]": curriculum_discipline_id,
    }
    requests.delete(Apeks.URL + "/api/call/system-database/delete", params=params)


def comp_delete(education_plan_id):
    """Удаление компетенций из учебного плана"""
    data = db_filter_req("plan_competencies", "education_plan_id", education_plan_id)
    for i in range(len(data)):
        params = {
            "token": Apeks.TOKEN,
            "table": "plan_competencies",
            "filter[id]": data[i]["id"],
        }
        requests.delete(Apeks.URL + "/api/call/system-database/delete", params=params)


def create_wp(curriculum_discipline_id):
    """Создание программы"""
    params = {"token": Apeks.TOKEN}
    data = {
        "table": "mm_work_programs",
        "fields[curriculum_discipline_id]": curriculum_discipline_id,
        "fields[name]": get_wp_name(curriculum_discipline_id),
        "fields[user_id]": get_main_staff_id(curriculum_discipline_id),
    }
    requests.post(Apeks.URL + "/api/call/system-database/add", params=params, data=data)


def get_wp_name(curriculum_discipline_id):
    """Название программы как у дисциплины плана"""
    disc_id = db_filter_req(
        "plan_curriculum_disciplines", "id", curriculum_discipline_id
    )[0]["discipline_id"]
    return db_filter_req("plan_disciplines", "id", disc_id)[0]["name"]


def get_main_staff_id(curriculum_discipline_id):
    """
    Получение идентификатора начальника кафедры
    или самого старшего на момент запроса.
    """
    department_id = db_filter_req(
        "plan_curriculum_disciplines", "id", curriculum_discipline_id
    )[0]["department_id"]
    state_staff_id = db_filter_req(
        "state_staff_history", "department_id", department_id
    )[0]["staff_id"]
    user_id = db_filter_req("state_staff", "id", state_staff_id)[0]["user_id"]
    return user_id
