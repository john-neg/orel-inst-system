from __future__ import annotations

import logging

from config import ApeksConfig as Apeks
from .api_delete import api_delete_from_db_table
from .api_get import check_api_db_response, api_get_db_table
from .api_post import api_add_to_db_table
from .app_core import data_processor


async def get_education_plans(
    education_specialty_id: int | str, year: int | str = 0
) -> dict:
    """
    Получение списка планов по указанной специальности.

    Parameters
    ----------
        education_specialty_id: int | str
            id специальности из таблицы 'plan_education_specialties'.
        year: int | str
            год начала обучения по плану (по умолчанию 0 = все)

    Returns
    ----------
        dict
            {plan_id: plan_name}
    """

    education_plans = data_processor(
        await check_api_db_response(
            await api_get_db_table(
                Apeks.TABLES.get("plan_education_plans"),
                data_type="plan",
                education_specialty_id=education_specialty_id,
                active="1",
            )
        )
    )

    plans = {}
    if year == 0:
        for plan in education_plans:
            plans[plan] = education_plans[plan].get("name")
    else:
        plans_dates = data_processor(
            await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("plan_semesters"),
                    education_plan_id=[*education_plans],
                    # Параметры для получения года начала обучения
                    course="1",
                    semester="1",
                )
            ),
            "education_plan_id",
        )
        for plan in education_plans:
            if education_plans[plan].get("custom_start_year") == str(year):
                plans[plan] = education_plans[plan].get("name")
            elif education_plans[plan].get("custom_start_year") is None:
                if plans_dates.get(plan).get("start_date").split("-")[0] == str(year):
                    plans[plan] = education_plans[plan].get("name")
    logging.debug(
        "Список учебных планов по специальности "
        f"{education_specialty_id} успешно передан"
    )
    return plans


async def get_plan_disciplines(
    table: str = Apeks.TABLES.get("plan_disciplines"),
    level: int | str = Apeks.DISC_LEVEL,
) -> dict:
    """
    Получение полного списка дисциплин из справочника Апекс-ВУЗ.

    Parameters
    ----------
        table: str
            таблица БД, содержащая перечень дисциплин.
        level: int | str
            уровень дисциплин в учебном плане.

    Returns
    ----------
        dict
            {id: {'full': 'название дисциплины', 'short': 'сокращенное название'}}
    """
    response = await check_api_db_response(await api_get_db_table(table, level=level))
    disc_dict = {}
    for disc in response:
        disc_dict[int(disc["id"])] = {
            "full": disc.get("name"),
            "short": disc.get("name_short"),
        }
    logging.debug("Информация о дисциплинах успешно передана")
    return disc_dict


async def get_plan_curriculum_disciplines(
    education_plan_id: int | str, disc_filter: bool = True, **kwargs
) -> dict:
    """
    Получение данных о дисциплинах учебного плана

    Parameters
    ----------
        education_plan_id: int | str
            id учебного плана
        disc_filter: bool
            фильтр удаляет блоки, части блоков и группы дисциплин. Если True,
            то остаются только фактически изучаемые дисциплины.
        **kwargs
            дополнительные фильтры (например department_id)

    Returns
    ----------
        dict
            {curriculum_discipline_id: {'id': id,
                                        'code': code,
                                        'name': name,
                                        'department_id': department_id
                                        'level': value
                                        'left_node: value}}
    """

    def disc_name(discipline_id: int) -> str:
        for discipline in disciplines_list:
            if discipline.get("id") == discipline_id:
                return discipline.get("name")

    disciplines_list = await check_api_db_response(
        await api_get_db_table(Apeks.TABLES.get("plan_disciplines"))
    )
    plan_disciplines = await check_api_db_response(
        await api_get_db_table(
            Apeks.TABLES.get("plan_curriculum_disciplines"),
            education_plan_id=education_plan_id,
            **kwargs,
        )
    )
    disciplines = {}
    for disc in plan_disciplines:
        disciplines[int(disc.get("id"))] = {
            "id": int(disc.get("id")),
            "code": disc.get("code"),
            "name": disc_name(disc.get("discipline_id")),
            "department_id": disc.get("department_id"),
            "level": disc.get("level"),
            "type": disc.get("type"),
            "left_node": disc.get("left_node"),
        }
    if disc_filter:
        for disc in [*disciplines]:
            if str(disciplines[disc].get("level")) != str(Apeks.DISC_LEVEL) or str(
                disciplines[disc].get("type")
            ) == str(Apeks.DISC_GROUP_TYPE):
                del disciplines[disc]
    logging.debug(
        f"Передана информация о дисциплинах education_plan_id: {education_plan_id}"
    )
    return disciplines


async def get_plan_education_specialties() -> dict:
    """
    Получение групп специальностей.

    Returns
    ----------
        dict
            {speciality_id: speciality_name}
    """

    request = data_processor(
        await check_api_db_response(
            await api_get_db_table(
                Apeks.TABLES.get("plan_education_specialties"),
            )
        )
    )
    specialties = {}
    for i in request:
        specialties[i] = request[i].get("name")
    logging.debug(
        "Информация о специальностях 'plan_education_specialties' успешно передана"
    )
    return specialties


