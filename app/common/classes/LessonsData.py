from __future__ import annotations

from copy import copy
from dataclasses import dataclass
from datetime import date, timedelta

from app.common.classes.EducationStaff import EducationStaff
from app.common.func import data_processor

from config import ApeksConfig as Apeks


@dataclass
class LessonsData:
    """
    Класс обрабатывает и формирует полные сведения об учебных занятиях

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
        staff_history_data: dict
            словарь с данными в каком подразделении и когда работал
            сотрудник {id: [{'department_id': 'value',
            'start_date': 'date', 'end_date': 'date'}]

    Methods:
    -------
        lessons_staff_processor (lessons_staff: dict) -> dict
            обрабатывает данные таблицы lessons_staff,
            выводит словарь в формате: {lesson_id: [staff_id]}
        def process_lessons -> list:
            возвращает обработанный список занятий с добавленными
            данными о кафедре, форме обучения, уровне образования
        def get_control_lessons -> list:
            возвращает список занятий типа контроль (зачет, экзамен)
        def get_lesson_type (lesson: dict) -> str:
            определяет и возвращает тип занятия или контроля.
        def get_student_type (lesson: dict) -> str:
            Определяет и возвращает тип обучающегося.
        def get_control_hours (contr_less: dict) -> int | float:
            возвращает количество часов для занятий, относящихся к формам
            контроля в зависимости от часов и коэффициентов образовательной
            организации. Если значение больше максимального, возвращаем
            максимальное (= аудиторное)
        def unknown_lessons -> list:
            возвращает список занятий, для которых не удалось определить
            кафедру, т.к. преподаватель не работает ни на одной кафедре
            в указанное время.
        def department_lessons (department_id: int) -> list:
            возвращает список занятий, относящихся к определенной кафедре
    """

    schedule_lessons: list
    schedule_lessons_staff: list
    load_groups: list
    load_subgroups: list
    plan_education_plans: list
    plan_education_plans_education_forms: list
    staff_history_data: dict

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
        self.structured_lessons = self.process_lessons()
        self.control_lessons = self.get_control_lessons()

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

    def process_lessons(self) -> list:
        """
        Возвращает обработанный список занятий с добавленными данными
        о кафедре, форме обучения, уровне образования

        Returns
        -------
            list
                полный список занятий
        """
        structured_lessons = []
        for lesson in self.schedule_lessons:
            group_id = lesson.get("group_id")
            if not group_id:
                subgroup_id = lesson.get("subgroup_id")
                if subgroup_id:
                    group_id = self.subgroups_data[int(subgroup_id)].get("group_id")
                    lesson["group_id"] = group_id
            education_plan_id = self.groups_data.get(int(group_id))["education_plan_id"]
            lesson["education_plan_id"] = education_plan_id
            lesson["education_form_id"] = self.plans_education_forms_data.get(
                int(education_plan_id)
            ).get("education_form_id")
            lesson["education_level_id"] = self.education_plans_data.get(
                int(education_plan_id)
            ).get("education_level_id")
            lesson_id = lesson.get("id")
            if lesson_id:
                if int(lesson_id) in self.lessons_staff_data:
                    for staff in self.lessons_staff_data.get(int(lesson_id)):
                        # Копируем для того чтобы одно занятие учитывалось
                        # разным преподавателям (когда проводят двое, трое и т.д.)
                        less_copy = copy(lesson)
                        less_copy["staff_id"] = int(staff)

                        for dept in self.staff_history_data.get(int(staff)):
                            lesson_date = date.fromisoformat(lesson.get("date"))
                            start_date = date.fromisoformat(dept.get("start_date"))
                            end_date = (
                                date.fromisoformat(dept.get("end_date"))
                                if dept.get("end_date")
                                else date.today() + timedelta(days=365)
                            )
                            if start_date <= lesson_date <= end_date:
                                less_copy["department_id"] = dept.get("department_id")
                                less_copy["hours"] = 2
                                structured_lessons.append(less_copy)
        return structured_lessons

    def get_control_lessons(self) -> list:
        """
        Возвращает список занятий типа контроль (зачет, экзамен)

        Returns
        -------
            list
                список занятий типа контроль
        """

        def check_and_process(lesson: dict) -> bool:
            """
            Проверяет формируемый список занятий и в случае нахождения
            аналогичного занятия из группы контроль не добавляет его в
            список, а увеличивает количество часов.

            Returns
            -------
                bool
                    True - если занятие найдено и обработано
                    False - если нет
            """
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
                str(Apeks.CONTROL_TYPE_ID.get(c_type))
                for c_type in (
                    "exam",
                    "zachet",
                    "zachet_mark",
                    "final_att",
                    "kandidat_exam",
                )
            ]:
                if not check_and_process(less):
                    control_less.append(copy(less))
        return control_less

    @staticmethod
    def get_lesson_type(lesson: dict) -> str:
        """
        Определяет и возвращает тип занятия или контроля.

        Parameters
        ----------
            lesson: dict
                словарь с данными об аудиторном занятии

        Returns
        -------
            str
                тип занятия
                (lecture, seminar, pract, group_cons, zachet, exam, final_att)
        """
        # Лекция
        if lesson.get("class_type_id") == str(Apeks.CLASS_TYPE_ID.get("lecture")):
            l_type = "lecture"
        # Семинар
        elif lesson.get("class_type_id") == str(Apeks.CLASS_TYPE_ID.get("seminar")):
            l_type = "seminar"
        # Практическое занятие (+ вх, вых. контроль)
        elif (
            lesson.get("class_type_id") == str(Apeks.CLASS_TYPE_ID.get("prakt"))
            or lesson.get("control_type_id")
            == str(Apeks.CONTROL_TYPE_ID.get("in_control"))
            or lesson.get("control_type_id")
            == str(Apeks.CONTROL_TYPE_ID.get("out_control"))
        ):
            l_type = "pract"
        # Групповая консультация
        elif lesson.get("control_type_id") == str(
            Apeks.CONTROL_TYPE_ID.get("group_cons")
        ):
            l_type = "group_cons"
        # Зачет (+ зачет с оценкой, + итоговая письменная аудиторная к/р)
        elif (
            lesson.get("control_type_id") == str(Apeks.CONTROL_TYPE_ID.get("zachet"))
            or lesson.get("control_type_id")
            == str(Apeks.CONTROL_TYPE_ID.get("zachet_mark"))
            or lesson.get("control_type_id")
            == str(Apeks.CONTROL_TYPE_ID.get("itog_kontr"))
        ):
            l_type = "zachet"
        # Экзамен (+ кандидатский экзамен)
        elif lesson.get("control_type_id") == str(
            Apeks.CONTROL_TYPE_ID.get("exam")
        ) or lesson.get("control_type_id") == str(
            Apeks.CONTROL_TYPE_ID.get("kandidat_exam")
        ):
            l_type = "exam"
        # Итоговая аттестация
        elif lesson.get("control_type_id") == str(
            Apeks.CONTROL_TYPE_ID.get("final_att")
        ):
            l_type = "final_att"
        else:
            l_type = None
        return l_type

    @staticmethod
    def get_student_type(lesson: dict) -> str:
        """
        Определяет и возвращает тип обучающегося.

        Parameters
        ----------
            lesson: dict
                словарь с данными об аудиторном занятии

        Returns
        -------
            str
                тип обучающегося
                (och, zo_high, zo_mid, adj, prof_p, dpo)
        """

        # проф подготовка (+ временный "костыль" ПП Цифр. грамотность - id: 549)
        if (
            lesson.get("education_form_id")
            == str(Apeks.EDUCATION_FORM_ID.get("prof_pod"))
            or lesson.get("discipline_id") == "549"
        ):
            s_type = "prof_p"
        # очно, бакалавр или специалитет
        elif lesson.get("education_form_id") == str(
            Apeks.EDUCATION_FORM_ID.get("ochno")
        ) and (
            lesson.get("education_level_id") == str(Apeks.EDUCATION_LEVEL_ID.get("bak"))
            or lesson.get("education_level_id")
            == str(Apeks.EDUCATION_LEVEL_ID.get("spec"))
        ):
            s_type = "och"
        # заочно, бакалавр или специалитет
        elif lesson.get("education_form_id") == str(
            Apeks.EDUCATION_FORM_ID.get("zaochno")
        ) and (
            lesson.get("education_level_id") == str(Apeks.EDUCATION_LEVEL_ID.get("bak"))
            or lesson.get("education_level_id")
            == str(Apeks.EDUCATION_LEVEL_ID.get("spec"))
        ):
            s_type = "zo_high"
        # заочно, среднее
        elif lesson.get("education_form_id") == str(
            Apeks.EDUCATION_FORM_ID.get("zaochno")
        ) and lesson.get("education_level_id") == str(
            Apeks.EDUCATION_LEVEL_ID.get("spo")
        ):
            s_type = "zo_mid"
        # адъюнктура
        elif lesson.get("education_level_id") == str(
            Apeks.EDUCATION_LEVEL_ID.get("adj")
        ):
            s_type = "adj"
        # дополнительное проф образование
        elif lesson.get("education_form_id") == str(Apeks.EDUCATION_FORM_ID.get("dpo")):
            s_type = "dpo"
        else:
            s_type = None
        return s_type

    def get_control_hours(self, contr_less: dict) -> int | float:
        """
        Возвращает количество часов для занятий, относящихся к формам
        контроля в зависимости от часов и коэффициентов образовательной
        организации. Если значение больше максимального, возвращает
        максимальное (= аудиторное)

        Parameters
        ----------
            contr_less: dict
                словарь с данными о занятии типа контроль

        Returns
        -------
            int | float
                количество академических часов
        """
        cont_type = self.get_lesson_type(contr_less)
        stud_type = self.get_student_type(contr_less)
        if contr_less.get("subgroup_id"):  # If subgroup - get people count from it
            subgroup_id = contr_less.get("subgroup_id")
            people_count = self.load_subgroups[int(subgroup_id)].get("people_count")
        else:
            group_id = contr_less.get("group_id")
            people_count = self.load_groups[int(group_id)].get("people_count")
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

    def unknown_lessons(self) -> list:
        """
        Возвращает список занятий, для которых не удалось определить кафедру,
        т.к. преподаватель не работает ни на одной кафедре в указанное время.
        """
        unknown = []
        for less in self.structured_lessons:
            if not less.get("department_id"):
                unknown.append(less)
        return unknown

    # def department_lessons(self, department_id: int) -> list:
    #     """Возвращает список занятий, относящихся к определенной кафедре"""
    #     dept_lessons = []
    #     for less in self.structured_lessons:
    #         if less.get("department_id") == int(department_id):
    #             dept_lessons.append(less)
    #     return dept_lessons


