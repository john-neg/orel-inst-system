import requests
from app.main.func import db_filter_req
from config import ApeksAPI


def get_disc_list():
    """Getting general disciplines list."""
    return db_filter_req("plan_disciplines", "level", 3)


def get_lessons(staff_id, month, year):
    """Getting staff lessons."""
    params = {
        "token": ApeksAPI.TOKEN,
        "staff_id": str(staff_id),
        "month": str(month),
        "year": str(year),
    }
    return requests.get(
        ApeksAPI.URL + "/api/call/schedule-schedule/staff", params=params
    ).json()["data"]["lessons"]


def get_edu_lessons(group_id, month, year):
    """Getting staff lessons."""
    params = {
        "token": ApeksAPI.TOKEN,
        "group_id": str(group_id),
        "month": str(month),
        "year": str(year),
    }
    return requests.get(
        ApeksAPI.URL + "/api/call/schedule-schedule/student", params=params
    ).json()["data"]["lessons"]
