from __future__ import annotations

import logging

from app.common.classes.EducationPlan import EducationPlanWorkPrograms
from common.exceptions import (
    ApeksWrongParameterException,
    ApeksParameterNonExistException,
)
from common.func.api_post import api_add_to_db_table, api_edit_db_table
from config import ApeksConfig as Apeks


async def work_program_view_data(
    plan: EducationPlanWorkPrograms, parameter: str
) -> dict:
    """
    Возвращает список параметров рабочих программ плана.
    Если параметра нет в рабочей программе создает его.

    Parameters
    ----------
        plan: EducationPlanWorkPrograms
            экземпляр класса EducationPlanWorkProgram
        parameter: str
            параметр поля рабочей программы значение которого нужно вернуть

    Returns
    -------
        dict
            значение параметра для дисциплины
            {"Название дисциплины плана": {work_program_id: "Значение параметра"}}
    """
    programs_info = {}
    for disc in plan.disc_wp_match:
        disc_name = plan.discipline_name(disc)
        programs_info[disc_name] = {}
        if not plan.disc_wp_match[disc]:
            programs_info[disc_name]["none"] = "-->Программа отсутствует<--"
        else:
            for wp in plan.disc_wp_match[disc]:
                try:
                    field_data = work_program_get_parameter_info(
                        plan.work_programs_data[wp], parameter
                    )
                except ApeksParameterNonExistException:
                    await work_program_add_parameter(wp, parameter)
                    field_data = ""
                else:
                    field_data = "" if not field_data else field_data
                programs_info[disc_name][wp] = field_data
    return programs_info


def work_program_field_tb_table(parameter: str) -> str:
    """
    Определяет в какой таблице базы данных находится
    передаваемое имя поля рабочей программы.

    Parameters
    ----------
        parameter: str
            название поля рабочей программы

    Returns
    -------
        str
            имя_таблицы
    """
    if parameter in Apeks.MM_WORK_PROGRAMS or parameter == "department_data":
        table_name = Apeks.TABLES.get("mm_work_programs")
    elif parameter in Apeks.MM_SECTIONS:
        table_name = Apeks.TABLES.get("mm_sections")
    elif parameter in Apeks.MM_WORK_PROGRAMS_DATA:
        table_name = Apeks.TABLES.get("mm_work_programs_data")
    else:
        message = f'Передан неверный параметр: "{parameter}"'
        logging.error(message)
        raise ApeksWrongParameterException(message)
    return table_name


def work_program_get_parameter_info(wp_data: dict, parameter: str) -> str:
    """
    Возвращает значение передаваемого параметра поля рабочей программы.

    Parameters
    ----------
        wp_data: dict
            словарь с данными о рабочей программе
            (см. функцию 'get_work_programs_data')
        parameter: str
            параметр поля рабочей программы значение которого нужно вернуть

    Returns
    -------
        str
            значение параметра
    """

    if parameter in Apeks.MM_SECTIONS:
        try:
            field_data = wp_data["sections"][parameter]
        except KeyError:
            message = (
                f"Параметр '{parameter}' отсутствует в таблице: "
                f"{Apeks.TABLES.get('mm_sections')}"
            )
            logging.error(message)
            raise ApeksParameterNonExistException(message)
    elif parameter in Apeks.MM_WORK_PROGRAMS_DATA:
        field_id = Apeks.MM_WORK_PROGRAMS_DATA.get(parameter)
        try:
            field_data = wp_data["fields"][field_id]
        except KeyError:
            message = (
                f"Параметр '{parameter}' отсутствует в таблице: "
                f"{Apeks.TABLES.get('mm_work_programs_data')}"
            )
            logging.error(message)
            raise ApeksParameterNonExistException(message)
    elif parameter == "department_data":
        date_department = wp_data.get("date_department")
        document_department = wp_data.get("document_department")
        if date_department:
            d = date_department.split("-")
            date_department = f"{d[-1]}.{d[-2]}.{d[-3]}"
        else:
            date_department = "[Не заполнена]"
        if document_department is None:
            document_department = "[Отсутствует]"
        field_data = (
            f"Дата заседания кафедры: {date_department}\r\n"
            f"Протокол № {document_department}"
        )
    elif parameter in Apeks.MM_WORK_PROGRAMS:
        field_data = wp_data.get(parameter)
    else:
        message = f'Передан неверный параметр: "{parameter}"'
        logging.error(message)
        raise ApeksWrongParameterException(message)
    return field_data


async def create_work_program(
        curriculum_discipline_id: int | str,
        name: str,
        user_id: int | str,
        status: int | str = 0,
        table_name: str = Apeks.TABLES.get("mm_work_programs"),
) -> dict:
    """
    Создание пустой рабочей программы.

    Parameters
    ----------
        curriculum_discipline_id: int | str
            id учебной дисциплины
        name: str
            название
        user_id: int | str
            id пользователя владельца
        status: int | str
            статус утверждения
        table_name: str
            имя таблицы в БД
    """

    response = await api_add_to_db_table(
        table_name,
        curriculum_discipline_id=curriculum_discipline_id,
        name=name,
        user_id=user_id,
        status=status,
    )
    if response.get("status") == 1:
        logging.debug(
            f"Создана рабочая программа disc_id:{curriculum_discipline_id} {name}."
        )
    else:
        logging.debug(
            f"Рабочая программа disc_id:{curriculum_discipline_id} {name} не создана."
        )
    return response


