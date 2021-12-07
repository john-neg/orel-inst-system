from datetime import date
import requests
from config import ApeksAPI, FlaskConfig


def allowed_file(filename):
    """Check if file extension in allowed list in Config"""
    return (
        "." in filename and filename.rsplit(".", 1)[1] in FlaskConfig.ALLOWED_EXTENSIONS
    )


def db_request(dbname):
    """DB request function without filter"""
    params = {"token": ApeksAPI.TOKEN, "table": dbname}
    response = requests.get(
        ApeksAPI.URL + "/api/call/system-database/get", params=params
    )
    return response.json()["data"]


def db_filter_req(dbname, sqltable, sqlvalue):
    """Filtered DB request (DB table, filter, value)"""
    params = {
        "token": ApeksAPI.TOKEN,
        "table": dbname,
        "filter[" + sqltable + "]": str(sqlvalue),
    }
    response = requests.get(
        ApeksAPI.URL + "/api/call/system-database/get", params=params
    )
    return response.json()["data"]


def get_active_staff_id():
    """getting Apeks ID of first active user (need to make general API data request)"""
    return db_filter_req("state_staff", "active", 1)[0]["id"]


def get_data(active_staff_id):
    """getting Apeks data about organisation structure"""
    params = {
        "token": ApeksAPI.TOKEN,
        "staff_id": active_staff_id,
        "month": date.today().strftime("%m"),
        "year": date.today().strftime("%Y"),
    }
    return requests.get(
        ApeksAPI.URL + "/api/call/schedule-schedule/staff", params=params
    ).json()["data"]


def education_specialty():
    """Getting education_speciality data"""
    payload = {"token": ApeksAPI.TOKEN, "table": "plan_education_specialties"}
    request = requests.get(
        ApeksAPI.URL + "/api/call/system-database/get", params=payload
    )
    specialties = {}
    for i in request.json()["data"]:
        specialties[i.get("id")] = i.get("name")
    return specialties


def education_plans(education_specialty_id, year=0):
    """Getting education plans with selected speciality"""
    payload = {
        "token": ApeksAPI.TOKEN,
        "table": "plan_education_plans",
        "filter[data_type]": "plan",
        "filter[education_specialty_id]": education_specialty_id,
        "filter[active]": "1",
    }
    request = requests.get(
        ApeksAPI.URL + "/api/call/system-database/get", params=payload
    )
    plans = {}
    if year == 0:
        for i in request.json()["data"]:
            plans[i.get("id")] = i.get("name")
        return plans
    else:
        for i in request.json()["data"]:
            if i.get("custom_start_year") == year:
                plans[i.get("id")] = i.get("name")
            elif i.get("custom_start_year") is None:
                if db_filter_req('plan_semesters', 'education_plan_id', i.get("id"))[0]['start_date'].split('-')[0] == year:
                    plans[i.get("id")] = i.get("name")
        return plans


def plan_curriculum_disciplines(education_plan_id):
    """Getting disciplines info as dict (disc_ID:[disc_code:disc_name])"""
    disciplines = {}
    resp = db_filter_req(
        "plan_curriculum_disciplines", "education_plan_id", education_plan_id
    )
    for disc in resp:
        if disc["level"] == "3":
            disciplines[disc["id"]] = [
                disc["code"],
                db_filter_req("plan_disciplines", "id", disc["discipline_id"])[0]["name"],
            ]
    return disciplines
