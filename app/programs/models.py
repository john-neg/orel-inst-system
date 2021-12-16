import requests
from app.main.func import (
    plan_curriculum_disciplines,
    db_filter_req,
    get_active_staff_id,
    get_data,
)
from app.programs.func import plan_department_disciplines
from config import ApeksAPI


class ApeksDeptData:
    def __init__(self):
        self.active_staff_id = get_active_staff_id()
        self.data = get_data(self.active_staff_id)
        self.departments = self.data["departments"]


class WorkProgram:
    def __init__(self, curriculum_discipline_id):
        self.curriculum_discipline_id = curriculum_discipline_id
        self.mm_work_programs = db_filter_req(
            "mm_work_programs", "curriculum_discipline_id", curriculum_discipline_id
        )
        self.work_program_id = self.mm_work_programs[0]["id"]
        self.name = self.mm_work_programs[0]["name"]
        self.mm_work_programs_items = {
            "name": "name",  # Название программы
            "reviewers_ext": "reviewers_ext",  # Рецензенты
            "date_approval": "date_approval",
            "date_methodical": "date_methodical",
            "document_methodical": "document_methodical",
            "date_academic": "date_academic",
            "document_academic": "document_academic",
        }
        self.special = {
            "date_department": "date_department",  # Дата заседания кафедры
            "document_department": "document_department",  # Протокол заседания кафедры
        }
        self.mm_sections_items = {
            "purposes": "purposes",  # Цели
            "tasks": "tasks",  # Задачи
            "place_in_structure": "place_in_structure",  # Место в структуре ООП
        }
        self.mm_work_programs_data_items = {
            "authorprint": 29,  # Автор(ы) рабочей программы (для печати)
            "no_next_disc": 30,  # Пояснение к таблице с последующими дисциплинами (информация об отсутствии)
            "templan_info": 31,  # Примечание к тематическому плану
            "self_provision": 8,  # Обеспечение самостоятельной работы
            "test_criteria": 32,  # Критерии оценки для сдачи промежуточной аттестации в форме тестирования
            "course_works": 12,  # Тематика курсовых работ
            "practice": 10,  # Практикум
            "control_works": 13,  # Тематика контрольных работ
            "exam_form_desc": 33,  # Примерные оценочные средства для проведения промежуточной аттестации
            "task_works": 9,  # Задачи
            "tests": 19,  # Тесты
            "regulations": 16,  # Нормативные акты
            "library_main": 1,  # Основная литература
            "library_add": 2,  # Дополнительная литература
            "library_np": 3,  # Научная продукция
            "internet": 18,  # Ресурсы информационно-телекоммуникационной сети Интернет
            "software": 15,  # Программное обеспечение
            "ref_system": 17,  # Базы данных, информационно-справочные и поисковые системы
            "materials_base": 20,  # Описание материально-технической базы
        }

    def get(self, parameter):
        if parameter in self.mm_work_programs_items:
            return self.mm_work_programs[0][self.mm_work_programs_items.get(parameter)]
        elif parameter in self.special:
            date_department = self.mm_work_programs[-1]["date_department"]
            document_department = self.mm_work_programs[-1]["document_department"]
            if date_department:
                date = date_department.split("-")
                date_department = f"{date[-1]}.{date[-2]}.{date[-3]}"
            else:
                date_department = "[Не заполнена]"
            if document_department is None:
                document_department = "[Отсутствует]"
            return f"Дата заседания кафедры: {date_department}\r\nПротокол № {document_department}"
        elif parameter in self.mm_sections_items:
            return db_filter_req(
                "mm_sections", "work_program_id", self.work_program_id
            )[-1][self.mm_sections_items.get(parameter)]
        elif parameter in self.mm_work_programs_data_items:
            try:
                params = {
                    "token": ApeksAPI.TOKEN,
                    "table": "mm_work_programs_data",
                    "filter[work_program_id]": self.work_program_id,
                    "filter[field_id]": str(
                        self.mm_work_programs_data_items.get(parameter)
                    ),
                }
                return requests.get(
                    ApeksAPI.URL + "/api/call/system-database/get", params=params
                ).json()["data"][-1]["data"]
            except IndexError:
                return ""
        else:
            return "Wrong parameter"

    def edit(self, parameter, load_data):
        def mm_work_programs_items(parameter, load_data):
            params = {"token": ApeksAPI.TOKEN}
            data = {
                "table": "mm_work_programs",
                "filter[id]": self.work_program_id,
                "fields["
                + self.mm_work_programs_items.get(parameter)
                + "]": str(load_data),
            }
            requests.post(
                ApeksAPI.URL + "/api/call/system-database/edit",
                params=params,
                data=data,
            )
        if parameter in self.mm_work_programs_items:
            mm_work_programs_items(parameter, load_data)
            self.mm_work_programs = db_filter_req(
                "mm_work_programs",
                "curriculum_discipline_id",
                self.curriculum_discipline_id,
            )
        elif parameter in self.special:
            ## Проверить!!!
            count = 0
            for param in self.special:
                data = load_data.split(" ")[count]
                mm_work_programs_items(param, data)
                count += 1
            self.mm_work_programs = db_filter_req(
                "mm_work_programs",
                "curriculum_discipline_id",
                self.curriculum_discipline_id,
            )
        elif parameter in self.mm_sections_items:
            params = {"token": ApeksAPI.TOKEN}
            data = {
                "table": "mm_sections",
                "filter[work_program_id]": self.work_program_id,
                "fields[" + self.mm_sections_items.get(parameter) + "]": str(load_data),
            }
            r = requests.post(
                ApeksAPI.URL + "/api/call/system-database/edit",
                params=params,
                data=data,
            )
            return r.json()
        elif parameter in self.mm_work_programs_data_items:
            params = {"token": ApeksAPI.TOKEN}
            data = {
                "table": "mm_work_programs_data",
                "filter[work_program_id]": self.work_program_id,
                "filter[field_id]": self.mm_work_programs_data_items.get(parameter),
                "fields[data]": str(load_data),
            }
            r = requests.post(
                ApeksAPI.URL + "/api/call/system-database/edit",
                params=params,
                data=data,
            )
            return r.json()
        else:
            return "Wrong parameter"


class WorkProgramBunchData:
    def __init__(self, education_plan_id, parameter):
        self.parameter = parameter
        self.education_plan_id = education_plan_id

    def all(self):
        disc_list = plan_curriculum_disciplines(self.education_plan_id)
        return self.wp_list_processing(disc_list)

    def department(self, department_id):
        disc_list = plan_department_disciplines(self.education_plan_id, department_id)
        return self.wp_list_processing(disc_list)

    def wp_list_processing(self, disc_list):
        result = {}
        for disc in disc_list:
            try:
                wp = WorkProgram(disc)
            except IndexError:
                result[" ".join(disc_list[disc])] = "-->Программа отсутствует<--"
                break
            try:
                result[" ".join(disc_list[disc])] = wp.get(self.parameter)
            except IndexError:
                result[" ".join(disc_list[disc])] = ""
        return result
