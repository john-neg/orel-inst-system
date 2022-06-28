from __future__ import annotations

import logging

from app.common.classes.EducationPlan import EducationPlanWorkPrograms
from app.common.exceptions import (
    ApeksParameterNonExistException,
    ApeksWrongParameterException,
)
from app.common.func.api_delete import api_delete_from_db_table
from app.common.func.api_get import check_api_db_response, api_get_db_table
from app.common.func.api_post import api_add_to_db_table, api_edit_db_table
from app.common.func.app_core import data_processor
from app.common.func.education_plan import get_plan_control_works
from config import ApeksConfig as Apeks


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
                  "competency_levels": {level_val: {'id': level_id,
                                                    'work_program_id': id,
                                                    'abilities': value,
                                                    'control_type_id': value,
                                                    'knowledge': value,
                                                    'level1': value,
                                                    'level2': value,
                                                    'level3': value,
                                                    'ownerships': value
                                                    'semester_id': value},
                  "control_works": {"id": record_id,
                                    "curriculum_discipline_id": id,
                                    "control_type_id": id,
                                    "semester_id": id,
                                    "hours": val,
                                    "is_classroom": val}}
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
        wp_data[wp]["control_works"] = {}

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
            # Получение групп компетенций
            competencies_fields = await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("mm_work_programs_competencies_fields"),
                )
            )
            comp_fields = {}
            for field in competencies_fields:
                comp_fields[field.get("id")] = field.get("code")
            # Получение содержимого компетенций
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
            # Получение уровней сформированности компетенций
            comp_levels = await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("mm_competency_levels"),
                    work_program_id=wp_list,
                )
            )
            for level in comp_levels:
                wp_id = int(level.get("work_program_id"))
                level_val = int(level.get("level"))
                items = [item for item in [*level]]
                for item in items:
                    if not wp_data[wp_id]["competency_levels"].get(level_val):
                        wp_data[wp_id]["competency_levels"][level_val] = {}
                    wp_data[wp_id]["competency_levels"][level_val][item] = level.get(
                        item
                    )
            # Получение данных о завершающих обучение формах контроля для
            # проверки и создания уровней сформированности компетенций
            curriculum_discipline_id = set(
                [wp_data[wp].get("curriculum_discipline_id") for wp in wp_data]
            )
            control_works = await get_plan_control_works(
                curriculum_discipline_id=[*curriculum_discipline_id],
                control_type_id=(
                    Apeks.CONTROL_TYPE_ID.get("exam"),
                    Apeks.CONTROL_TYPE_ID.get("zachet"),
                    Apeks.CONTROL_TYPE_ID.get("zachet_mark"),
                    Apeks.CONTROL_TYPE_ID.get("final_att"),
                ),
            )
            for wp in wp_data:
                disc_id = int(wp_data[wp].get("curriculum_discipline_id"))
                if disc_id in control_works:
                    wp_data[wp]["control_works"] = control_works.get(disc_id)
    logging.debug("Передана информация о рабочих программах дисциплин {wp_list}")
    return wp_data


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
    message = f"Данные успешно обновлены."
    return message


async def load_lib_add_field(
    work_program_id: int | str,
    field_id: int | str,
    table_name: str = Apeks.TABLES.get("mm_work_programs_data"),
) -> dict:
    """
    Добавления пустого поля (field) списка литературы в рабочую программу.

    Parameters
    ----------
        work_program_id: int | str
            id рабочей программы
        field_id: int | str
            id поля для загрузки данных
        table_name: str
            имя таблицы в БД
    """
    response = await api_add_to_db_table(
        table_name,
        work_program_id=work_program_id,
        field_id=field_id,
        data="",
    )
    logging.debug(
        f"В рабочую программу '{work_program_id}' " f"добавлено поле '{field_id}'."
    )
    return response


async def load_lib_edit_field(
    work_program_id: int | str,
    field_id: int | str,
    load_data: str,
    check: int | str = 1,
    table_name: str = Apeks.TABLES.get("mm_work_programs_data"),
) -> dict:
    """
    Изменения поля поля (field) в рабочей программе.

    Parameters
    ----------
        work_program_id: int | str
            id рабочей программы
        field_id: int | str
            id поля для загрузки данных
        load_data: str
            данные для загрузки
        check: int | str
            отметка для статуса логического контроля проверки данных
            0 - не проверять поле, если нет данных
            по умолчанию - 1
        table_name: str
            имя таблицы в БД
    """
    if not load_data:
        load_data = ""
    filters = {
        "work_program_id": work_program_id,
        "field_id": field_id,
    }
    fields = {
        "data": load_data,
        "check": check,
    }
    response = await api_edit_db_table(
        table_name,
        filters,
        fields,
    )
    logging.debug(f"В рабочей программе {work_program_id} обновлено поле {field_id}.")
    return response


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
    logging.debug(
        f"В рабочую программу '{work_program_id}' добавлено "
        f"поле '{parameter}' со значением '{load_data}'."
    )
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
