from calendar import monthrange
from datetime import date
import requests
from app.main.func import db_filter_req, db_request
from config import ApeksAPI


def get_lessons(year, month):
    """List of lessons for selected month"""
    first_day = 1
    last_day = monthrange(year, month)[1]

    params = {
        "token": ApeksAPI.TOKEN,
        "table": 'schedule_day_schedule_lessons',
        "filter": "date between '" + date(year, month, first_day).isoformat() + "' and '" + date(year, month, last_day).isoformat() + "'"
    }
    resp = requests.get(
        ApeksAPI.URL + "/api/call/system-database/get", params=params)
    return resp.json()['data']


def lessons_staff():
    """Get staff for lesson_id ( {lesson_id:staff_id} )"""
    lessons_staff = {}
    resp = db_request('schedule_day_schedule_lessons_staff')
    for less in resp:
        if less.get('lesson_id') in lessons_staff:
            lessons_staff[less.get('lesson_id')].append(less.get('staff_id'))
        else:
            lessons_staff[less.get('lesson_id')] = [less.get('staff_id')]
    return lessons_staff


def load_subgroups():
    """Get group_id for subgroup_id ( {subgroup_id:group_id} )"""
    subgroups = {}
    resp = db_request('load_subgroups')
    for sub in resp:
        subgroups[sub.get('id')] = sub.get('group_id')
    return subgroups


def load_groups():
    """Get group info by group_id ( {id:[{}] )"""
    groups = {}
    resp = db_request('load_groups')
    for group in resp:
        groups[group.get('id')] = group
    return groups


def plan_education_plans_education_forms():
    """Get education_form_id info by education_plan_id ( {education_plan_id:education_form_id} )"""
    education_forms = {}
    resp = db_request('plan_education_plans_education_forms')
    for plan in resp:
        education_forms[plan.get('education_plan_id')] = plan.get('education_form_id')
    return education_forms


def plan_education_plans():
    """Get plan info by plan_id ( {id:[{}] )"""
    education_plans = {}
    resp = db_request('plan_education_plans')
    for plan in resp:
        education_plans[plan.get('id')] = plan
    return education_plans


def get_lesson_type(lesson):
    if lesson.get("class_type_id") == "1":  # Лекция
        l_type = "lecture"
    elif lesson.get("class_type_id") == "2":  # Семинар
        l_type = "seminar"
    elif (
        lesson.get("class_type_id") == "3"
        or lesson.get("control_type_id") == "12"
        or lesson.get("control_type_id") == "13"
    ):  # П/з, входной, выходной контроль
        l_type = "pract"
    elif lesson.get("control_type_id") == "15":  # Консультации
        l_type = "group_cons"
    elif (
        lesson.get("control_type_id") == "2"
        or lesson.get("control_type_id") == "6"
        or lesson.get("control_type_id") == "10"
    ):  # Зачет, зачет с оценкой, итоговая письменная аудиторная к/р
        l_type = "zachet"
    elif lesson.get("control_type_id") == "1" or lesson.get("control_type_id") == "16":  # Экзамен
        l_type = "exam"
    elif lesson.get("control_type_id") == "14":  # Итоговая аттестация
        l_type = "final_att"
    else:
        l_type = None
    return l_type


def get_student_type(lesson):
    if lesson.get("education_form_id") == "1" and (
        lesson.get("education_level_id") == "3"
        or lesson.get("education_level_id") == "5"
    ):  # Очно, бакалавр или специалитет
        s_type = "och"
    elif lesson.get("education_form_id") == "3" and (
        lesson.get("education_level_id") == "3"
        or lesson.get("education_level_id") == "5"
    ):  # заочно, бакалавр или специалитет
        s_type = "zo_high"
    elif (
        lesson.get("education_form_id") == "3"
        and lesson.get("education_level_id") == "2"
    ):  # зачно, сренднее
        s_type = "zo_mid"
    elif lesson.get("education_level_id") == "7":  # адъюнктура
        s_type = "adj"
    elif lesson.get("education_form_id") == "7":  # проф подготовка
        s_type = "prof_p"
    elif lesson.get("education_form_id") == "5":  # дополнительное проф образование
        s_type = "dpo"
    else:
        s_type = None
    return s_type
