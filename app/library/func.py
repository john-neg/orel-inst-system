import requests
from openpyxl import load_workbook
from app.main.func import xlsx_iter_rows, xlsx_normalize
from config import ApeksAPI


def library_file_processing(filename):
    """Обработка загруженного файла c литературой (to dict without first string)"""
    wb = load_workbook(filename)
    ws = wb.active
    replace_dict = {"  ": " ", "–": "-", "\t": ""}
    xlsx_normalize(ws, replace_dict)
    liblist = list(xlsx_iter_rows(ws))
    del liblist[0]
    lib_dict = {}
    for lib in liblist:
        lib_dict[lib[0]] = []
        for i in range(1, len(lib)):
            lib_dict[lib[0]].append(lib[i])
    return lib_dict


def load_bibl(work_program_id, field_id, load_data):
    """Загрузка Литетратуры в программу (field_id = 1-осн, 2-доп, 3-науч прод)"""
    params = {"token": ApeksAPI.TOKEN}
    data = {
        "table": "mm_work_programs_data",
        "filter[work_program_id]": work_program_id,
        "filter[field_id]": field_id,
        "fields[data]": load_data,
    }
    requests.post(ApeksAPI.URL + "/api/call/system-database/edit", params=params, data=data)


def add_bibl_field(work_program_id, field_id):
    """Добавление полей в рабочую программу в случае их отсутствия"""
    params = {"token": ApeksAPI.TOKEN}
    data = {
        "table": "mm_work_programs_data",
        "fields[work_program_id]": work_program_id,
        "fields[field_id]": field_id,
        "fields[data]": "",
    }
    requests.post(ApeksAPI.URL + "/api/call/system-database/add", params=params, data=data)
