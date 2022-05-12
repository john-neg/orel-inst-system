
# schedule_day_schedule_lessons - занятия
# schedule_day_schedule_lessons_staff - staff_id для каждого занятия {lesson_id:staff_id}
# load_subgroups - подгруппы
# load_groups
# plan_education_plans_education_forms
# plan_education_plans
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
        self.load_groups_data = self.load_groups_processor(self.load_groups)
        self.load_groups_data = self.load_groups_processor(self.load_groups)

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
    def load_groups_processor(load_groups):
        """
        Get group info by group_id
        {id:[{}].
        """
        data = {}
        for group in load_groups:
            data[group.get("id")] = group
        return data


