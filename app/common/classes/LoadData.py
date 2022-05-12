from __future__ import annotations

from dataclasses import dataclass

from app.common.classes.EducationStaff import EducationStaff

from config import ApeksConfig as Apeks


@dataclass
class LoadData(EducationStaff):
    year: int | str
    month_start: int | str
    month_end: int | str
    departments: dict
    lessons_staff: dict
    load_groups: dict
    load_subgroups: dict
    plan_education_plans: dict
    plan_education_plans_education_forms: dict

    def __post_init__(self) -> None:
        super().__post_init__()
        self.staff_dept_structure = self.staff_dept_structure()
        self.structured_lessons = self.process_lessons()
        self.control_lessons = self.control_lessons()

    # def __init__(
    #     self,
    #     year: int,
    #     month: int,
    #     lesson_staff: dict,
    #     load_subgroup: dict,
    #     load_group: dict,
    #     plan_education_plans_education_form: dict,
    #     plan_education_plan: dict,
    # ):
    #     self.year = year
    #     self.month = month
    #     self.departments = get_departments()
    #     self.lesson_staff = lesson_staff
    #     self.load_subgroups = load_subgroup
    #     self.load_groups = load_group
    #     self.plan_education_plans_education_forms = plan_education_plans_education_form
    #     self.plan_education_plans = plan_education_plan
    #     self.education_staff = EducationStaff(month, year)
    #     self.staff_dept_structure = self.staff_dept_structure()
    #     self.structured_lessons = self.process_lessons()
    #     self.control_lessons = self.control_lessons()

    def staff_dept_structure(self):
        """
        Department ID for prepod in current month
        {staff_id:department_id}.
        """
        structure = {}
        for dept in self.departments:
            staff_list = self.department_staff(dept)
            for staff in staff_list:
                structure[staff] = dept
        return structure

    def process_lessons(self):
        """Current month lessons list with all data for load report"""
        structured_lessons = []
        if self.month == "январь-август":
            month_list = [1, 2, 3, 4, 5, 6, 7, 8]
        elif self.month == "сентябрь-декабрь":
            month_list = [9, 10, 11, 12]
        else:
            month_list = [int(self.month)]
        for month in month_list:
            for lesson in get_lessons(self.year, month):
                if not lesson.get("group_id"):
                    if lesson.get("subgroup_id"):
                        lesson["group_id"] = self.load_subgroups[
                            lesson.get("subgroup_id")
                        ].get("group_id")
                education_plan_id = self.load_groups.get(lesson.get("group_id"))[
                    "education_plan_id"
                ]
                education_form_id = self.plan_education_plans_education_forms.get(
                    education_plan_id
                )
                education_level_id = self.plan_education_plans.get(education_plan_id)[
                    "education_level_id"
                ]
                lesson["education_plan_id"] = education_plan_id
                lesson["education_form_id"] = education_form_id
                lesson["education_level_id"] = education_level_id
                if lesson.get("id") in self.lessons_staff:
                    for staff in self.lessons_staff[lesson["id"]]:
                        less_copy = copy(lesson)
                        less_copy["staff_id"] = int(staff)
                        less_copy["department_id"] = self.staff_dept_structure.get(
                            int(staff)
                        )
                        less_copy["hours"] = 2
                        structured_lessons.append(less_copy)
        return structured_lessons

    def control_lessons(self):
        """Получения занятий типа контроль (зачет, экзамен)"""

        def check_and_process(lesson):
            """Сверка типа занятия для определения типа контроль"""
            lookup = [
                "staff_id",
                "discipline_id",
                "group_id",
                "control_type_id",
                "date",
            ]
            counter = 0
            for c in control_less:
                if [lesson[val] for val in lookup] == [c[val] for val in lookup]:
                    c["hours"] += 2
                    c["lesson_time_id"] = (
                        c.get("lesson_time_id") + ", " + lesson.get("lesson_time_id")
                    )
                    counter += 1
            if counter != 0:
                return True
            else:
                return False

        control_less = []
        for less in self.structured_lessons:
            if less.get("control_type_id") in [
                str(Apeks.CONTROL_TYPE_ID.get(i))
                for i in ("exam", "zachet", "zachet_mark", "final_att", "kandidat_exam")
            ]:
                if not check_and_process(less):
                    control_less.append(copy(less))
        return control_less

    def get_control_hours(self, contr_less):
        """
        Getting hours for control lessons depending on students number,
        education type etc...
        Если значение больше максимального, возвращаем максимальное
        """
        cont_type = get_lesson_type(contr_less)
        stud_type = get_student_type(contr_less)
        if contr_less.get("subgroup_id"):  # If subgroup - get people count from it
            subgroup_id = contr_less.get("subgroup_id")
            people_count = self.load_subgroups[subgroup_id].get("people_count")
        else:
            group_id = contr_less.get("group_id")
            people_count = self.load_groups[group_id].get("people_count")
        if stud_type == "prof_p" or stud_type == "dpo":
            return contr_less["hours"]
        elif stud_type == "adj" and (
            contr_less.get("control_type_id") == Apeks.CONTROL_TYPE_ID.get("final_att")
            or contr_less.get("control_type_id")
            == Apeks.CONTROL_TYPE_ID.get("kandidat_exam")
        ):
            value = int(people_count) * Apeks.ADJ_KF
            return Apeks.ADJ_KF_MAX if value > Apeks.ADJ_KF_MAX else value
        elif cont_type == "zachet":
            value = int(people_count) * Apeks.ZACH_KF
            return Apeks.ZACH_KF_MAX if value > Apeks.ZACH_KF_MAX else value
        elif cont_type == "exam":
            value = int(people_count) * Apeks.EXAM_KF
            return Apeks.EXAM_KF_MAX if value > Apeks.EXAM_KF_MAX else value
        elif cont_type == "final_att":
            value = int(people_count) * Apeks.FINAL_KF
            return Apeks.FINAL_KF_MAX if value > Apeks.FINAL_KF_MAX else value

    def unknown_lessons(self):
        """
        Lessons with inactive staff
        (which doesn't work in department in selected time).
        """
        unknown = []
        for less in self.structured_lessons:
            if not less.get("department_id"):
                unknown.append(less)
        return unknown

    def department_lessons(self, department_id):
        """Select department lessons for load report"""
        dept_lessons = []
        for less in self.structured_lessons:
            if less.get("department_id") == int(department_id):
                dept_lessons.append(less)
        return dept_lessons