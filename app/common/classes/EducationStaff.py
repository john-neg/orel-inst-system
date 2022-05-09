from __future__ import annotations

import logging
from calendar import monthrange
from datetime import date

from app.common.func import api_get_db_table, check_api_db_response, get_state_staff
from config import ApeksConfig as Apeks


class EducationStaff:
    """
    Сведения о преподавательском составе по подразделениям.
    Используются 3 таблицы базы данных Апекс-ВУЗ:
    'state_staff' - список имен,
    'state_staff_history' - история работы в подразделении,
    'state_staff_positions' - позиции для сортировки.

    Attributes
    ----------
    month: int | str
        месяц (также можно указывать 2 периода:
            "январь-август" (1 семестр),
            "сентябрь-декабрь" (2 семестр))
    year: int | str
        учебный год

    Methods
    -------
    department_staff (department_id: int | str) -> dict
        список преподавателей, работавших в подразделении (id) в заданный период.
    """

    def __init__(self, month: int | str, year: int | str) -> None:
        month_tuple = tuple(
            [str(i) for i in range(1, 13)]
            + ["0" + str(i) for i in range(1, 10)]
            + ["январь-август", "сентябрь-декабрь"]
        )
        if str(month) in month_tuple:
            if month == "январь-август":
                self.start_month = 1
                self.end_month = 8
            elif month == "сентябрь-декабрь":
                self.start_month = 9
                self.end_month = 12
            else:
                self.start_month = int(month)
                self.end_month = int(month)
        else:
            message = (
                "Конструктор класса 'EducationStaff' "
                f"не может принять несуществующий месяц: {month}."
            )
            logging.error(message)
            raise ValueError(message)
        try:
            self.year = int(year)
        except ValueError as error:
            message = (
                "Конструктор класса 'EducationStaff' "
                f"не может принять несуществующий год: {year}. {error}"
            )
            logging.error(message)
            raise ValueError(message)

        self.state_staff = get_state_staff()
        self.state_staff_history = check_api_db_response(
            api_get_db_table("state_staff_history")
        )
        self.state_staff_positions = check_api_db_response(
            api_get_db_table(Apeks.tables.get("state_staff_positions"))
        )

    def department_staff(self, department_id: int | str) -> dict:
        """
        Список преподавателей, работавших в
        выбранном подразделении в течении выбранного периода,
        отсортированные по занимаемой должности.
        """
        staff_list = []
        for staff in self.state_staff_history:
            if staff.get("staff_id"):
                staff_id = int(staff.get("staff_id"))
                staff_pos = staff.get("position_id")
                if staff_pos and int(staff_pos) not in Apeks.EXCLUDE_LIST:
                    for pos in self.state_staff_positions:
                        if pos.get("id") == staff_pos:
                            staff["sort"] = int(pos.get("sort"))
                            break
                    else:
                        staff["sort"] = 0

                    staff_info = (
                        staff_id,
                        self.state_staff.get(staff_id).get("short"),
                        staff.get("sort"),
                    )

                    if staff.get("end_date"):
                        if date.fromisoformat(staff.get("end_date")) > date(
                            self.year, self.start_month, 1
                        ):
                            staff_list.append(staff_info)
                    else:
                        if date.fromisoformat(staff.get("start_date")) <= date(
                            self.year,
                            self.end_month,
                            monthrange(self.year, self.end_month)[1],
                        ):
                            staff_list.append(staff_info)
        dept_staff = {}
        for staff in sorted(staff_list, key=lambda x: x[2], reverse=True):
            dept_staff[staff[0]] = staff[1]

        logging.debug(
            "Передана информация о составе подразделения: "
            f"department_id:{department_id}, "
            f"за период year:{self.year}, "
            f"start_month:{self.start_month}, "
            f"end_month:{self.end_month}"
        )
        return dept_staff
