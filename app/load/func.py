from calendar import monthrange
from datetime import date
import requests
from app.main.func import db_request
from config import ApeksConfig as Apeks


def get_lessons(year, month):
    """List of lessons for selected month"""
    first_day = 1
    last_day = monthrange(year, month)[1]

    params = {
        "token": Apeks.TOKEN,
        "table": "schedule_day_schedule_lessons",
        "filter": f"date between '{date(year, month, first_day).isoformat()}' "
                  f"and '{date(year, month, last_day).isoformat()}'",
    }
    resp = requests.get(
        Apeks.URL + "/api/call/system-database/get", params=params
    )
    return resp.json()["data"]


async def lessons_staff():
    """
    Get staff for lesson_id
    {lesson_id:staff_id}.
    """
    staff = {}
    resp = await db_request("schedule_day_schedule_lessons_staff")
    for less in resp:
        if less.get("lesson_id") in staff:
            staff[less.get("lesson_id")].append(int(less.get("staff_id")))
        else:
            staff[less.get("lesson_id")] = [int(less.get("staff_id"))]
    return staff


async def load_subgroups():
    """
    Get group_id for subgroup_id
    {subgroup_id:group_id}.
    """
    subgroups = {}
    resp = await db_request("load_subgroups")
    for sub in resp:
        subgroups[sub.get("id")] = sub
    return subgroups


async def load_groups():
    """
    Get group info by group_id
    {id:[{}].
    """
    groups = {}
    resp = await db_request("load_groups")
    for group in resp:
        groups[group.get("id")] = group
    return groups


async def plan_education_plans_education_forms():
    """
    Get education_form_id info by education_plan_id
    {education_plan_id:education_form_id}.
    """
    education_forms = {}
    resp = await db_request("plan_education_plans_education_forms")
    for plan in resp:
        education_forms[plan.get("education_plan_id")] = plan.get("education_form_id")
    return education_forms


async def plan_education_plans():
    """
    Get plan info by plan_id
    {id:[{}].
    """
    education_plans = {}
    resp = await db_request("plan_education_plans")
    for plan in resp:
        education_plans[plan.get("id")] = plan
    return education_plans


def get_lesson_type(lesson):
    """Распределение типов занятий и контролей по группам."""
    if lesson.get("class_type_id") == str(Apeks.CLASS_TYPE_ID.get("lecture")):
        l_type = "lecture"
    elif lesson.get("class_type_id") == str(Apeks.CLASS_TYPE_ID.get("seminar")):
        l_type = "seminar"
    elif (
        lesson.get("class_type_id") == str(Apeks.CLASS_TYPE_ID.get("prakt"))
        or lesson.get("control_type_id")
        == str(Apeks.CONTROL_TYPE_ID.get("in_control"))
        or lesson.get("control_type_id")
        == str(Apeks.CONTROL_TYPE_ID.get("out_control"))
    ):
        l_type = "pract"
    elif lesson.get("control_type_id") == str(Apeks.CONTROL_TYPE_ID.get("group_cons")):
        l_type = "group_cons"
    elif (
        lesson.get("control_type_id") == str(Apeks.CONTROL_TYPE_ID.get("zachet"))
        or lesson.get("control_type_id")
        == str(Apeks.CONTROL_TYPE_ID.get("zachet_mark"))
        or lesson.get("control_type_id")
        == str(Apeks.CONTROL_TYPE_ID.get("itog_kontr"))
    ):
        l_type = "zachet"
        # Зачет, зачет с оценкой, итоговая письменная аудиторная к/р
    elif lesson.get("control_type_id") == str(
        Apeks.CONTROL_TYPE_ID.get("exam")
    ) or lesson.get("control_type_id") == str(
        Apeks.CONTROL_TYPE_ID.get("kandidat_exam")
    ):
        l_type = "exam"
        # Экзамен
    elif lesson.get("control_type_id") == str(Apeks.CONTROL_TYPE_ID.get("final_att")):
        l_type = "final_att"
        # Итоговая аттестация
    else:
        l_type = None
    return l_type


def get_student_type(lesson):
    if (
        lesson.get("education_form_id") == str(Apeks.EDUCATION_FORM_ID.get("prof_pod"))
        or lesson.get("discipline_id") == "549"
    ):
        s_type = "prof_p"  # проф подготовка (+ костыль ПП Цифр. грамотность - id - 549)
    elif lesson.get("education_form_id") == str(
        Apeks.EDUCATION_FORM_ID.get("ochno")
    ) and (
        lesson.get("education_level_id") == str(Apeks.EDUCATION_LEVEL_ID.get("bak"))
        or lesson.get("education_level_id")
        == str(Apeks.EDUCATION_LEVEL_ID.get("spec"))
    ):
        s_type = "och"  # очно, бакалавр или специалитет
    elif lesson.get("education_form_id") == str(
        Apeks.EDUCATION_FORM_ID.get("zaochno")
    ) and (
        lesson.get("education_level_id") == str(Apeks.EDUCATION_LEVEL_ID.get("bak"))
        or lesson.get("education_level_id")
        == str(Apeks.EDUCATION_LEVEL_ID.get("spec"))
    ):
        s_type = "zo_high"  # заочно, бакалавр или специалитет
    elif lesson.get("education_form_id") == str(
        Apeks.EDUCATION_FORM_ID.get("zaochno")
    ) and lesson.get("education_level_id") == str(Apeks.EDUCATION_LEVEL_ID.get("spo")):
        s_type = "zo_mid"  # заочно, среднее
    elif lesson.get("education_level_id") == str(Apeks.EDUCATION_LEVEL_ID.get("adj")):
        s_type = "adj"  # адъюнктура
    elif lesson.get("education_form_id") == str(Apeks.EDUCATION_FORM_ID.get("dpo")):
        s_type = "dpo"  # дополнительное проф образование
    else:
        s_type = None
    return s_type
