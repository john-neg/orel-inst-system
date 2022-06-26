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
