from typing import Any

from config import ApeksConfig


def process_stable_staff_data(
    departments: dict, staff_history: list, staff_document_data: dict
):
    """
    Рассчитывает информацию о наличии личного состава подразделении.
    """

    for staff in staff_history:
        dept_id = int(staff.get("department_id"))
        dept_data = departments[dept_id]
        if staff.get("vacancy_id") and staff.get("value") == "1":
            dept_data["staff_total"] = dept_data.get("staff_total", 0) + 1
    staff_data = {key: {} for key in ApeksConfig.DEPT_TYPES.values()}

    for dept in sorted(departments, key=lambda d: departments[d].get("short")):
        dept_data = departments[dept]
        dept_type = dept_data.get("type")
        dept_cur_data = staff_document_data["departments"].get(str(dept))
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


def process_full_staff_data(
    staff_ids: dict, state_staff_positions: dict, state_staff: dict
) -> list[dict[str, Any]]:

    full_staff_data = []
    for staff_id, staff_hist in staff_ids.items():
        staff_id = staff_id
        position_id = int(staff_hist.get("position_id"))
        position = state_staff_positions.get(position_id)
        staff_data = state_staff.get(int(staff_id))
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
