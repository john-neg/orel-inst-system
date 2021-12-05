from datetime import date
import requests
from app.main.func import db_filter_req
from config import ApeksAPI


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


def get_disc_list():
    """getting general disciplines list"""
    return db_filter_req("plan_disciplines", "level", 3)


def get_lessons(staff_id, month, year):
    """getting staff lessons"""
    params = {
        "token": ApeksAPI.TOKEN,
        "staff_id": str(staff_id),
        "month": str(month),
        "year": str(year),
    }
    return requests.get(
        ApeksAPI.URL + "/api/call/schedule-schedule/staff", params=params
    ).json()["data"]["lessons"]
