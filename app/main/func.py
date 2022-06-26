import requests

from config import ApeksConfig as Apeks


def db_request(table_name):
    """DB request function without filter."""
    params = {"token": Apeks.TOKEN, "table": table_name}
    response = requests.get(
        Apeks.URL + "/api/call/system-database/get", params=params
    )
    return response.json()["data"]


def db_filter_req(table_name, sql_field, sql_value):
    """Filtered DB request (DB table, filter, value)."""
    params = {
        "token": Apeks.TOKEN,
        "table": table_name,
        "filter[" + sql_field + "]": str(sql_value),
    }
    response = requests.get(
        Apeks.URL + "/api/call/system-database/get", params=params
    )
    return response.json()["data"]


def plan_curriculum_disciplines(education_plan_id):
    """Getting plan disciplines info as dict (disc_ID:[disc_code:disc_name]).
    Async ЗАМЕНА ЕСТЬ В common
    """

    def disc_name(discipline_id):
        for discipline in disc_list:
            if discipline.get("id") == discipline_id:
                return discipline["name"]

    disciplines = {}
    disc_list = db_request("plan_disciplines")
    plan_disc = db_filter_req(
        "plan_curriculum_disciplines", "education_plan_id", education_plan_id
    )
    for disc in plan_disc:
        if (
                disc["level"] == "3" and not disc["type"] == "16"
        ):  # type 16 - группы дисциплин
            disciplines[disc["id"]] = [disc["code"], disc_name(disc["discipline_id"])]
    return disciplines


