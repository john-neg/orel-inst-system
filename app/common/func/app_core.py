from __future__ import annotations

import logging

from openpyxl import Workbook

from app.common.exceptions import ApeksWrongParameterException, \
    ApeksParameterNonExistException
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
    if parameter in Apeks.MM_WORK_PROGRAMS:
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
            message = (f"Параметр '{parameter}' отсутствует в таблице: "
                       f"{Apeks.TABLES.get('mm_sections')}")
            logging.error(message)
            raise ApeksParameterNonExistException(message)
    elif parameter in Apeks.MM_WORK_PROGRAMS_DATA:
        field_id = Apeks.MM_WORK_PROGRAMS_DATA.get(parameter)
        try:
            field_data = wp_data["fields"][field_id]
        except KeyError:
            message = (f"Параметр '{parameter}' отсутствует в таблице: "
                       f"{Apeks.TABLES.get('mm_work_programs_data')}")
            logging.error(message)
            raise ApeksParameterNonExistException(message)
    elif parameter == "department_data":
        date_department = wp_data.get('date_department')
        document_department = wp_data.get('document_department')
        if date_department:
            d = date_department.split("-")
            date_department = f"{d[-1]}.{d[-2]}.{d[-3]}"
        else:
            date_department = "[Не заполнена]"
        if document_department is None:
            document_department = "[Отсутствует]"
        field_data = (f"Дата заседания кафедры: {date_department}\r\n"
                      f"Протокол № {document_department}")
    elif parameter in Apeks.MM_WORK_PROGRAMS:
        field_data = wp_data.get(parameter)
    else:
        message = f'Передан неверный параметр: "{parameter}"'
        logging.error(message)
        raise ApeksWrongParameterException(message)
    return field_data


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