async def get_plan_discipline_competencies(
    curriculum_discipline_id: tuple[int | str] | list[int | str],
    table_name: str = Apeks.TABLES.get("plan_curriculum_discipline_competencies"),
) -> dict:
    """
    Получение данных о связях дисциплин и компетенций учебного плана

    Parameters
    ----------
        curriculum_discipline_id: int | str
            id учебной дисциплины плана
        table_name: str
            имя_таблицы

    Returns
    ----------
        dict
            {curriculum_discipline_id: []}
    """

    response = await check_api_db_response(
        await api_get_db_table(
            table_name,
            curriculum_discipline_id=curriculum_discipline_id,
        )
    )
    discipline_competencies = {}
    for res in response:
        disc_id = int(res.get("curriculum_discipline_id"))
        comp_id = int(res.get("competency_id"))
        discipline_competencies.setdefault(disc_id, []).append(comp_id)

    logging.debug(
        "Передана информация о компетенциях "
        f"учебных дисциплин {curriculum_discipline_id}"
    )
    return discipline_competencies


async def get_plan_control_works(
    curriculum_discipline_id: tuple[int | str] | list[int | str],
    table_name: str = Apeks.TABLES.get("plan_control_works"),
    **kwargs
) -> dict:
    """
    Возвращает данные из таблицы "plan_control_works" о завершающих формах
    контроля для дисциплин учебного плана (отбираются записи с наибольшим
    значением "semester_id").

    :param curriculum_discipline_id: id учебной дисциплины
    :param table_name: имя таблицы
    :param kwargs: дополнительные фильтры
    :return: {"curriculum_discipline_id": {"id": record_id,
              "curriculum_discipline_id": id, "control_type_id": id,
              "semester_id": id, "hours": val, "is_classroom": val}
    """
    response = await check_api_db_response(
        await api_get_db_table(
            table_name,
            curriculum_discipline_id=curriculum_discipline_id,
            **kwargs
        )
    )
    control_works = {}
    for record in response:
        disc_id = int(record.get("curriculum_discipline_id"))
        control = control_works.setdefault(disc_id, record)
        if int(control.get("semester_id")) < int(record.get("semester_id")):
            control_works[disc_id] = record
    logging.debug("Передана информация о завершающих формах контроля "
                  f"для дисциплин учебного плана {curriculum_discipline_id}")
    return control_works


async def plan_competency_add(
    education_plan_id: int | str,
    code: str,
    description: str,
    left_node: int | str,
    right_node: int | str,
    level: int | str = 1,
    table_name: str = Apeks.TABLES.get("plan_competencies"),
) -> dict:
    """
    Добавление компетенции в учебный план.

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


async def discipline_competency_add(
    curriculum_discipline_id: int | str,
    competency_id: int | str,
    table_name: str = Apeks.TABLES.get("plan_curriculum_discipline_competencies"),
) -> dict:
    """Добавление компетенции в учебный план.

    Parameters
    ----------
        curriculum_discipline_id: int | str,
            id дисциплины учебного плана
        competency_id: int | str
            id компетенции учебного плана
        table_name: str
            имя таблицы в БД
    """
    response = await api_add_to_db_table(
        table_name,
        curriculum_discipline_id=curriculum_discipline_id,
        competency_id=competency_id,
    )
    if response.get("status") == 1:
        logging.debug(
            f"Добавлена связь дисциплины ({curriculum_discipline_id}) "
            f"и компетенции ({competency_id})."
        )
    else:
        logging.debug(
            f"Не удалось добавить связь дисциплины ({curriculum_discipline_id}) "
            f"и компетенции ({competency_id})."
        )
    return response


async def plan_competencies_del(
    education_plan_id: int | str,
    table_name: str = Apeks.TABLES.get("plan_competencies"),
) -> dict:
    """
    Удаление данных о компетенциях из учебного плана.

    Parameters
    ----------
        education_plan_id: int | str
            id учебного плана
        table_name: str
            имя таблицы в БД
    """

    response = await api_delete_from_db_table(
        table_name,
        education_plan_id=education_plan_id,
    )
    if response.get("status") == 1:
        logging.debug(
            f"Удалены сведения о компетенциях из учебного плана: {education_plan_id}."
        )
    else:
        logging.debug(
            "Не удалось удалить сведения о компетенциях "
            f"из учебного плана: {education_plan_id}."
        )
    return response


async def plan_disciplines_competencies_del(
    curriculum_discipline_id: int | str | tuple[int | str] | list[int | str],
    table_name: str = Apeks.TABLES.get("plan_curriculum_discipline_competencies"),
) -> dict:
    """
    Удаление данных о связях компетенций с дисциплинами из учебного плана.

    Parameters
    ----------
        curriculum_discipline_id: int | str | tuple[int | str] | list[int | str]
            id учебной дисциплины плана
        table_name: str
            имя таблицы в БД
    """

    response = await api_delete_from_db_table(
        table_name,
        curriculum_discipline_id=curriculum_discipline_id,
    )
    if response.get("status") == 1:
        logging.debug(
            f"Удалены сведения о связях компетенций "
            f"с дисциплинами учебного плана: {curriculum_discipline_id}."
        )
    else:
        logging.debug(
            "Не удалось удалить сведения о связях компетенций "
            f"с дисциплинами учебного плана: {curriculum_discipline_id}."
        )
    return response
