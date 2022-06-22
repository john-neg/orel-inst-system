from __future__ import annotations

import logging
from json import JSONDecodeError

import httpx

from app.common.exceptions import ApeksWrongParameterException
from app.common.func.app_core import work_program_field_tb_table
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
        table_name: str
            имя_таблицы
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


async def load_lib_add_field(
        work_program_id: int | str,
        field_id: int | str,
        table_name: str = Apeks.TABLES.get("mm_work_programs_data")
) -> dict:
    """
    Добавления пустого поля (field) списка литературы в рабочую программу.

    Parameters
    ----------
        work_program_id: int | str
            id рабочей программы
        field_id: int | str
            id поля для загрузки данных
        table_name: str
            имя таблицы в БД
    """
    response = await api_add_to_db_table(
        table_name,
        work_program_id=work_program_id,
        field_id=field_id,
        data="",
    )
    logging.debug(f"В рабочую программу '{work_program_id}' добавлено поле '{field_id}'.")
    return response


async def plan_competency_add(
        education_plan_id: int | str,
        code: str,
        description: str,
        left_node: int | str,
        right_node: int | str,
        level: int | str = 1,
        table_name: str = Apeks.TABLES.get("plan_competencies"),
) -> dict:
    """Добавление компетенции в учебный план.

    Parameters
    ----------
        education_plan_id: int | str
            id учебного плана
        code: str
            код компетенции
        description: str
            описание компетенции
        left_node: int | str
            начальная граница сортировки
        right_node: int | str
            конечная граница сортировки
        level: int | str = 1
            код уровня компетенции
        table_name: str
            имя таблицы в БД
    """

    response = await api_add_to_db_table(
        table_name,
        education_plan_id=education_plan_id,
        code=code,
        description=description,
        level=level,
        left_node=left_node,
        right_node=right_node,
    )
    if response.get("status") == 1:
        logging.debug(
            f"Добавлена компетенция {code} в учебный план: {education_plan_id}."
        )
    else:
        logging.debug(
            f"Компетенция {code} не добавлена в учебный план: {education_plan_id}."
        )
    return response


async def create_work_program(
        curriculum_discipline_id: int | str,
        name: str,
        user_id: int | str,
        status: int | str = 0,
        table_name: str = Apeks.TABLES.get("mm_work_programs"),
) -> dict:
    """
    Создание пустой рабочей программы.

    Parameters
    ----------
        curriculum_discipline_id: int | str
            id учебной дисциплины
        name: str
            название
        user_id: int | str
            id пользователя владельца
        status: int | str
            статус утверждения
        table_name: str
            имя таблицы в БД
    """

    response = await api_add_to_db_table(
        table_name,
        curriculum_discipline_id=curriculum_discipline_id,
        name=name,
        user_id=user_id,
        status=status,
    )
    if response.get("status") == 1:
        logging.debug(
            f"Создана рабочая программа disc_id:{curriculum_discipline_id} {name}."
        )
    else:
        logging.debug(
            f"Рабочая программа disc_id:{curriculum_discipline_id} {name} не создана."
        )
    return response


async def work_program_add_parameter(
    work_program_id: int | str, parameter: str, load_data: str = ""
) -> dict:
    """
    Добавления пустого поля (parameter) в рабочую программу.

    Parameters
    ----------
        work_program_id: int | str
            id рабочей программы
        parameter: str
            id поля для загрузки данных
        load_data: str
            содержимое поля для загрузки. (необязательное)
    """
    table_name = work_program_field_tb_table(parameter)
    if table_name == Apeks.TABLES.get("mm_sections"):
        fields = {
            "work_program_id": work_program_id,
            Apeks.MM_SECTIONS.get(parameter): load_data,
        }
        response = await api_add_to_db_table(
            table_name,
            fields,
        )
        print(response)
    elif table_name == Apeks.TABLES.get("mm_work_programs_data"):
        fields = {
            "work_program_id": work_program_id,
            "field_id": Apeks.MM_WORK_PROGRAMS_DATA.get(parameter),
            "data": "",
        }
        response = await api_add_to_db_table(
            table_name,
            **fields,
        )
    else:
        message = f"Передан неверный параметр '{parameter}' для загрузки в программу"
        logging.debug(message)
        raise ApeksWrongParameterException(message)
    logging.debug(f"В рабочую программу '{work_program_id}' добавлено "
                  f"поле '{parameter}' со значением '{load_data}'.")
    return response


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
    for db_field, db_value in fields.items():
        data[f"fields[{db_field}]"] = str(db_value)
    logging.debug(
        f"Переданы параметры для запроса 'api_edit_db_table': к таблице '{table_name}'"
    )
    return endpoint, params, data


