from __future__ import annotations

import logging
from json import JSONDecodeError

import requests

from app.common.exceptions import ApeksApiException
from app.main.func import db_filter_req
from config import ApeksConfig as Apeks


def get_disc_list():
    """Получаем полный список дисциплин из справочника Апекс-ВУЗ"""
    return db_filter_req("plan_disciplines", "level", 3)


def apeks_api_get_staff_lessons(
    staff_id: int | str,
    month: int | str,
    year: int | str,
) -> dict:
    """
    Получаем список занятий по id преподавателя
    за определенный месяц и год.
    """
    endpoint = f"{Apeks.URL}/api/call/schedule-schedule/staff"
    params = {
        "token": Apeks.TOKEN,
        "staff_id": str(staff_id),
        "month": str(month),
        "year": str(year),
    }
    try:
        response = requests.get(endpoint, params=params)
    except ConnectionError as error:
        logging.error(f'Ошибка при запросе к API Апекс-ВУЗ: "{error}"')
    else:
        try:
            resp_json = response.json()
        except JSONDecodeError as error:
            logging.error(f'Ошибка конвертации ответа API Апекс-ВУЗ в JSON: "{error}"')
        else:
            logging.debug(
                f"Запрос успешно выполнен: staff_id:{staff_id}, month:{month}, year:{year}"
            )
            return resp_json


def apeks_api_check_staff_lessons(response: dict) -> list:
    """
    Проверяем ответ API Апекс-ВУЗ со списком занятий
    на наличие необходимых ключей и корректность данных.
    """
    if not isinstance(response, dict):
        message = "Ответ API содержит некорректный тип данных (dict expected)"
        raise TypeError(message)
    if "data" not in response:
        message = 'В ответе API отсутствует ключ "data"'
        raise ApeksApiException(message)
    data = response.get("data")
    if not isinstance(data, dict):
        message = "Ответ API содержит некорректный тип данных (dict expected)"
        raise TypeError(message)
    if "lessons" not in data:
        message = 'В ответе API отсутствует ключ "lessons"'
        raise ApeksApiException(message)
    lessons = data.get("lessons")
    if not isinstance(lessons, list):
        message = "Ответ API содержит некорректный тип данных (list expected)"
        raise TypeError(message)
    return lessons


# def get_edu_lessons(group_id, month, year):
#     """Getting group lessons."""
#     params = {
#         "token": Apeks.TOKEN,
#         "group_id": str(group_id),
#         "month": str(month),
#         "year": str(year),
#     }
#     return requests.get(
#         Apeks.URL + "/api/call/schedule-schedule/student", params=params
#     ).json()["data"]["lessons"]
#
#
from pprint import pprint
pprint(apeks_api_get_staff_lessons(32, 5, 2022))
