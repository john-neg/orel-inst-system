from __future__ import annotations

import logging
import re

from openpyxl import load_workbook

from common.classes.EducationPlan import (
    EducationPlanCompetencies,
    EducationPlanIndicators,
)
from common.func.api_delete import api_delete_from_db_table
from common.func.api_get import (
    get_work_programs_data,
    get_plan_curriculum_disciplines,
    check_api_db_response,
    api_get_db_table,
    get_plan_discipline_competencies,
)
from common.func.api_post import api_add_to_db_table, api_edit_db_table
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


def get_competency_code(indicator) -> str:
    """
    Выводит код компетенций индикатора.

    :return: код компетенции
    """
    comp_code = re.split(Apeks.COMP_FROM_IND_REGEX, indicator, 1)[0]
    if len(comp_code) > 12:
        comp_code = re.split(Apeks.FULL_CODE_SPLIT_REGEX, indicator, 1)[0]
    return comp_code


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
        curriculum_discipline_id=[*plan_disciplines], competencies=True
    )
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
        work_programs_data=work_programs_data,
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


async def work_programs_competencies_level_del(
    level_id: int | str | tuple[int | str] | list[int | str],
    table_name: str = Apeks.TABLES.get("mm_competency_levels"),
) -> dict:
    """
    Удаление данных об уровнях сформированности компетенций из рабочих программ.

    Parameters
    ----------
        level_id: int | str | tuple[int | str] | list[int | str]
            id уровня сформированности компетенций
        table_name: str
            имя таблицы в БД
    """
    if level_id:
        response = await api_delete_from_db_table(
            table_name,
            id=level_id,
        )
    else:
        response = {"status": 1, "data": 0}
    if response.get("status") == 1:
        logging.debug(
            f"Удалены уровни (кол-во - {response.get('data')}) формирования "
            "компетенций из рабочих программ."
        )
    else:
        logging.error(
            f"Не удалось удалить уровни {level_id} формирования компетенций "
            "из рабочих программ."
        )
    return response


async def work_program_competency_data_add(
    fields: dict,
    table_name: str = Apeks.TABLES.get("mm_work_programs_competencies_data"),
) -> dict:
    """
    Добавление данных о компетенции в рабочую программу.

    :param fields: {"work_program_id": val, "competency_id": val,
        "field_id": val, "value": val}
    :param table_name: имя таблицы БД
    :return: ответ api {status: code, data: val}
    """
    response = await api_add_to_db_table(
        table_name,
        **fields,
    )
    if response.get("status") == 1:
        logging.debug(
            "Добавлены данные о компетенции в рабочую программу "
            f"{fields.get('work_program_id')}."
        )
    else:
        logging.error(
            f"Не удалось добавить данные о компетенции в рабочую программу "
            f"{fields.get('work_program_id')}."
        )
    return response


async def work_program_competency_level_add(
    fields: dict,
    table_name: str = Apeks.TABLES.get("mm_competency_levels"),
) -> dict:
    """
    Добавление данных об уровне формирования компетенций в рабочую программу.

    :param fields: {"work_program_id": val, "level": val, "semester_id": val,
        "control_type_id": val, "knowledge": val, "abilities": val,
        "ownerships": val, "level1": "", "level2": "", "level3": ""}
    :param table_name: имя таблицы БД
    :return: ответ api {status: code, data: value}
    """
    response = await api_add_to_db_table(
        table_name,
        **fields,
    )
    if response.get("status") == 1:
        logging.debug(
            "Добавлены данные об уровне формирования компетенций в "
            f"рабочую программу {fields.get('work_program_id')}."
        )
    else:
        logging.error(
            "Не удалось добавить данные об уровне формирования компетенций в "
            f"рабочую программу {fields.get('work_program_id')}."
        )
    return response


async def work_program_competency_level_edit(
    work_program_id: int | str,
    fields: dict,
    level: int | str = Apeks.BASE_COMP_LEVEL,
    table_name: str = Apeks.TABLES.get("mm_competency_levels"),
) -> dict:
    """
    Изменение данных об уровне формирования компетенций в рабочей программе.

    :param work_program_id: id рабочей программы
    :param fields: поля для редактирования {"semester_id": val,
        "control_type_id": val, "knowledge": val, "abilities": val,
        "ownerships": val, "level1": "", "level2": "", "level3": ""}
    :param level: номер уровня сформированности для редактирования
    :param table_name: имя таблицы БД
    :return: ответ api {status: code, data: value}
    """
    filters = {"work_program_id": work_program_id, "level": level}
    response = await api_edit_db_table(table_name, filters, fields)

    if response.get("status") == 1:
        logging.debug(
            "Изменены сведения об уровне формирования компетенций "
            f"в рабочей программе {work_program_id}."
        )
    else:
        logging.error(
            "Не удалось изменить сведения об уровне формирования компетенций "
            f"в рабочей программе {work_program_id}."
        )
    return response