async def work_program_add_parameter(
    work_program_id: int | str, parameter: str, load_data: str = ""
) -> dict:
    """
    Добавления пустого поля (parameter) в рабочую программу.

    Parameters
    ----------
        work_program_id: int | str
            id рабочей программы
        parameter: str
            id поля для загрузки данных
        load_data: str
            содержимое поля для загрузки. (необязательное)
    """
    table_name = work_program_field_tb_table(parameter)
    if table_name == Apeks.TABLES.get("mm_sections"):
        fields = {
            "work_program_id": work_program_id,
            Apeks.MM_SECTIONS.get(parameter): load_data,
        }
        response = await api_add_to_db_table(
            table_name,
            **fields,
        )
    elif table_name == Apeks.TABLES.get("mm_work_programs_data"):
        fields = {
            "work_program_id": work_program_id,
            "field_id": Apeks.MM_WORK_PROGRAMS_DATA.get(parameter),
            "data": "",
        }
        response = await api_add_to_db_table(
            table_name,
            **fields,
        )
    else:
        message = f"Передан неверный параметр '{parameter}' для загрузки в программу"
        logging.debug(message)
        raise ApeksWrongParameterException(message)
    logging.debug(f"В рабочую программу '{work_program_id}' добавлено "
                  f"поле '{parameter}' со значением '{load_data}'.")
    return response


async def work_programs_dates_update(
    work_program_id: int | str | tuple[int | str] | list[int | str],
    date_methodical: str,
    document_methodical: str,
    date_academic: str,
    document_academic: str,
    date_approval: str,
    table_name: str = Apeks.TABLES.get("mm_work_programs"),
):
    """
    Обновление информации о рассмотрении и утверждении рабочих программ.

    Parameters
    ----------
        work_program_id: int | str
            id рабочей программы
        date_methodical: str
            дата протокола заседания метод. совета
        document_methodical: str
            номер протокола заседания кафедры
        date_academic: str
            дата протокола заседания ученого совета
        document_academic: str
            номер протокола заседания ученого совета
        date_approval: str
            дата утверждения
        table_name: str
            имя таблицы в БД
    """
    filters = {
        "id": work_program_id,
    }
    fields = {
        "date_methodical": date_methodical,
        "document_methodical": document_methodical,
        "date_academic": date_academic,
        "document_academic": document_academic,
        "date_approval": date_approval,
    }
    response = await api_edit_db_table(
        table_name,
        filters,
        fields,
    )
    logging.debug(f"В рабочих программах {work_program_id} обновлены поля {fields}.")
    return response


async def edit_work_programs_data(
    work_program_id: int | str | tuple[int | str] | list[int | str], **kwargs
):
    """
    Редактирование информации в рабочих программах.

    Parameters
    ----------
        work_program_id: int | str
            id рабочей программы
    """
    payload = {
        Apeks.TABLES.get("mm_work_programs"): {
            "filters": {"id": work_program_id},
            "fields": {},
        },
        Apeks.TABLES.get("mm_sections"): {
            "filters": {"work_program_id": work_program_id},
            "fields": {},
        },
        Apeks.TABLES.get("mm_competency_levels"): {
            "filters": {"work_program_id": work_program_id, "level": 1},
            "fields": {},
        },
        Apeks.TABLES.get("mm_work_programs_data"): {},
    }

    if kwargs:
        for db_field, db_value in kwargs.items():
            table_name = work_program_field_tb_table(db_field)

            if table_name == Apeks.TABLES.get("mm_work_programs_data"):
                field_data = {
                    "filters": {
                        "work_program_id": work_program_id,
                        "field_id": Apeks.MM_WORK_PROGRAMS_DATA.get(db_field),
                    },
                    "fields": {"data": db_value},
                }
                payload[table_name][db_field] = field_data
            else:
                payload[table_name]["fields"][db_field] = db_value

    for table in payload:
        if table == Apeks.TABLES.get("mm_work_programs_data"):
            for field in payload[table]:
                filters = payload[table][field].get("filters")
                fields = payload[table][field].get("fields")
                logging.debug(
                    f"Переданы данные для обновления программ. {table, filters, fields}"
                )
                await api_edit_db_table(table, filters, fields)

        else:
            filters = payload[table].get("filters")
            fields = payload[table].get("fields")
            if fields:
                logging.debug(
                    f"Переданы данные для обновления программ. {table, filters, fields}"
                )
                await api_edit_db_table(table, filters, fields)
    return f"Данные успешно обновлены."
