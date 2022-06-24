from __future__ import annotations

import logging

from openpyxl import load_workbook

from app.common.func.app_core import xlsx_iter_rows, xlsx_normalize
from common.func.api_post import api_add_to_db_table, api_edit_db_table
from config import ApeksConfig as Apeks


def library_file_processing(file: str) -> dict:
    """
    Обработка загруженного файла c данными об обеспечении.
    (словарь без первой строки файла).

    Parameters
    ----------
        file: str
            полный путь к файлу с обеспечением для дисциплины

    Returns
    -------
        dict
            {"Название дисциплины": ["данные об обеспечении"]}

    """
    wb = load_workbook(file)
    ws = wb.active
    replace_dict = {
        "  ": " ",
        "–": "-",
        "\t": "",
        "_x000D_": "",
        "None": "",
        "Нет программы": ""
    }
    ws = xlsx_normalize(ws, replace_dict)
    lib_list = list(xlsx_iter_rows(ws))
    del lib_list[0]
    lib_dict = {}
    for lib in lib_list:
        lib_dict[lib[0].strip()] = []
        for i in range(1, len(lib)):
            lib_dict[lib[0]].append(lib[i])
    return lib_dict


async def load_lib_add_field(
        work_program_id: int | str,
        field_id: int | str,
        table_name: str = Apeks.TABLES.get("mm_work_programs_data")
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
    logging.debug(f"В рабочую программу '{work_program_id}' добавлено поле '{field_id}'.")
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
