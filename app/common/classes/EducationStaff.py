from __future__ import annotations

import logging
from calendar import monthrange
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date

from config import ApeksConfig as Apeks


@dataclass
class EducationStaff:
    """
    Сведения о преподавательском составе кафедр за указанный период.

    Attributes:
    ----------
        year: int | str
            учебный год (число 20xx).
        month_start: int | str
            начальный месяц (число 1-12).
        month_end: int | str
            конечный месяц (число 1-12).
        state_staff: dict
            преобразованные данные из таблицы 'state_staff'
            (словарь с именами  в формате:
            {id: {'full': 'полное имя', 'short': 'сокращенное имя'}}).
        state_staff_history: Iterable
            данные из таблицы 'state_staff_history'
            (история работы в подразделении)
        state_staff_positions: Iterable
            данные из таблицы 'state_staff_positions'
            (позиции для сортировки по занимаемой должности)
        departments: dict
            преобразованные данные из таблицы 'state_departments'
            (словарь с названиями кафедр в формате:
            {id: {'full': 'название кафедры', 'short': 'сокращенное название'}}).

    Methods:
    -------
        department_staff (department_id: int | str) -> dict
            список преподавателей, работавших в подразделении (id) в указанный период.
        staff_history() -> dict
            данные в каком подразделении и когда работал сотрудник.
            если работает в настоящий момент 'end_date' = None.
    """
    # TODO добавить year_start/end, сделать чтобы месяц +/- 6 корректно работали

    year: int | str
    month_start: int | str
    month_end: int | str
    state_staff: dict
    state_staff_history: Iterable
    state_staff_positions: Iterable
    departments: dict

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
        Список преподавателей, работавших в выбранном подразделении
        (department_id) в течении указанного периода, отсортированные
        по занимаемой должности.

        Parameters
        ----------
            department_id: int | str
                id кафедры.
            reverse: bool
                определяет порядок ключей и значений.
                Если True то сначала будет 'short_name' потом id.
                По умолчанию False.

        Returns
        -------
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

    def staff_history(self) -> dict:
        """
        Возвращает словарь с данными в каком подразделении и когда работал
        сотрудник. Если работает в настоящий момент 'end_date' = None.

        Returns
        -------
            dict
                {id: [{'department_id': 'value',
                       'start_date': 'date',
                       'end_date': 'date'}].
        """
        data = {}
        for d_val in self.state_staff_history:
            if int(d_val.get("department_id")) in self.departments:
                staff_id = d_val.get("staff_id")
                if not data.get(int(staff_id)):
                    data[int(staff_id)] = [d_val]
                else:
                    data[int(staff_id)].append(d_val)
        logging.debug(
            "Передана информация 'staff_history' в каком "
            "подразделении и когда работал сотрудник"
        )
        return data
