import datetime
import logging
from typing import Any

from flask import flash
from pymongo.cursor import Cursor

from app.auth.func import has_permission
from app.core.services.apeks_db_state_departments_service import get_db_apeks_state_departments_service
from app.core.services.apeks_db_system_branches import get_apeks_db_system_branches_service
from app.core.services.apeks_db_system_settings import get_apeks_db_system_settings_service
from config import ApeksConfig, PermissionsConfig
from ..core.db.staff_models import StaffAllowedFaculty, StaffVariousBusyTypes
from ..core.services.apeks_db_student_marks_service import (
    get_apeks_db_student_marks_service,
)
from ..core.services.apeks_db_student_student_history_service import (
    get_apeks_db_student_student_history_service,
)
from ..core.services.apeks_db_student_students_groups_service import (
    get_apeks_db_student_students_groups_service,
)
from ..core.services.apeks_db_student_students_service import (
    get_apeks_db_student_students_service,
)
from ..core.services.base_apeks_api_service import data_processor
from ..core.services.staff_various_document_service import StaffVariousGroupDocStructure


def make_short_name(family_name: str, name: str, surname: str = None) -> str:
    """Создает короткое имя формата Иванов И.И."""
    name_letter = f"{name[0]}." if name else ""
    surname_letter = f"{surname[0]}." if surname else ""
    return f"{family_name} {name_letter}{surname_letter}"