# 'schedule_day_schedule_lessons' - занятия
# 'schedule_day_schedule_lessons_staff' - staff_id для каждого занятия {lesson_id:staff_id}
# 'load_subgroups' - подгруппы
# 'load_groups'
# 'plan_education_plans_education_forms'
# 'plan_education_plans'


# import requests
# from pprint import pprint
# from config import ApeksConfig as Apeks
#
#
#
# def db_request(table_name, **kwargs):
#     """DB request function without filter."""
#     endpoint = f"{Apeks.URL}/api/call/system-database/get"
#     params = {"token": Apeks.TOKEN, "table": table_name}
#     if kwargs:
#         for db_filter, db_value in kwargs.items():
#             params[f"filter[{db_filter}]"] = str(db_value)
#     response = requests.get(endpoint, params=params)
#     return response.json()["data"]
#
# #
#
# pprint(db_request("schedule_day_schedule_lessons", journal_lesson_id=13229))


# from app.common.classes.EducationStaff import EducationStaff
# from app.common.func import (
#     get_departments,
#     get_state_staff,
#     check_api_db_response,
#     api_get_db_table,
#     check_api_staff_lessons_response,
#     api_get_staff_lessons,
#     get_disciplines,
#     data_processor,
#     get_lessons,
# )
#
# import asyncio
# from pprint import pprint
#
# year = 2022
# month_start = 5
# month_end = 5
#
#
# async def main():
#     staff = EducationStaff(
#         year,
#         month_start,
#         month_end,
#         state_staff=await get_state_staff(),
#         state_staff_history=await check_api_db_response(
#             await api_get_db_table(Apeks.TABLES.get("state_staff_history"))
#         ),
#         state_staff_positions=await check_api_db_response(
#             await api_get_db_table(Apeks.TABLES.get("state_staff_positions"))
#         ),
#         departments=await get_departments(),
#     )
#
#     data = LessonsData(
#         schedule_lessons=await check_api_db_response(await get_lessons(year, month_start, month_end)),
#         schedule_lessons_staff=await check_api_db_response(
#             await api_get_db_table(
#                 Apeks.TABLES.get("schedule_day_schedule_lessons_staff")
#             )
#         ),
#         load_groups=await check_api_db_response(
#             await api_get_db_table(Apeks.TABLES.get("load_groups"))
#         ),
#         load_subgroups=await check_api_db_response(
#             await api_get_db_table(Apeks.TABLES.get("load_subgroups"))
#         ),
#         plan_education_plans=await check_api_db_response(
#             await api_get_db_table(Apeks.TABLES.get("plan_education_plans"))
#         ),
#         plan_education_plans_education_forms=await check_api_db_response(
#             await api_get_db_table(
#                 Apeks.TABLES.get("plan_education_plans_education_forms")
#             )
#         ),
#         staff_history_data=staff.staff_history(),
#     )
#
#     pprint(data.unknown_lessons())
#
#
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
#     loop.close()

