import logging
from typing import Any

from flask import flash
from pymongo.cursor import Cursor

from app.core.db.staff_models import StaffAllowedFaculty
from config import ApeksConfig


def make_short_name(family_name: str, name: str, surname: str = None) -> str:
    """Создает короткое имя формата Иванов И.И."""
    name_letter = f"{name[0]}." if name else ''
    surname_letter = f"{surname[0]}." if surname else ''
    return f"{family_name} {name_letter}{surname_letter}"


def process_apeks_stable_staff_data(
    departments: dict[str, Any],
    staff_history: dict[str, Any],
    staff_document_data: dict[str, Any],
    state_vacancies: dict[str, Any],
) -> dict:
    """
    Рассчитывает информацию о наличии личного состава подразделений.

    :param departments: данные о подразделениях
    :param staff_history: данные таблицы staff_history
    :param staff_document_data: данные документа на определенную дату
    :param state_vacancies: данные таблицы state_vacancies
    :return: {"Тип подразделения": {"Сокр. назв. подр.": {"name": "short",
              "staff_total": value, "staff_absence": value, "staff_stock": value,
              "staff_military_total": value, "staff_military_absence": value,
              "staff_military_stock": value}}}
    """
    for staff_id, staff_data in staff_history.items():
        dept_id = staff_data.get("department_id")
        dept_data = departments[dept_id]
        vacancy_id = staff_data.get("vacancy_id")
        if vacancy_id:
            vacancy = state_vacancies.get(vacancy_id)
            vacancy_value = staff_data.get("value")
            staff_data["has_rank"] = vacancy.get("has_rank")
            if vacancy_value == "1":
                dept_staff_ids = dept_data.setdefault("dept_staff_ids", {})
                dept_staff_ids[staff_id] = {"has_rank": vacancy.get("has_rank")}
    staff_data = {key: {} for key in ApeksConfig.DEPT_TYPES.values()}
    for dept in sorted(departments, key=lambda d: departments[d].get("short")):
        dept_data = departments[dept]
        dept_type = dept_data.get("type")
        if dept_type in staff_data:
            dept_document_data = staff_document_data["departments"].get(dept)
            dept_total = len(dept_data.get("dept_staff_ids", {}))
            dept_military_total = len(
                [
                    item
                    for item in dept_data.get("dept_staff_ids", {}).values()
                    if item and item.get("has_rank") == "1"
                ]
            )
            if dept_document_data:
                dept_absence_staff_ids = [
                    staff_id
                    for absence_data in dept_document_data["absence"].values()
                    for staff_id in absence_data
                ]
                dept_absence = len(dept_absence_staff_ids)
                dept_military_absence = len(
                    [
                        staff_id
                        for staff_id in dept_absence_staff_ids
                        if staff_history[staff_id].get("has_rank") == "1"
                    ]
                )
            else:
                dept_absence = dept_military_absence = None

            dept_stock = (
                dept_total - dept_absence if isinstance(dept_absence, int) else None
            )
            dept_military_stock = (
                dept_military_total - dept_military_absence
                if isinstance(dept_military_absence, int)
                else None
            )

            type_data = staff_data[dept_type]
            type_data[dept] = {
                "name": dept_data.get("short"),
                "staff_total": dept_total,
                "staff_absence": dept_absence,
                "staff_stock": dept_stock,
                "staff_military_total": dept_military_total,
                "staff_military_absence": dept_military_absence,
                "staff_military_stock": dept_military_stock,
            }
    return staff_data


def process_document_stable_staff_data(staff_document_data: dict) -> dict[str, Any]:
    """Обрабатывает данные документа - строевой записки постоянного состава."""

    if not staff_document_data:
        return {}
    departments = sorted(
        staff_document_data["departments"].values(), key=lambda item: item.get("name")
    )
    staff_data = {
        "staff_total": 0,
        "staff_stock": 0,
        "staff_absence": 0,
        "departments_by_type": {},
        "absence_types": {},
    }
    for department in departments:
        dept_type = department.get("type")
        department["total_absence"] = 0
        type_data = staff_data["departments_by_type"].setdefault(dept_type, list())
        type_data.append(department)
        staff_data["staff_total"] += department.get("total")
        dept_abscence = department.get("absence")
        for abscence in dept_abscence:
            staff_data["absence_types"].setdefault(abscence, 0)
            staff_data["absence_types"][abscence] += len(dept_abscence[abscence])
            department["total_absence"] += len(dept_abscence[abscence])
    staff_data["staff_absence"] = sum(staff_data["absence_types"].values())
    staff_data["staff_stock"] = staff_data["staff_total"] - staff_data["staff_absence"]
    return staff_data


