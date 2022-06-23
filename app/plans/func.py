from typing import Tuple, Dict, Any, List, Set

import requests
from openpyxl import load_workbook

from app.common.func.app_core import xlsx_iter_rows, xlsx_normalize
from app.main.func import db_filter_req
from common.classes.EducationPlan import EducationPlanCompetencies
from config import ApeksConfig as Apeks


def comps_file_processing(file: str) -> list:
    """Обработка загруженного файла c компетенциями.

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


def matrix_simple_file_processor(
    plan: EducationPlanCompetencies, file: str
) -> tuple[dict, set[Any], set[Any]]:
    """
    Проверка файла простой матрицы.

    Parameters
    ----------
        plan:
            экземпляр класса EducationPlanCompetencies
        file: str
            полный путь к файлу со списком компетенций

    Returns
    -------
        tuple[dict, set[Any], set[Any]]
            match_data: dict
                {"discipline_name": {"id": disc_id, "code": disc_code,
                "left_node": left_node, "comps": {"comp_name": comp_id}}.
            comp_not_in_plan: set
                список компетенций из файла, которые не найдены в плане.
            comp_not_in_file: set
                список компетенций из плана, которые не найдены в файле.
    """
    # Обработка файла
    wb = load_workbook(file)
    ws = wb.active
    file_list = list(xlsx_iter_rows(ws))
    file_dict = {}
    for line in file_list:
        disc_name = line[1]
        file_dict[disc_name] = []
        for i in range(2, len(line)):
            if line[i] == "+":
                comp_code = file_list[0][i]
                file_dict[disc_name].append(comp_code)
    # Компетенции
    plan_competencies = {
        comp.get("code"): key for key, comp in plan.plan_competencies.items()
    }
    file_comp: set = {file_list[0][i] for i in range(2, len(file_list[0]))}
    plan_comp: set = set(plan_competencies)
    comp_not_in_file = file_comp.difference(plan_comp)
    comp_not_in_plan = plan_comp.difference(file_comp)
    # Соответствие плана и файла
    disciplines = plan.plan_curriculum_disciplines
    match_data = {
        val.get("name"): {
            "id": key,
            "code": val.get("code"),
            "left_node": val.get("left_node"),
        }
        for key, val in disciplines.items()
        if val.get("level") == str(Apeks.DISC_LEVEL)
           and val.get("type") != str(Apeks.DISC_TYPE)
    }
    for disc in match_data:
        if disc in file_dict:
            match_data[disc]["comps"] = {}
            for comp in file_dict[disc]:
                if comp in plan_competencies:
                    match_data[disc]["comps"][comp] = plan_competencies[comp]
    return match_data, comp_not_in_plan, comp_not_in_file


# def matrix_simple_upload(self, filename):
#     """Загрузка связей из файла простой матрицы"""
#     wb = load_workbook(filename)
#     ws = wb.active
#     file_data = list(xlsx_iter_rows(ws))
#     load_data = {}
#     for disc in self.disciplines:
#         load_data[disc] = []
#         for line in file_data:
#             if self.disciplines[disc][1] == line[1]:
#                 for i in range(2, len(line)):
#                     if str(line[i]) == "+":
#                         load_data[disc].append(
#                             self.get_comp_id_by_code(file_data[0][i])
#                         )
#     for data in load_data:
#         if load_data.get(data):
#             for comp in load_data.get(data):
#                 if comp is not None:
#                     disciplines_comp_load(data, comp)







def disciplines_comp_load(curriculum_discipline_id, competency_id):
    """Загрузка связи дисциплины с компетенцией"""
    params = {"token": Apeks.TOKEN}
    data = {
        "table": "plan_curriculum_discipline_competencies",
        "fields[curriculum_discipline_id]": curriculum_discipline_id,
        "fields[competency_id]": competency_id,
    }
    requests.post(Apeks.URL + "/api/call/system-database/add", params=params, data=data)


def disciplines_wp_clean(work_program_id):
    """Удаление записей о компетенциях в РП"""
    params = {
        "token": Apeks.TOKEN,
        "table": "mm_work_programs_competencies_data",
        "filter[work_program_id]": work_program_id,
    }
    requests.delete(Apeks.URL + "/api/call/system-database/delete", params=params)


def disciplines_comp_del(curriculum_discipline_id):
    """Удаление связей дисциплины и компетенций"""
    params = {
        "token": Apeks.TOKEN,
        "table": "plan_curriculum_discipline_competencies",
        "filter[curriculum_discipline_id]": curriculum_discipline_id,
    }
    requests.delete(Apeks.URL + "/api/call/system-database/delete", params=params)


def comp_delete(education_plan_id):
    """Удаление компетенций из учебного плана"""
    data = db_filter_req("plan_competencies", "education_plan_id", education_plan_id)
    for i in range(len(data)):
        params = {
            "token": Apeks.TOKEN,
            "table": "plan_competencies",
            "filter[id]": data[i]["id"],
        }
        requests.delete(Apeks.URL + "/api/call/system-database/delete", params=params)


def create_wp(curriculum_discipline_id):
    """Создание программы"""
    params = {"token": Apeks.TOKEN}
    data = {
        "table": "mm_work_programs",
        "fields[curriculum_discipline_id]": curriculum_discipline_id,
        "fields[name]": get_wp_name(curriculum_discipline_id),
        "fields[user_id]": get_main_staff_id(curriculum_discipline_id),
    }
    requests.post(Apeks.URL + "/api/call/system-database/add", params=params, data=data)


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
