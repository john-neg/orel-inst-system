import requests
from openpyxl import load_workbook
from app.main.func import db_filter_req
from config import ApeksAPI, FlaskConfig


def disciplines_comp_load(curriculum_discipline_id, competency_id):
    """Загрузка связи дисциплины с компетенцией"""
    params = {"token": ApeksAPI.TOKEN}
    data = {
        "table": "plan_curriculum_discipline_competencies",
        "fields[curriculum_discipline_id]": curriculum_discipline_id,
        "fields[competency_id]": competency_id,
    }
    requests.post(
        ApeksAPI.URL + "/api/call/system-database/add", params=params, data=data
    )


def disciplines_wp_clean(work_program_id):
    """Удаление записей о компетенциях в РП"""
    params = {
        "token": ApeksAPI.TOKEN,
        "table": "mm_work_programs_competencies_data",
        "filter[work_program_id]": work_program_id,
    }
    requests.delete(ApeksAPI.URL + "/api/call/system-database/delete", params=params)


def disciplines_comp_del(curriculum_discipline_id):
    """Удаление связей дисциплины и компетенций"""
    params = {
        "token": ApeksAPI.TOKEN,
        "table": "plan_curriculum_discipline_competencies",
        "filter[curriculum_discipline_id]": curriculum_discipline_id,
    }
    requests.delete(ApeksAPI.URL + "/api/call/system-database/delete", params=params)


def comp_delete(education_plan_id):
    """Удаление компетенций из учебного плана"""
    data = db_filter_req("plan_competencies", "education_plan_id", education_plan_id)
    for i in range(len(data)):
        params = {
            "token": ApeksAPI.TOKEN,
            "table": "plan_competencies",
            "filter[id]": data[i]["id"],
        }
        requests.delete(
            ApeksAPI.URL + "/api/call/system-database/delete", params=params
        )


def comps_file_processing(filename):
    """Обработка загруженного файла"""
    wb = load_workbook(filename)
    ws = wb.active

    def iter_rows(ws):
        for row in ws.iter_rows():
            yield [cell.value for cell in row]

    comps = list(iter_rows(ws))
    del comps[0]
    return comps
