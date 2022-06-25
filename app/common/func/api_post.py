from __future__ import annotations

import logging
from json import JSONDecodeError

import httpx

from common.exceptions import ApeksApiException
from config import ApeksConfig as Apeks


def api_post_request_handler(func):
    """Декоратор для функций, отправляющих POST запрос к API Апекс-ВУЗ"""

    async def wrapper(*args, **kwargs) -> dict:
        endpoint, params, data = await func(*args, **kwargs)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(endpoint, params=params, data=data)
                response.raise_for_status()
            except httpx.RequestError as exc:
                logging.error(
                    f"{func.__name__}. Ошибка при запросе к "
                    f"API Апекс-ВУЗ: {exc.request.url!r}."
                )
            except httpx.HTTPStatusError as exc:
                logging.error(
                    f"{func.__name__}. Произошла ошибка "
                    f"{exc.response.status_code} во время "
                    f"запроса {exc.request.url!r}."
                )
            else:
                try:
                    resp_json = response.json()
                    del params["token"]
                    if resp_json.get("status") == 1:
                        logging.debug(
                            f"{func.__name__}. Запрос успешно выполнен, данные "
                            f"({resp_json.get('data')}) добавлены / обновлены: {data}"
                        )
                        return resp_json
                    else:
                        logging.debug(
                            f"{func.__name__}. Произошла ошибка: "
                            f"{resp_json.get('message')}"
                        )
                        return resp_json
                except JSONDecodeError as error:
                    logging.error(
                        f"{func.__name__}. Ошибка конвертации "
                        f"ответа API Апекс-ВУЗ в JSON: '{error}'"
                    )

    return wrapper


@api_post_request_handler
async def api_add_to_db_table(
    table_name: str, url: str = Apeks.URL, token: str = Apeks.TOKEN, **kwargs
):
    """
    Запрос к API для добавления информации в таблицу базы данных Апекс-ВУЗ.

    Parameters
    ----------


        url: str
            URL сервера
        token: str
            токен для API
        **kwargs: int | str
            'field_name=value' название_поля=значение, которые нужно добавить
    """
    endpoint = f"{url}/api/call/system-database/add"
    params = {"token": token}
    data = {"table": table_name}
    for db_field, db_value in kwargs.items():
        data[f"fields[{db_field}]"] = str(db_value)
    logging.debug(
        f"Переданы параметры для запроса 'api_add_to_db_table': к таблице {table_name}"
    )
    return endpoint, params, data


@api_post_request_handler
async def api_edit_db_table(
    table_name: str,
    filters: dict[int | str : int | str | tuple[int | str] | list[int | str]],
    fields: dict[int | str : int | str],
    url: str = Apeks.URL,
    token: str = Apeks.TOKEN,
):
    """
    Запрос к API для изменения информации в таблице базы данных Апекс-ВУЗ.

    Parameters
    ----------
        table_name: str
            имя_таблицы
        filters: dict[int | str: int | str | tuple[int | str] | list[int | str]]
            фильтры для запроса
        fields: dict[int | str: int | str]
            изменяемые поля
        url: str
            URL сервера
        token: str
            токен для API
    """
    endpoint = f"{url}/api/call/system-database/edit"
    params = {"token": token}
    data = {"table": table_name}
    for db_field, db_value in filters.items():
        if type(db_value) in (int, str):
            values = str(db_value)
        else:
            values = [str(val) for val in db_value]
        data[f"filter[{db_field}][]"] = values
        if not values:
            message = "Для фильтра операции 'edit' передан параметр с пустым значением"
            logging.error(message)
            raise ApeksApiException(message)
    for db_field, db_value in fields.items():
        data[f"fields[{db_field}]"] = str(db_value)
    logging.debug(
        f"Переданы параметры для запроса 'api_edit_db_table': к таблице '{table_name}'"
    )
    return endpoint, params, data