def process_apeks_stable_staff_data(
    departments: dict[str, Any],
    staff_history: dict[str, Any],
    staff_document_data: dict[str, Any],
    state_vacancies: dict[str, Any],
    branches: dict[str, str]
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
        dept_data = departments.get(dept_id)
        vacancy_id = staff_data.get("vacancy_id")
        if vacancy_id and dept_data:
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
            dept_branch_id = dept_data.get("branch_id")
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
                        if staff_history.get(staff_id)
                        and staff_history[staff_id].get("has_rank") == "1"
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
                "branch_id": dept_branch_id
            }
    # TODO далее следует говнокод, который преобразует старую структуру данных с одним подразделением
    # в структуру, содержащую филиалы:
    result = {}
    for depts_by_types in staff_data:
        for item in staff_data[depts_by_types]:
            if not result.get(branches[staff_data[depts_by_types][item].get('branch_id')]):
                result[branches[staff_data[depts_by_types][item].get('branch_id')]] = {}
            if not result[branches[staff_data[depts_by_types][item].get('branch_id')]].get(depts_by_types):
                result[branches[staff_data[depts_by_types][item].get('branch_id')]][depts_by_types] = {}
            result[branches[staff_data[depts_by_types][item].get('branch_id')]][depts_by_types][item] = staff_data[depts_by_types][item]
    staff_data = result
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
    state_special_ranks: dict[str, Any] = None,
) -> list[dict[str, Any]]:
    """
    Формирует данные о личном составе с должностями и позициями сортировки.

    :param staff_ids: данные таблицы staff_history
    :param state_staff_positions: данные таблицы state_staff_positions
    :param state_staff: данные таблицы state_staff
    :param state_special_ranks: данные таблицы state_special_ranks
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
            rank_id = staff_data.get("special_rank_id")
            rank = state_special_ranks.get(rank_id)
        full_staff_data.append(
            {
                "staff_id": staff_id,
                "full_name": staff_data.get("full"),
                "name": staff_data.get("short"),
                "position": position_data.get("name"),
                "department_id": staff_hist.get("department_id"),
                "sort": position_data.get("sort"),
                "rank": rank.get("name") if rank else None,
            }
        )
    full_staff_data.sort(key=lambda x: int(x["sort"]), reverse=True)
    return full_staff_data


def process_documents_range_by_busy_type(
    staff_documents_data: Cursor | list,
    depts: list,
    branches: list
) -> dict[str, dict[str, Any]]:
    """
    Рассчитывает количество пропусков по типам за период.

    :returns: {"branch": {"absence_type": {"staff_id": {"name": "staff_name", "count": value}}}}
    """
    processed_data = {}
    # добавляем структуру филиалов
    for branch in branches:
        processed_data[branch] = {}
    for document in staff_documents_data:
        try:
            departments = document["departments"]
            for dept_id in departments:
                absence_data = departments[dept_id]["absence"]
                for absence, data in absence_data.items():
                    if dept_id in depts:
                        absence_type_data = processed_data[depts[dept_id]['branch_id']].setdefault(absence, {})
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
    for branch in processed_data:
        for busy_type in processed_data[branch]:
            processed_data[branch][busy_type] = dict(
                sorted(
                    processed_data[branch][busy_type].items(),
                    key=lambda x: x[1].get("count"),
                    reverse=True,
                )
            )
    return processed_data


def process_documents_range_by_staff_id(
    staff_documents_data: Cursor | list,
    depts: list,
    branches: list
) -> dict[str, dict[str, Any]]:
    """
    Рассчитывает количество пропусков по сотрудникам за период.

    :returns: {"branch": {"staff_id" :{"name": "staff_name", "absence": {"absence_type": value}}}}
    """
    processed_data = {}
    # добавляем структуру филиалов
    for branch in branches:
        processed_data[branch] = {}
    for document in staff_documents_data:
        try:
            departments = document["departments"]
            for dept_id in departments:
                absence_data = departments[dept_id]["absence"]
                for absence, staff_data in absence_data.items():
                    if staff_data is not None:
                        for key, value in staff_data.items():
                            if dept_id in depts:
                                staff_info = processed_data[depts[dept_id]['branch_id']].setdefault(
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
    for branch in branches:
        processed_data[branch] = dict(sorted(processed_data[branch].items(), key=lambda x: x[1].get("name")))
    return processed_data


async def get_students_data(group_id: str | int) -> list:
    """
    Возвращает список студентов учебной группы.

    :param group_id: Идентификатор группы
    :returns: [{'id': '797', 'family_name': 'Фамилия ', 'name': 'Имя',
                'surname': 'Отчество', 'sex': 'F', 'birthday': '2003-12-09',
                'user_id': '188', 'special_rank_id': '1', 'file_id': None,
                'employer_id': '3', 'job_position_id': '1',
                'external_id': '', 'short_name': 'Фамилия И.О.'}]
    """

    students_group_service = get_apeks_db_student_students_groups_service()
    group_students = data_processor(
        await students_group_service.get(group_id=group_id),
        key="student_id",
    )
    students_service = get_apeks_db_student_students_service()
    students_data = await students_service.get(id=group_students)
    students_data = sorted(students_data, key=lambda x: x.get("family_name"))
    student_history_service = get_apeks_db_student_student_history_service()
    fired_students = [
        student.get("student_id")
        for student in await student_history_service.get(
            student_id=group_students.keys(),
            type=ApeksConfig.STUDENT_HISTORY_RECORD_TYPES.keys(),
            group_id=group_id,
        )
    ]
    students_data = [
        student for student in students_data if student.get("id") not in fired_students
    ]
    for student in students_data:
        student["short_name"] = make_short_name(
            student.get("family_name"), student.get("name"), student.get("surname")
        )
    return students_data


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
            # заменяем None в banch_id на 0:
            if not groups_data["groups"].get(str(faculty.apeks_id))['branch_id']:
                groups_data["groups"].get(str(faculty.apeks_id))['branch_id'] = '0'
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


def process_document_various_staff_data(
    various_document_data: dict,
    groups: list,
    faculty_names: dict,
    branches: dict,
    departments
) -> dict[str, Any]:
    """Обрабатывает данные документа - строевой записки переменного состава."""

    if not various_document_data:
        return {}
    staff_data = {}
    for branch in branches:
        branch_data = staff_data.setdefault(branch, {})
        branch_data.update({
            "daytime": various_document_data.get("daytime"),
            "status": various_document_data.get("status"),
            "total": 0,
            "stock": 0,
            "absence": 0,
            "faculty_data": {},
        })
        for group in various_document_data["groups"].values():
            faculty = group["faculty"]
            faculty_branch_id = 0
            faculty_id = 0
            for gr in groups:
                if gr['id'] == group['id']:
                    faculty_id = gr['department_id']
                    if departments.get(faculty_id):
                        faculty_branch_id = departments[faculty_id]['branch_id']
            if faculty_branch_id != branch:
                continue
            if faculty_id not in branch_data["faculty_data"]:
                branch_data["faculty_data"][faculty_id] = {
                    "faculty": faculty,
                    "faculty_id": faculty_id,
                    "total": 0,
                    "stock": 0,
                    "absence": 0,
                    "absence_types": {},
                }
            faculty_data = branch_data["faculty_data"][faculty_id]
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
        faculty_ids = {}
        for faculty, faculty_data in faculty_names.items():
            faculty_ids[str(faculty_data[2])] = [faculty_data[0], faculty]

        def sort_faculty(faculty_id):
            if faculty_id in faculty_ids:
                return faculty_ids[faculty_id]
            return max(faculty_ids.values()) + 1

        branch_data["faculty_data"] = {
            faculty: branch_data["faculty_data"][faculty]
            for faculty in sorted(branch_data["faculty_data"], key=sort_faculty)
        }
        for faculty in branch_data["faculty_data"]:
            branch_data["total"] += branch_data["faculty_data"][faculty]["total"]
            branch_data["stock"] += branch_data["faculty_data"][faculty]["stock"]
            branch_data["absence"] += branch_data["faculty_data"][faculty]["absence"]
        branch_data["faculty_data"] = {
            faculty_ids[faculty_id][1]: faculty_data for faculty_id, faculty_data in branch_data["faculty_data"].items()
        }

    return staff_data


async def lesson_skips_processor(
    lesson: dict,
    document: StaffVariousGroupDocStructure,
    busy_types: list[StaffVariousBusyTypes],
    group_students: dict,
):
    """Обрабатывает пропуски занятия и редактирует электронный журнал."""

    student_marks_service = get_apeks_db_student_marks_service()
    journal_lesson_id = lesson.get("journal_lesson_id")
    lesson_marks = await student_marks_service.get(journal_lesson_id=journal_lesson_id)
    lesson_actions = {
        "name": lesson.get("discipline"),
        "add": 0,
        "edit": 0,
        "delete": 0,
    }
    busy_data = {busy.slug: busy.match for busy in busy_types}

    students_skips = {}
    for absence in document.absence:
        for student in document.absence[absence]:
            if busy_data.get(absence):
                students_skips[student] = str(busy_data.get(absence))
    for illness in document.absence_illness:
        for student in document.absence_illness[illness]:
            students_skips[student] = str(ApeksConfig.ILLNESS_SKIP_ID)

    for mark in lesson_marks:
        student_id = mark.get("student_id")
        skip_reason_id = mark.get("skip_reason_id")
        user_id = mark.get("user_id")
        if user_id == str(ApeksConfig.BASE_USER_ID) and student_id in group_students:
            if student_id not in students_skips:
                delete_count = await student_marks_service.delete(
                    journal_lesson_id=journal_lesson_id,
                    student_id=student_id,
                    user_id=user_id,
                )
                lesson_actions["delete"] += delete_count
            elif students_skips[student_id] != skip_reason_id:
                filters = {
                    "journal_lesson_id": journal_lesson_id,
                    "student_id": student_id,
                    "user_id": user_id,
                }
                fields = {
                    "skip_reason_id": students_skips[student_id],
                    "datetime": datetime.datetime.now(),
                }
                edit_count = await student_marks_service.update(filters, fields)
                lesson_actions["edit"] += edit_count
        if student_id in students_skips:
            del students_skips[student_id]

    for student_id, skip_reason_id in students_skips.items():
        add_count = await student_marks_service.create(
            journal_lesson_id=journal_lesson_id,
            mark_type_id="1",
            student_id=student_id,
            skip_reason_id=skip_reason_id,
            user_id=ApeksConfig.BASE_USER_ID,
            datetime=datetime.datetime.now(),
        )
        lesson_actions["add"] += add_count
    return lesson_actions


async def get_departments_by_branches():
    """Возвращает список подразделений, разбитый по филиалам"""

    # TODO говнокод, можно улучшить + учесть вариат > 1 филиала
    departments = {}
    departments_service = get_db_apeks_state_departments_service()
    if has_permission(PermissionsConfig.USER_HEAD_OFFICE_PERMISSION):
        departments.update(await departments_service.get_departments(branch_id='0'))
    if has_permission(PermissionsConfig.USER_BRANCH_OFFICE_1_PERMISSION):
        departments.update(await departments_service.get_departments(branch_id='1'))
    return departments
        

async def get_branches():
    """Возвращает список филиалов"""

    # TODO тоже говнокод
    branches = {}
    if has_permission(PermissionsConfig.USER_HEAD_OFFICE_PERMISSION):
        # получить название головного подразделения
        system_settings_service = get_apeks_db_system_settings_service()
        raw_settings = await system_settings_service.get()
        for item in raw_settings:
            if item['setting'] == 'system.ou.short_name':
                branches['0'] = item['value']
                break
    if has_permission(PermissionsConfig.USER_BRANCH_OFFICE_1_PERMISSION):
        # получить названия филиалов
        system_branches_service = get_apeks_db_system_branches_service()
        raw_branches = await system_branches_service.get()
        for branch in raw_branches:
            branches[branch['id']] = branch['name']
    return branches

