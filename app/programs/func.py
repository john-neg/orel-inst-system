import requests
from app.main.func import db_filter_req, plan_curriculum_disciplines
from config import ApeksAPI


def wp_update_list(education_plan_id):
    """Getting ID and names of plan work programs"""
    disciplines = plan_curriculum_disciplines(education_plan_id)
    workprogram = {}
    not_exist = {}
    for disc in disciplines:
        response = db_filter_req("mm_work_programs", "curriculum_discipline_id", disc)
        if response:
            wp_id = response[0]["id"]
            wp_name = response[0]["name"]
            workprogram[wp_id] = wp_name
        else:
            not_exist[disc] = disciplines[str(disc)]
    return workprogram, not_exist


def wp_dates_update(
    wp_id,
    date_methodical,
    document_methodical,
    date_academic,
    document_academic,
    date_approval,
):
    """Update workprogram signature dates"""
    params = {'token': ApeksAPI.TOKEN}
    data = {
        "table": "mm_work_programs",
        "filter[id]": wp_id,
        "fields[date_methodical]": date_methodical,
        "fields[document_methodical]": document_methodical,
        "fields[date_academic]": date_academic,
        "fields[document_academic]": document_academic,
        "fields[date_approval]": date_approval,
    }
    send = requests.post(
        ApeksAPI.URL + "/api/call/system-database/edit", params=params, data=data)
    return send.json()["data"]


def plan_department_disciplines(education_plan_id, department_id):
    """Getting department disciplines info as dict (disc_ID:[disc_code:disc_name])"""
    disciplines = {}
    resp = db_filter_req(
        "plan_curriculum_disciplines", "education_plan_id", education_plan_id
    )
    for disc in resp:
        if disc["level"] == "3" and disc["department_id"] == str(department_id):
            disciplines[disc["id"]] = [
                disc["code"],
                db_filter_req("plan_disciplines", "id", disc["discipline_id"])[0]["name"],
            ]
    return disciplines
