from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ScheduleLessonsStaff:
    """
    Класс для работы со списком занятий преподавателя за определенный период.

    Attributes:
    -----------
        staff_id: int | str
            id преподавателя.
        month: int | str
            месяц (число от 1 до 12).
        year: int | str
            учебный год (число 20хх).
        lessons_data: Iterable
            ответ GET запроса API "/api/call/schedule-schedule/staff"
            в формате JSON.
        disciplines: dict
            список дисциплин в формате {id: {'full': 'название
            дисциплины', 'short': 'сокращенное название'}}.
        load_subgroups_data: dict
            словарь для поиска 'group_id' в случае его отсутствия
            по 'subgroup_id' в формате {subgroup_id: {'group_id': val}}

    Methods:
    --------
        calendar_name(l_index: int) -> str
            выводит заголовок для занятия по его индексу в self.data.
        time_start(l_index: int) -> datetime
            выводит время начала занятия.
        time_end(l_index: int) -> datetime
            выводит время окончания занятия.
    """

    staff_id: int | str
    month: int | str
    year: int | str
    lessons_data: Iterable
    disciplines: dict
    load_subgroups_data: dict

    def calendar_name(self, l_index: int) -> str:
        """
        Выводит полный заголовок занятия по индексу.

        Parameters
        ----------
            l_index: int
                индекс занятия в списке 'lessons_data'
        """
        class_type_name = self.lessons_data[l_index].get("class_type_name")
        topic_code = self.lessons_data[l_index].get("topic_code")
        topic_code_fixed = f" ({topic_code})" if topic_code else ""
        discipline_id = self.lessons_data[l_index].get("discipline_id")
        try:
            short_disc_name = self.disciplines.get(int(discipline_id)).get("short")
        except AttributeError:
            logging.error(
                f"Не найдено название дисциплины по 'discipline_id': {discipline_id}"
            )
            short_disc_name = "Название дисциплины отсутствует"
        group = self.lessons_data[l_index].get("groupName")
        name = f"{class_type_name}{topic_code_fixed} {short_disc_name} {group}"
        return name

    def time_start(self, l_index: int) -> datetime:
        """
        Выводит время начала занятия.

        Parameters
        ----------
            l_index: int
                индекс занятия в списке 'lessons_data'
        """
        date = datetime.strptime(
            self.lessons_data[l_index].get("date"), "%d.%m.%Y"
        ).date()
        time = datetime.strptime(
            self.lessons_data[l_index].get("lessonTime").split(" - ")[0], "%H:%M"
        ).time()
        return datetime.combine(date, time)

    def time_end(self, l_index: int) -> datetime:
        """
        Выводит время окончания занятия.

        Parameters
        ----------
            l_index: int
                индекс занятия в списке 'lessons_data'
        """
        date = datetime.strptime(
            self.lessons_data[l_index].get("date"), "%d.%m.%Y"
        ).date()
        time = datetime.strptime(
            self.lessons_data[l_index].get("lessonTime").split(" - ")[1], "%H:%M"
        ).time()
        return datetime.combine(date, time)
