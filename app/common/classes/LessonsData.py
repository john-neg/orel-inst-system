from copy import copy
from dataclasses import dataclass

from app.common.func import data_processor


@dataclass
class LessonsDataProcessor:
    """
    Обработчик сведений об учебных занятиях

    Attributes:
    ----------
        schedule_lessons: list
            данные из таблицы 'schedule_day_schedule_lessons'
            (сведения об учебных занятиях)
        schedule_lessons_staff: list
            данные из таблицы 'schedule_day_schedule_lessons_staff'
            (сведения о преподавателях, которые проводили занятия)
        load_groups: list
            данные из таблицы 'load_groups'
            (названия учебных групп)
        load_subgroups: list
            данные из таблицы 'load_subgroups'
            (названия учебных подгрупп и 'group_id' соответствующих групп)
        plan_education_plans: list
            данные из таблицы 'plan_education_plans'
            (сведения об учебных планах)
        plan_education_plans_education_forms: list
            данные из таблицы 'plan_education_plans_education_forms'
            (содержит 'education_form_id' для учебных планов)

    Methods:
    -------
        lessons_staff_processor (lessons_staff: dict) -> dict
            обрабатывает данные таблицы lessons_staff,
            выводит словарь в формате: {lesson_id: [staff_id]}
        data_processor (table_data: list, dict_key: str) -> dict
            преобразует полученные данные из таблиц БД Апекс-ВУЗ
            в словарь {id: {keys: values}}.

    """

    schedule_lessons: list
    schedule_lessons_staff: list
    load_groups: list
    load_subgroups: list
    plan_education_plans: list
    plan_education_plans_education_forms: list
    departments: dict

    def __post_init__(self):
        self.lessons_staff_data = self.lessons_staff_processor(
            self.schedule_lessons_staff
        )
        self.groups_data = data_processor(self.load_groups)
        self.subgroups_data = data_processor(self.load_subgroups)
        self.education_plans_data = data_processor(self.plan_education_plans)
        self.plans_education_forms_data = data_processor(
            self.plan_education_plans_education_forms, dict_key="education_plan_id"
        )

    @staticmethod
    def lessons_staff_processor(lessons_staff: list) -> dict:
        """
        Обрабатывает данные таблицы 'lessons_staff'.

        Parameters
        ----------
            lessons_staff: list
                данные таблицы 'lessons_staff' в формате JSON

        Returns
        -------
        dict
            {lesson_id: [staff_id]}.
        """
        data = {}
        for i in lessons_staff:
            if i.get("lesson_id") in data:
                data[int(i.get("lesson_id"))].append(int(i.get("staff_id")))
            else:
                data[int(i.get("lesson_id"))] = [int(i.get("staff_id"))]
        return data



    def staff_dept_structure(self):
        """
        Department ID for prepod in current month
        {staff_id:department_id}.
        """
        structure = {}
        for dept in self.departments:
            staff_list = self.education_staff_data.department_staff(dept)
            for staff in staff_list:
                structure[staff] = dept
        return structure

    def process_lessons(self):
        """Current month lessons list with all data for load report"""
        structured_lessons = []
        for lesson in self.schedule_lessons:
            group_id = lesson.get("group_id")
            if not group_id:
                subgroup_id = lesson.get("subgroup_id")
                if subgroup_id:
                    lesson["group_id"] = self.subgroups_data[subgroup_id].get("group_id")
            education_plan_id = self.groups_data.get(group_id)["education_plan_id"]
            education_form_id = self.plans_education_forms_data.get(education_plan_id).get('education_form_id')
            education_level_id = self.education_plans_data.get(education_plan_id).get("education_level_id")
            lesson["education_plan_id"] = education_plan_id
            lesson["education_form_id"] = education_form_id
            lesson["education_level_id"] = education_level_id
            if lesson.get("id") in self.lessons_staff_data:
                for staff in self.lessons_staff_data.get(lesson["id"]):
                    # Копируем для того чтобы одно занятие учитывалось
                    # разным преподавателям (когда проводят двое, трое и т.д.)
                    less_copy = copy(lesson)
                    less_copy["staff_id"] = int(staff)
                    #TODO написать код для работы с методом staff_history класса EducationStaff
                    less_copy["department_id"] = self.staff_dept_structure.get(int(staff))
                    less_copy["hours"] = 2
                    structured_lessons.append(less_copy)
        return structured_lessons




# 'schedule_day_schedule_lessons' - занятия
# 'schedule_day_schedule_lessons_staff' - staff_id для каждого занятия {lesson_id:staff_id}
# 'load_subgroups' - подгруппы
# 'load_groups'
# 'plan_education_plans_education_forms'
# 'plan_education_plans'


import requests
from pprint import pprint
from config import ApeksConfig as Apeks


def db_request(table_name):
    """DB request function without filter."""
    params = {"token": Apeks.TOKEN, "table": table_name}
    response = requests.get(Apeks.URL + "/api/call/system-database/get", params=params)
    return response.json()["data"]


pprint(db_request("state_staff_history"))