def process_stable_staff_data(
    staff_ids: dict[str, Any],
    state_staff_positions: dict[str, Any],
    state_staff: dict[str, Any],
    state_special_ranks: dict[str, Any] = None
) -> list[dict[str, Any]]:
    """
    Формирует данные о личном составе с должностями и позициями сортировки.

    :param staff_ids: данные таблицы staff_history
    :param state_staff_positions: данные таблицы state_staff_positions
    :param state_staff: данные таблицы state_staff
    :return: list({"staff_id": "staff_id", "name": "short",
                   "position": "name", "sort": "sort"})
    """
    full_staff_data = []
    for staff_id, staff_hist in staff_ids.items():
        position_id = staff_hist.get("position_id")
        position_data = state_staff_positions.get(position_id)
        staff_data = state_staff.get(staff_id)
        rank = None
        if state_special_ranks:
            rank_id = staff_data.get('special_rank_id')
            rank = state_special_ranks.get(rank_id)
        full_staff_data.append(
            {
                "staff_id": staff_id,
                "full_name": staff_data.get("full"),
                "name": staff_data.get("short"),
                "position": position_data.get("name"),
                "department_id": staff_hist.get("department_id"),
                "sort": position_data.get("sort"),
                "rank": rank.get('name') if rank else None
            }
        )
    full_staff_data.sort(key=lambda x: int(x["sort"]), reverse=True)
    return full_staff_data


def process_documents_range_by_busy_type(
    staff_documents_data: Cursor | list,
) -> dict[str, dict[str, Any]]:
    """
    Рассчитывает количество пропусков по типам за период.

    :returns: {"absence_type": {"staff_id": {"name": "staff_name", "count": value}}}
    """
    processed_data = {}
    for document in staff_documents_data:
        try:
            departments = document["departments"]
            for dept_id in departments:
                absence_data = departments[dept_id]["absence"]
                for absence, data in absence_data.items():
                    absence_type_data = processed_data.setdefault(absence, {})
                    if data is not None:
                        for key, value in data.items():
                            staff_info = absence_type_data.setdefault(key, {"count": 0})
                            staff_info["count"] += 1
                            staff_info["name"] = value
        except KeyError:
            message = (
                f"Не удалось прочитать документ {document.get('_id')}. "
                f"Дата документа: {document.get('date')}"
            )
            logging.error(message)
            flash(message, "danger")
    for busy_type in processed_data:
        processed_data[busy_type] = dict(
            sorted(
                processed_data[busy_type].items(),
                key=lambda x: x[1].get("count"),
                reverse=True,
            )
        )
    return processed_data


def process_documents_range_by_staff_id(
    staff_documents_data: Cursor | list,
) -> dict[str, dict[str, Any]]:
    """
    Рассчитывает количество пропусков по сотрудникам за период.

    :returns: {"staff_id" :{"name": "staff_name", "absence": {"absence_type": value}}}
    """
    processed_data = {}
    for document in staff_documents_data:
        try:
            departments = document["departments"]
            for dept_id in departments:
                absence_data = departments[dept_id]["absence"]
                for absence, staff_data in absence_data.items():
                    if staff_data is not None:
                        for key, value in staff_data.items():
                            staff_info = processed_data.setdefault(
                                key, {"absence": {}, "total": 0}
                            )
                            staff_info["name"] = value
                            staff_info["absence"][absence] = (
                                staff_info["absence"].get(absence, 0) + 1
                            )
                            staff_info["total"] += 1
        except KeyError:
            message = (
                f"Не удалось прочитать документ {document.get('_id')}. "
                f"Дата документа: {document.get('date')}"
            )
            logging.error(message)
            flash(message, "danger")
    return dict(sorted(processed_data.items(), key=lambda x: x[1].get("name")))


