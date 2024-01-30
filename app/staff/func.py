from typing import Any

from config import ApeksConfig


def process_apeks_stable_staff_data(
    departments: dict, staff_history: list, staff_document_data: dict
) -> dict:
    """
    Рассчитывает информацию о наличии личного состава подразделений.

    :param departments: данные о подразделениях
    :param staff_history: данные таблицы staff_history
    :param staff_document_data: данные документа на определенную дату
    :return: {"Тип подразделения": {"Сокр. назв. подр.": {"name": "short",
              "staff_total": num, "staff_absence": num, "staff_stock": num}}}
    """
    for staff in staff_history:
        dept_id = staff.get("department_id")
        dept_data = departments[dept_id]
        if staff.get("vacancy_id") and staff.get("value") == "1":
            dept_data["staff_total"] = dept_data.get("staff_total", 0) + 1
    staff_data = {key: {} for key in ApeksConfig.DEPT_TYPES.values()}
    for dept in sorted(departments, key=lambda d: departments[d].get("short")):
        dept_data = departments[dept]
        dept_type = dept_data.get("type")
        dept_cur_data = staff_document_data["departments"].get(dept)
        dept_total = dept_data.get("staff_total", 0)
        dept_absence = (
            sum(len(val) for val in dept_cur_data["absence"].values())
            if dept_cur_data
            else "нет данных"
        )
        dept_stock = (
            dept_total - dept_absence if isinstance(dept_absence, int) else "нет данных"
        )
        if dept_type in staff_data:
            type_data = staff_data[dept_type]
            type_data[dept] = {
                "name": dept_data.get("short"),
                "staff_total": dept_total,
                "staff_absence": dept_absence,
                "staff_stock": dept_stock,
            }
    return staff_data


def process_document_stable_staff_data(staff_document_data: dict) -> dict[str, Any]:
    """Обрабатывает данные документа - строевой записки постоянного состава."""

    if not staff_document_data:
        return {}
    departments = sorted(
        staff_document_data["departments"].values(),
        key=lambda item: item.get("name")
    )
    staff_data = {
        "staff_total": 0,
        "staff_stock": 0,
        "staff_absence": 0,
        "departments_by_type": {},
        "absence_types": {}
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


def process_full_staff_data(
    staff_ids: dict[str, Any],
    state_staff_positions: dict[str, Any],
    state_staff: dict[str, Any],
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
        position = state_staff_positions.get(position_id)
        staff_data = state_staff.get(staff_id)
        full_staff_data.append(
            {
                "staff_id": staff_id,
                "name": staff_data.get("short"),
                "position": position.get("name"),
                "sort": position.get("sort"),
            }
        )
    full_staff_data.sort(key=lambda x: int(x["sort"]), reverse=True)
    return full_staff_data
