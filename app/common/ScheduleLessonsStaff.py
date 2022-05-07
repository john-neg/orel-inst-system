from __future__ import annotations

from datetime import datetime

from app.common.func import (
    api_get_staff_lessons,
    check_api_staff_lessons_response,
    get_disc_list,
)


class ScheduleLessonsStaff:
    """Класс для работы со списком занятий преподавателя за определенный период.

    Attributes
    ----------
    staff_id: int | str,
        id преподавателя
    month: int | str,
        месяц
    year: int | str
        учебный год

    Methods
    -------
    calendar_name(self, l_index: int) -> str
        выводит заголовок для занятия по его индексу в self.data.
    short_disc_name(self, discipline_id: int | str) -> str:
        получение сокращенного названия дисциплины для занятия
    time_start(self, l_index: int) -> datetime:
        время начала занятия -> datetime
    time_end(self, l_index: int) -> datetime:
        время окончания занятия -> datetime.
    """

    def __init__(self, staff_id: int | str, month: int | str, year: int | str) -> None:
        self.data = check_api_staff_lessons_response(
            api_get_staff_lessons(staff_id, month, year)
        )
        self.plan_disciplines = get_disc_list()

    def calendar_name(self, l_index: int) -> str:
        """Вывод полного заголовка занятия по индексу."""
        class_type_name = self.data[l_index].get("class_type_name")
        topic_code = self.data[l_index].get("topic_code")
        topic_code_fixed = f" ({topic_code})" if topic_code else ""
        short_disc_name = self.short_disc_name(self.data[l_index].get("discipline_id"))
        group = self.data[l_index].get("groupName")
        name = f"{class_type_name}{topic_code_fixed} {short_disc_name} {group}"
        return name

    def short_disc_name(self, discipline_id: int | str) -> str:
        """Получение сокращенного названия дисциплины для занятия."""
        for disc in self.plan_disciplines:
            if disc.get("id") == str(discipline_id):
                return disc.get("name_short")

    def time_start(self, l_index: int) -> datetime:
        """Время начала занятия -> datetime"""
        date = datetime.strptime(self.data[l_index].get("date"), "%d.%m.%Y").date()
        time = datetime.strptime(
            self.data[l_index].get("lessonTime").split(" - ")[0], "%H:%M"
        ).time()
        return datetime.combine(date, time)

    def time_end(self, l_index: int) -> datetime:
        """Время окончания занятия -> datetime"""
        date = datetime.strptime(self.data[l_index].get("date"), "%d.%m.%Y").date()
        time = datetime.strptime(
            self.data[l_index].get("lessonTime").split(" - ")[1], "%H:%M"
        ).time()
        return datetime.combine(date, time)
