from __future__ import annotations

import logging
from calendar import monthrange
from dataclasses import dataclass
from datetime import date

from config import ApeksConfig as Apeks


@dataclass
class EducationStaff:
    """
    Сведения о преподавательском составе кафедр за указанный период.

    Attributes:
    ----------
    year (int | str):
        учебный год (число 20xx).
    month_start (int | str):
        начальный месяц (число 1-12).
    month_end (int | str):
        конечный месяц (число 1-12).
    state_staff (dict):
        данные из таблицы 'state_staff'
        (словарь с именами  в формате: {id: {'full': 'полное имя', 'short': 'сокращенное имя'}}).
    state_staff_history (list):
        данные из таблицы 'state_staff_history' в формате JSON
        (история работы в подразделении)
    state_staff_positions (list):
        данные из таблицы 'state_staff_positions' в формате JSON
        (позиции для сортировки по занимаемой должности)

    Methods:
    -------
    department_staff (department_id: int | str) -> dict
        список преподавателей, работавших в подразделении (id) в указанный период.
    """

    year: int | str
    month_start: int | str
    month_end: int | str
    state_staff: dict
    state_staff_history: list
    state_staff_positions: list

    def __post_init__(self) -> None:
        try:
            self.month_start = int(self.month_start)
            self.month_end = int(self.month_end)
            if self.month_start and self.month_end not in range(1, 13):
                raise ValueError
        except ValueError as error:
            message = (
                f"Конструктор класса {self.__class__} не может принять "
                f"несуществующий начальный - {self.month_start} или "
                f"конечный - {self.month_end} месяцы. {error}"
            )
            logging.error(message)
            raise ValueError(message)
        try:
            self.year = int(self.year)
        except ValueError as error:
            message = (
                "Конструктор класса 'EducationStaff' "
                f"не может принять несуществующий год: {self.year}. {error}"
            )
            logging.error(message)
            raise ValueError(message)

    def department_staff(self, department_id: int | str, reverse: bool = False) -> dict:
        """
        Список преподавателей, работавших в
        выбранном подразделении (department_id) в течении указанного периода,
        отсортированные по занимаемой должности.

        Parameters:
        ----------
        department_id (int | str):
            id кафедры.
        reverse (bool):
            определяет порядок ключей и значений.
            Если True то сначала будет 'short_name' потом id.
            По умолчанию False.

        Returns:
        ----------
        dict
            {id: 'short_name'} или {'short_name': id}.
        """
        staff_list = []
        for staff in self.state_staff_history:
            if staff.get("staff_id") and staff.get("department_id") == str(
                department_id
            ):
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
                            self.year, self.month_start, 1
                        ):
                            staff_list.append(staff_info)
                    else:
                        if date.fromisoformat(staff.get("start_date")) <= date(
                            self.year,
                            self.month_end,
                            monthrange(self.year, self.month_end)[1],
                        ):
                            staff_list.append(staff_info)
        dept_staff = {}
        for staff in sorted(staff_list, key=lambda x: x[2], reverse=True):
            if reverse:
                dept_staff[staff[1]] = staff[0]
            else:
                dept_staff[staff[0]] = staff[1]

        logging.debug(
            "Передана информация о составе подразделения: "
            f"department_id: {department_id}, "
            f"за период year: {self.year}, "
            f"month_start: {self.month_start}, "
            f"month_end: {self.month_end}"
        )
        return dept_staff
