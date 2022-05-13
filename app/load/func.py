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