async def load_lib_edit_field(
    work_program_id: int | str,
    field_id: int | str,
    load_data: str,
    check: int | str = 1,
    table_name: str = Apeks.TABLES.get("mm_work_programs_data"),
) -> dict:
    """
    Изменения поля поля (field) в рабочей программе.

    Parameters
    ----------
        work_program_id: int | str
            id рабочей программы
        field_id: int | str
            id поля для загрузки данных
        load_data: str
            данные для загрузки
        check: int | str
            отметка для статуса логического контроля проверки данных
            0 - не проверять поле, если нет данных
            по умолчанию - 1
        table_name: str
            имя таблицы в БД
    """
    if not load_data:
        load_data = ""
    filters = {
        "work_program_id": work_program_id,
        "field_id": field_id,
    }
    fields = {
        "data": load_data,
        "check": check,
    }
    response = await api_edit_db_table(
        table_name,
        filters,
        fields,
    )
    logging.debug(f"В рабочей программе {work_program_id} обновлено поле {field_id}.")
    return response


async def work_programs_dates_update(
    work_program_id: int | str | tuple[int | str] | list[int | str],
    date_methodical: str,
    document_methodical: str,
    date_academic: str,
    document_academic: str,
    date_approval: str,
    table_name: str = Apeks.TABLES.get("mm_work_programs"),
):
    """
    Обновление информации о рассмотрении и утверждении рабочих программ.

    Parameters
    ----------
        work_program_id: int | str
            id рабочей программы
        date_methodical: str
            дата протокола заседания метод. совета
        document_methodical: str
            номер протокола заседания кафедры
        date_academic: str
            дата протокола заседания ученого совета
        document_academic: str
            номер протокола заседания ученого совета
        date_approval: str
            дата утверждения
        table_name: str
            имя таблицы в БД
    """
    filters = {
        "id": work_program_id,
    }
    fields = {
        "date_methodical": date_methodical,
        "document_methodical": document_methodical,
        "date_academic": date_academic,
        "document_academic": document_academic,
        "date_approval": date_approval,
    }
    response = await api_edit_db_table(
        table_name,
        filters,
        fields,
    )
    logging.debug(f"В рабочих программах {work_program_id} обновлены поля {fields}.")
    return response


async def edit_work_programs_data(
    work_program_id: int | str | tuple[int | str] | list[int | str], **kwargs
):
    """
    Редактирование информации в рабочих программах.

    Parameters
    ----------
        work_program_id: int | str
            id рабочей программы
    """
    payload = {
        Apeks.TABLES.get("mm_work_programs"): {
            "filters": {"id": work_program_id},
            "fields": {},
        },
        Apeks.TABLES.get("mm_sections"): {
            "filters": {"work_program_id": work_program_id},
            "fields": {},
        },
        Apeks.TABLES.get("mm_competency_levels"): {
            "filters": {"work_program_id": work_program_id, "level": 1},
            "fields": {},
        },
        Apeks.TABLES.get("mm_work_programs_data"): {},
    }

    if kwargs:
        for db_field, db_value in kwargs.items():
            table_name = work_program_field_tb_table(db_field)

            if table_name == Apeks.TABLES.get("mm_work_programs_data"):
                field_data = {
                    "filters": {
                        "work_program_id": work_program_id,
                        "field_id": Apeks.MM_WORK_PROGRAMS_DATA.get(db_field),
                    },
                    "fields": {"data": db_value},
                }
                payload[table_name][db_field] = field_data
            else:
                payload[table_name]["fields"][db_field] = db_value

    for table in payload:
        if table == Apeks.TABLES.get("mm_work_programs_data"):
            for field in payload[table]:
                filters = payload[table][field].get("filters")
                fields = payload[table][field].get("fields")
                logging.debug(
                    f"Переданы данные для обновления программ. {table, filters, fields}"
                )
                await api_edit_db_table(table, filters, fields)

        else:
            filters = payload[table].get("filters")
            fields = payload[table].get("fields")
            if fields:
                logging.debug(
                    f"Переданы данные для обновления программ. {table, filters, fields}"
                )
                await api_edit_db_table(table, filters, fields)
    return f"Данные успешно обновлены."


# import asyncio
# from pprint import pprint
#
#
# async def main():
#     pprint(
#         await edit_work_programs_data(
#             [3229, 4308],
#             document_department=13,
#             knowledge="Знать",
#             course_works="Темы работ",
#             regulations="Нормативные акты",
#             software="Базы данных",
#             control_type_id=2,
#             purposes="Цели",
#             tasks="Задачи",
#             abilities="Умения",
#             reviewers_ext="Рецензенты",
#             test="test",
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
