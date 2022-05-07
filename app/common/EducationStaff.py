from __future__ import annotations

import logging
from calendar import monthrange
from datetime import date

from app.common.func import api_get_db_table, check_api_db_response
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

    def __init__(
        self,
        month: int | str,
        year: int | str,
    ) -> None:
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

        self.state_staff_history = check_api_db_response(
            api_get_db_table(Apeks.tables.get("state_staff_history"))
        )
        self.state_staff = self.get_state_staff()
        self.state_staff_positions = check_api_db_response(
            api_get_db_table(Apeks.tables.get("state_staff_positions"))
        )

    @staticmethod
    def get_state_staff() -> dict:
        """Получение коротких имен преподавателей."""
        staff_short_dict = {}
        resp = check_api_db_response(api_get_db_table(Apeks.tables.get("state_staff")))
        for staff in resp:
            family_name = staff.get("family_name")
            family_name = family_name if family_name else "??????"
            first_name = staff.get("name")
            first_name = first_name[0] if first_name else "?"
            second_name = staff.get("surname")
            second_name = second_name[0] if second_name else "?"
            staff_short_dict[
                staff.get("id")
            ] = f"{family_name} {first_name}.{second_name}."
        return staff_short_dict

    def department_staff(self, department_id: int | str) -> dict:
        """
        Список преподавателей, работавших в
        выбранном подразделении в течении выбранного периода.
        """

        def staff_sort(staff_id: int | str):
            """Получение кода сортировки преподавателей по должности."""
            position_id = ""
            for sort_staff in staff_list:
                if sort_staff.get("staff_id") == str(staff_id):
                    position_id = sort_staff.get("position_id")
            for k in self.state_staff_positions:
                if k.get("id") == position_id:
                    return k.get("sort")

        dept_history = [
            i
            for i in self.state_staff_history
            if i.get("department_id") == str(department_id)
        ]

        staff_list = []
        for staff in dept_history:
            if staff.get("position_id") not in Apeks.EXCLUDE_LIST:
                if staff.get("end_date"):
                    if date.fromisoformat(staff.get("end_date")) > date(
                        self.year, self.start_month, 1
                    ):
                        staff_list.append(staff)
                else:
                    if date.fromisoformat(staff.get("start_date")) <= date(
                        self.year,
                        self.end_month,
                        monthrange(self.year, self.end_month)[1],
                    ):
                        staff_list.append(staff)

        sort_dict = {}
        for i in staff_list:
            sort_dict[i["staff_id"]] = int(staff_sort(i["staff_id"]))
        a = sorted(sort_dict.items(), key=lambda x: x[1], reverse=True)

        prepod_dict = {}
        for i in range(len(a)):
            prepod_dict[a[i][0]] = self.state_staff.get(a[i][0])
        logging.debug(
            "Передана информация о составе подразделения: "
            f"department_id:{department_id}, "
            f"за период year:{self.year}, "
            f"start_month:{self.start_month}, "
            f"end_month:{self.end_month}"
        )
        return prepod_dict