def staff_various_groups_data_filter(
    groups_data: dict, allowed_faculty: list[StaffAllowedFaculty]
) -> dict:
    """
    Обрабатывает данные факультетов. Фильтрует отсутствующие в таблице
    StaffAllowedFaculty, удаляет архив данных о группа и заменяет название
    факультета из базы данных.
    """
    groups_result = {}
    if groups_data.get("groups"):
        for faculty in allowed_faculty:
            faculty_data = groups_data["groups"].get(str(faculty.apeks_id))
            if faculty_data is not None:
                if faculty_data.get("archive"):
                    del faculty_data["archive"]
                faculty_data["name"] = faculty.name
                groups_result[faculty.apeks_id] = faculty_data
    return groups_result


def process_apeks_various_group_data(
    groups_data: dict[str, Any],
    document_data: dict[str, Any],
) -> dict:
    """
    Добавляет информацию о наличии личного состава в данные о группах.

    :param groups_data: данные о группах
    :param document_data: данные документа на определенную дату
    """

    for faculty_data in groups_data.values():
        if faculty_data.get("items"):
            for course_data in faculty_data["items"].values():
                if course_data.get("items"):
                    for group_data in course_data["items"].values():
                        group_id = group_data.get("id")
                        group_data["student_stock"] = None
                        group_data["student_absence"] = None
                        if document_data["groups"].get(group_id):
                            document_group = document_data["groups"][group_id]
                            # group_data["student_total"] = document_group.get("total")
                            group_data["student_absence"] = sum(
                                len(absence)
                                for absence in document_group["absence"].values()
                            ) + sum(
                                len(absence)
                                for absence in document_group[
                                    "absence_illness"
                                ].values()
                            )
                            group_data["student_stock"] = (
                                group_data["student_count"]
                                - group_data["student_absence"]
                            )
    return groups_data


def process_document_various_staff_data(various_document_data: dict, faculty_names: dict) -> dict[str, Any]:
    """Обрабатывает данные документа - строевой записки переменного состава."""

    if not various_document_data:
        return {}
    staff_data = {
        "daytime": various_document_data.get("daytime"),
        "status": various_document_data.get("status"),
        "total": 0,
        "stock": 0,
        "absence": 0,
        "faculty_data": {}
    }
    for group in various_document_data["groups"].values():
        faculty = group["faculty"]
        if faculty not in staff_data["faculty_data"]:
            staff_data["faculty_data"][faculty] = {
                "total": 0, "stock": 0, "absence": 0, "absence_types": {}
            }
        faculty_data = staff_data["faculty_data"][faculty]
        faculty_data["total"] += group["total"]
        for absence_type in group["absence"]:
            value = len(group["absence"][absence_type])
            faculty_data["absence_types"].setdefault(absence_type, 0)
            faculty_data["absence_types"][absence_type] += value
            faculty_data["absence"] += value
        faculty_data["absence_types"].setdefault("illness", 0)
        for illness in group["absence_illness"]:
            value = len(group["absence_illness"][illness])
            faculty_data["absence_types"]["illness"] += value
            faculty_data["absence"] += value
        faculty_data["stock"] = faculty_data["total"] - faculty_data["absence"]

    def sort_faculty(faculty_name):
        if faculty_name in faculty_names:
            return faculty_names[faculty_name]
        return max(faculty_names.values()) + 1

    staff_data["faculty_data"] = {
        faculty: staff_data["faculty_data"][faculty]
        for faculty in sorted(staff_data["faculty_data"], key=sort_faculty)
    }

    for faculty in staff_data["faculty_data"]:
        staff_data["total"] += staff_data["faculty_data"][faculty]["total"]
        staff_data["stock"] += staff_data["faculty_data"][faculty]["stock"]
        staff_data["absence"] += staff_data["faculty_data"][faculty]["absence"]

    return staff_data
