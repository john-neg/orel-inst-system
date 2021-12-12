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


class WorkProgramData:
    def __init__(self):
        self.disc_list = []

    def mm_work_programs(self, field):
        """Метод для работы с таблицей mm_work_programs (общие данные о рабочих программах)
        (индекс -1 чтобы бралось более новое значение если их более 1)"""
        response = {}
        for disc in self.disc_list:
            try:
                response[" ".join(self.disc_list[disc])] = db_filter_req(
                    "mm_work_programs", "curriculum_discipline_id", disc
                )[-1][field]
            except IndexError:
                response[" ".join(self.disc_list[disc])] = "-->Программа отсутствует<--"
        return response

    def names(self):
        """Получение имен рабочих программ"""
        return self.mm_work_programs("name")

    def reviewers_ext(self):
        """Получение рецензентов рабочих программ"""
        return self.mm_work_programs("reviewers_ext")

    def date_department(self):
        """Получение даты утверждения и номера протокола кафедры"""
        response = {}
        for disc in self.disc_list:
            try:
                data = db_filter_req(
                    "mm_work_programs", "curriculum_discipline_id", disc
                )
                date_department = data[-1]["date_department"]
                document_department = data[-1]["document_department"]
                if date_department:
                    date = date_department.split("-")
                    date_department = f"{date[-1]}.{date[-2]}.{date[-3]}"
                else:
                    date_department = "[Не заполнена]"
                if document_department is None:
                    document_department = "[Отсутствует]"
                response[
                    " ".join(self.disc_list[disc])
                ] = f"Дата заседания кафедры: {date_department}\r\nПротокол № {document_department}"
            except IndexError:
                response[" ".join(self.disc_list[disc])] = "-->Программа отсутствует<--"
        return response

    def mm_sections(self, field):
        """Метод для работы с таблицей mm_sections (цели, задачи...)"""
        response = {}
        for disc in self.disc_list:
            try:
                wp_id = db_filter_req(
                    "mm_work_programs", "curriculum_discipline_id", disc
                )[0]["id"]
            except IndexError:
                response[" ".join(self.disc_list[disc])] = "-->Программа отсутствует<--"
            else:
                try:
                    response[" ".join(self.disc_list[disc])] = db_filter_req(
                        "mm_sections", "work_program_id", wp_id
                    )[-1][field]
                except IndexError:
                    response[" ".join(self.disc_list[disc])] = ""
        return response

    def purposes(self):
        """Цели"""
        return self.mm_sections("purposes")

    def tasks(self):
        """Задачи"""
        return self.mm_sections("tasks")

    def place_in_structure(self):
        """Место в структуре ООП"""
        return self.mm_sections("place_in_structure")

    def mm_work_programs_data(self, field_id):
        """Метод для работы с таблицей mm_work_programs_data (произвольные поля программ)"""
        response = {}
        for disc in self.disc_list:
            try:
                wp_id = db_filter_req(
                    "mm_work_programs", "curriculum_discipline_id", disc
                )[0]["id"]
            except IndexError:
                response[" ".join(self.disc_list[disc])] = "-->Программа отсутствует<--"
            else:
                try:
                    params = {
                        "token": ApeksAPI.TOKEN,
                        "table": "mm_work_programs_data",
                        "filter[work_program_id]": wp_id,
                        "filter[field_id]": field_id,
                    }
                    resp = requests.get(
                        ApeksAPI.URL + "/api/call/system-database/get", params=params
                    ).json()["data"]

                    response[" ".join(self.disc_list[disc])] = resp[-1]["data"]
                except IndexError:
                    response[" ".join(self.disc_list[disc])] = ""
        return response

    def authorprint(self):
        """Автор(ы) рабочей программы (для печати)"""
        field_id = 29
        return self.mm_work_programs_data(field_id)

    def no_next_disc(self):
        """Пояснение к таблице с последующими дисциплинами (информация об отсутствии)"""
        field_id = 30
        return self.mm_work_programs_data(field_id)

    def templan_info(self):
        """Примечание к тематическому плану"""
        field_id = 31
        return self.mm_work_programs_data(field_id)

    def self_provision(self):
        """Обеспечение самостоятельной работы"""
        field_id = 8
        return self.mm_work_programs_data(field_id)

    def test_criteria(self):
        """Критерии оценки для сдачи промежуточной аттестации в форме тестирования"""
        field_id = 32
        return self.mm_work_programs_data(field_id)

    def course_works(self):
        """Тематика курсовых работ"""
        field_id = 12
        return self.mm_work_programs_data(field_id)

    def practice(self):
        """Практикум"""
        field_id = 10
        return self.mm_work_programs_data(field_id)

    def control_works(self):
        """Тематика контрольных работ"""
        field_id = 13
        return self.mm_work_programs_data(field_id)

    def exam_form_desc(self):
        """Примерные оценочные средства для проведения промежуточной аттестации обучающихся по дисциплине"""
        field_id = 33
        return self.mm_work_programs_data(field_id)

    def task_works(self):
        """Задачи"""
        field_id = 9
        return self.mm_work_programs_data(field_id)

    def tests(self):
        """Тесты"""
        field_id = 19
        return self.mm_work_programs_data(field_id)

    def regulations(self):
        """Нормативные акты"""
        field_id = 16
        return self.mm_work_programs_data(field_id)

    def internet(self):
        """Ресурсы информационно-телекоммуникационной сети Интернет"""
        field_id = 18
        return self.mm_work_programs_data(field_id)

    def software(self):
        """Программное обеспечение"""
        field_id = 15
        return self.mm_work_programs_data(field_id)

    def ref_system(self):
        """Базы данных, информационно-справочные и поисковые системы"""
        field_id = 17
        return self.mm_work_programs_data(field_id)

    def materials_base(self):
        """Описание материально-технической базы"""
        field_id = 20
        return self.mm_work_programs_data(field_id)


class WorkProgramBunchData(WorkProgramData):
    def __init__(self, education_plan_id):
        """Данные РП по учебному плану"""
        super().__init__()
        self.disc_list = plan_curriculum_disciplines(education_plan_id)


class WorkProgramDeptData(WorkProgramData):
    def __init__(self, education_plan_id, department_id):
        """Данные РП по кафедре"""
        super().__init__()
        self.disc_list = plan_department_disciplines(education_plan_id, department_id)
