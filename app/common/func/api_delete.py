from __future__ import annotations

import logging
from json import JSONDecodeError

import httpx

from config import ApeksConfig as Apeks


def api_delete_request_handler(func):
    """Декоратор для функций, отправляющих DELETE запрос к API Апекс-ВУЗ"""

    async def wrapper(*args, **kwargs) -> dict:
        endpoint, params = await func(*args, **kwargs)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(endpoint, params=params)
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
                    if resp_json.get('status') == 1:
                        logging.debug(
                            f"{func.__name__}. Запрос успешно выполнен: "
                            f"{params}. Данные удалены: {resp_json.get('data')}"
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


@api_delete_request_handler
async def api_delete_from_db_table(
    table_name: str, url: str = Apeks.URL, token: str = Apeks.TOKEN, **kwargs
):
    endpoint = f"{url}/api/call/system-database/delete"
    params = {"token": token, "table": table_name}
    for db_field, db_value in kwargs.items():
        params[f"filter[{db_field}][]"] = str(db_value)
    return endpoint, params


# import asyncio
# from pprint import pprint
#
#
# async def main():
#     pprint(
#         await api_delete_from_db_table(
#             'mm_work_programs',
#             id=4313,
#         )
#     )
# # pprint(await get_plan_curriculum_disciplines(
# #     education_plan_id=133,
# # ))
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
#     loop.close()