from dataclasses import dataclass


@dataclass
class LessonsDataProcessor:
    # year: int | str
    # month_start: int | str
    # month_end: int | str
    schedule_lessons: list
    schedule_lessons_staff: dict
    load_groups: dict
    load_subgroups: dict
    plan_education_plans: dict
    plan_education_plans_education_forms: dict

    def __post_init__(self):
        self.lessons_staff_data = self.lessons_staff_processor(self.schedule_lessons_staff)
        self.load_groups_data = self.data_processor(self.load_groups)
        self.load_subgroups_data = self.data_processor(self.load_subgroups)
        # self.load_education_plans_data =

    @staticmethod
    def lessons_staff_processor(lessons_staff):
        """
        Соответствие id занятия id преподавателя

        {lesson_id: [staff_id]}
        """
        data = {}
        for i in lessons_staff:
            if i.get("lesson_id") in data:
                data[int(i.get("lesson_id"))].append(int(i.get("staff_id")))
            else:
                data[int(i.get("lesson_id"))] = [int(i.get("staff_id"))]
        return data

    @staticmethod
    def data_processor(load_groups):
        """Преобразует информацию о группах в словарь {id: 'name'}."""
        data = {}
        for group in load_groups:
            data[int(group.get("id"))] = group
        return data

    # @staticmethod
    # def education_plans_processor(
    #         plan_education_plans,
    #         plan_education_plans_education_forms
    # ):
        # cls.data_processor(self.plan_education_plans)
        # self.data_processor(plan_education_plans_education_forms)
        # """Преобразует информацию о группах в словарь {id: 'name'}."""
        # data = {}
        # for group in load_groups:
        #     data[int(group.get("id"))] = group
        # return data


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
    response = requests.get(
        Apeks.URL + "/api/call/system-database/get", params=params
    )
    return response.json()["data"]


pprint(db_request('plan_education_plans_education_forms'))
