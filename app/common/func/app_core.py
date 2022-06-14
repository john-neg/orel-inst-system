from __future__ import annotations

import logging

from openpyxl import Workbook

from config import FlaskConfig, ApeksConfig as Apeks


def allowed_file(filename: str) -> bool:
    """Проверяет что расширение файла в списке разрешенных."""
    return (
        "." in filename and filename.rsplit(".", 1)[1] in FlaskConfig.ALLOWED_EXTENSIONS
    )


def data_processor(table_data: list, dict_key: str = "id") -> dict:
    """
    Преобразует полученные данные из таблиц БД Апекс-ВУЗ.

    Parameters
    ----------
        table_data: list
            данные таблицы, содержащей список словарей в формате JSON
        dict_key: str
            название поля значения которого станут ключами словаря
            по умолчанию - 'id'

    Returns
    -------
        dict
            {id: {keys: values}}.
    """
    data = {}
    for d_val in table_data:
        data[int(d_val.get(dict_key))] = d_val
    logging.debug(f"Обработаны данные. Ключ: {dict_key}")
    return data


def work_program_field_tb_table(field_name: str) -> str:
    """
    Определяет в какой таблице базы данных находится
    передаваемое имя поля рабочей программы.

    Parameters
    ----------
        field_name: str
            название поля рабочей программы

    Returns
    -------
        str
            имя_таблицы
    """
    if field_name in Apeks.MM_WORK_PROGRAMS:
        table_name = Apeks.TABLES.get("mm_work_programs")
    elif field_name in Apeks.MM_SECTIONS:
        table_name = Apeks.TABLES.get("mm_sections")
    elif field_name in Apeks.MM_COMPETENCY_LEVELS:
        table_name = Apeks.TABLES.get("mm_competency_levels")
    elif field_name in Apeks.MM_WORK_PROGRAMS_DATA:
        table_name = Apeks.TABLES.get("mm_work_programs_data")
    else:
        return "unknown_parameter"
    return table_name



def xlsx_iter_rows(worksheet: Workbook.active):
    """
    Чтение данных таблицы XLSX по рядам.

    Parameters
    ----------
        worksheet: Workbook.active
            активный лист таблицы
    """
    for row in worksheet.iter_rows():
        yield [cell.value for cell in row]


def xlsx_normalize(worksheet: Workbook.active, replace: dict):
    """
    Функция для замены символов в таблице.

    Parameters
    ----------
        worksheet: Workbook.active
            активный лист таблицы
        replace: dict
            словарь для замены {'изменяемое значение': 'новое значение'}

    Returns
    -------
        worksheet: Workbook.active
            измененный лист
    """
    for key, val in replace.items():
        for r in range(1, worksheet.max_row + 1):
            for c in range(1, worksheet.max_column + 1):
                s = str(worksheet.cell(r, c).value).strip()
                worksheet.cell(r, c).value = s.replace(key, val)
    return worksheet
