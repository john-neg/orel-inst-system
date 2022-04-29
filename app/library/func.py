import requests
from openpyxl import load_workbook
from app.main.func import xlsx_iter_rows, xlsx_normalize
from config import FlaskConfig as Config


def library_file_processing(filename) -> dict:
    """
    Обработка загруженного файла c литературой
    (словарь без первой строки файла).
    """
    wb = load_workbook(filename)
    ws = wb.active
    replace_dict = {
        "  ": " ",
        "–": "-",
        "\t": "",
        "_x000D_": "",
        "None": "",
        "Нет программы": ""
    }
    xlsx_normalize(ws, replace_dict)
    lib_list = list(xlsx_iter_rows(ws))
    del lib_list[0]
    lib_dict = {}
    for lib in lib_list:
        lib_dict[lib[0]] = []
        for i in range(1, len(lib)):
            lib_dict[lib[0]].append(lib[i])
    return lib_dict


def load_bibl(work_program_id, field_id, load_data):
    """
    Загрузка Литературы в программу
    (field_id = 1-осн, 2-доп...).
    """
    params = {"token": Config.APEKS_TOKEN}
    data = {
        "table": "mm_work_programs_data",
        "filter[work_program_id]": work_program_id,
        "filter[field_id]": field_id,
        "fields[data]": load_data,
    }
    requests.post(
        Config.APEKS_URL + "/api/call/system-database/edit", params=params, data=data
    )
