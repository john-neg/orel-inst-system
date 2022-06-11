import requests
from openpyxl import load_workbook

from app.main.func import db_filter_req
from app.common.func.app_core import xlsx_iter_rows, xlsx_normalize
from config import ApeksConfig as Apeks


def disciplines_comp_load(curriculum_discipline_id, competency_id):
    """Загрузка связи дисциплины с компетенцией"""
    params = {"token": Apeks.TOKEN}
    data = {
        "table": "plan_curriculum_discipline_competencies",
        "fields[curriculum_discipline_id]": curriculum_discipline_id,
        "fields[competency_id]": competency_id,
    }
    requests.post(
        Apeks.URL + "/api/call/system-database/add", params=params, data=data
    )


def disciplines_wp_clean(work_program_id):
    """Удаление записей о компетенциях в РП"""
    params = {
        "token": Apeks.TOKEN,
        "table": "mm_work_programs_competencies_data",
        "filter[work_program_id]": work_program_id,
    }
    requests.delete(
        Apeks.URL + "/api/call/system-database/delete", params=params
    )


def disciplines_comp_del(curriculum_discipline_id):
    """Удаление связей дисциплины и компетенций"""
    params = {
        "token": Apeks.TOKEN,
        "table": "plan_curriculum_discipline_competencies",
        "filter[curriculum_discipline_id]": curriculum_discipline_id,
    }
    requests.delete(
        Apeks.URL + "/api/call/system-database/delete", params=params
    )


def comp_delete(education_plan_id):
    """Удаление компетенций из учебного плана"""
    data = db_filter_req("plan_competencies", "education_plan_id", education_plan_id)
    for i in range(len(data)):
        params = {
            "token": Apeks.TOKEN,
            "table": "plan_competencies",
            "filter[id]": data[i]["id"],
        }
        requests.delete(
            Apeks.URL + "/api/call/system-database/delete", params=params
        )


def comps_file_processing(filename):
    """Обработка загруженного файла c компетенциями (to list without first string)"""
    wb = load_workbook(filename)
    ws = wb.active

    replace_dict = {"  ": " ", "–": "-", ". - ": " - ", "K": "К", "O": "О"}
    ws = xlsx_normalize(ws, replace_dict)

    comps = list(xlsx_iter_rows(ws))
    del comps[0]
    return comps


def create_wp(curriculum_discipline_id):
    """Создание программы"""
    params = {"token": Apeks.TOKEN}
    data = {
        "table": "mm_work_programs",
        "fields[curriculum_discipline_id]": curriculum_discipline_id,
        "fields[name]": get_wp_name(curriculum_discipline_id),
        "fields[user_id]": get_main_staff_id(curriculum_discipline_id),
    }
    requests.post(
        Apeks.URL + "/api/call/system-database/add", params=params, data=data
    )


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
