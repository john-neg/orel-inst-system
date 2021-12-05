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


def plan_curriculum_disciplines(education_plan_id):
    """Getting disciplines info as dict (disc_ID:[disc_code:disc_name])"""
    disciplines = {}
    plan_curriculum_disciplines = db_filter_req(
        "plan_curriculum_disciplines", "education_plan_id", education_plan_id
    )
    for disc in plan_curriculum_disciplines:
        if disc["level"] == "3":
            disciplines[disc["id"]] = [
                disc["code"],
                db_filter_req("plan_disciplines", "id", disc["discipline_id"])[0][
                    "name"
                ],
            ]
    return disciplines


def education_plans(education_specialty_id):
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
    for i in request.json()["data"]:
        plans[i.get("id")] = i.get("name")
    return plans
