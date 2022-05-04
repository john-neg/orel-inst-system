from __future__ import annotations

import logging
from json import JSONDecodeError

import requests

from config import ApeksConfig as Apeks

from pprint import pprint


def apeks_api_get_lessons(
        staff_id: int | str,
        month: int | str,
        year: int | str,
) -> list:
    """
    Получаем список занятий по id преподавателя
    за определенный месяц и год.
    """
    params = {
        "token": Apeks.TOKEN,
        "staff_id": str(staff_id),
        "month": str(month),
        "year": str(year),
    }
    try:
        response = requests.get(
            Apeks.URL + "/api/call/schedule-schedule/staff",
            params=params,
        )
    except ConnectionError as error:
        logging.error(f'Ошибка при запросе к API Апекс-ВУЗ: "{error}"')
    else:
        try:
            resp_json = response.json()
        except JSONDecodeError as error:
            logging.error(f'Ошибка конвертации ответа API Апекс-ВУЗ в JSON: "{error}"')
        else:
            return resp_json #["data"]["lessons"]


pprint(apeks_api_get_lessons(33, 5, 2022))