from datetime import datetime, date

import requests

from app.main.func import (
    plan_curriculum_disciplines,
    db_filter_req,
    get_system_user_name,
    add_wp_field,
)
from app.programs.func import plan_department_disciplines
from config import ApeksConfig as Apeks


class WorkProgram:
    def __init__(self, curriculum_discipline_id):
        self.curriculum_discipline_id = curriculum_discipline_id
        self.mm_work_programs = db_filter_req(
            "mm_work_programs",
            "curriculum_discipline_id",
            curriculum_discipline_id
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
            "status": "status",
        }
        self.special = {
            "date_department": "date_department",  # Дата заседания кафедры
            "document_department": "document_department",  # Протокол заседания кафедры
            "department_data": "department_data"
        }
        self.mm_sections_items = {
            "purposes": "purposes",  # Цели дисциплины
            "tasks": "tasks",  # Задачи дисциплины
            "place_in_structure": "place_in_structure",  # Место в структуре ООП
        }
        self.mm_work_programs_data_items = Apeks.MM_WORK_PROGRAMS_DATA

    def get(self, parameter):
        """Get work program field data."""
        if parameter in self.mm_work_programs_items:
            return self.mm_work_programs[0][self.mm_work_programs_items.get(parameter)]
        elif parameter in self.special:
            date_department = self.mm_work_programs[-1]["date_department"]
            document_department = self.mm_work_programs[-1]["document_department"]
            if date_department:
                d = date_department.split("-")
                date_department = f"{d[-1]}.{d[-2]}.{d[-3]}"
            else:
                date_department = "[Не заполнена]"
            if document_department is None:
                document_department = "[Отсутствует]"
            return f"Дата заседания кафедры: {date_department}\r\n" \
                   f"Протокол № {document_department}"
        elif parameter in self.mm_sections_items:
            try:
                data = db_filter_req(
                    "mm_sections", "work_program_id", self.work_program_id
                )[-1][self.mm_sections_items.get(parameter)]
                return data
            except IndexError:
                params = {"token": Apeks.TOKEN}
                data = {
                    "table": "mm_sections",
                    "fields[work_program_id]": self.work_program_id,
                }
                requests.post(
                    Apeks.URL + "/api/call/system-database/add",
                    params=params,
                    data=data,
                )
                return ""
        elif parameter in self.mm_work_programs_data_items:
            try:
                params = {
                    "token": Apeks.TOKEN,
                    "table": "mm_work_programs_data",
                    "filter[work_program_id]": self.work_program_id,
                    "filter[field_id]": str(
                        self.mm_work_programs_data_items.get(parameter)
                    ),
                }
                return requests.get(
                    Apeks.URL + "/api/call/system-database/get",
                    params=params
                ).json()["data"][-1]["data"]
            except IndexError:
                add_wp_field(
                    self.work_program_id,
                    self.mm_work_programs_data_items.get(parameter)
                )
                return ""
        else:
            return "Wrong parameter"

    def edit(self, parameter, load_data):
        """Edit work program field data."""
        def mm_work_programs_items(f_param, f_data):
            mm_params = {"token": Apeks.TOKEN}
            mm_data = {
                "table": "mm_work_programs",
                "filter[id]": self.work_program_id,
                "fields[" + f_param + "]": f_data,
            }
            requests.post(
                Apeks.URL + "/api/call/system-database/edit",
                params=mm_params,
                data=mm_data,
            )
        if parameter in self.mm_work_programs_items:
            mm_work_programs_items(parameter, load_data)
            self.mm_work_programs = db_filter_req(
                "mm_work_programs",
                "curriculum_discipline_id",
                self.curriculum_discipline_id,
            )
        elif parameter in self.special:
            param = 'date_department'
            d = load_data.split("\r\n")[0].replace(
                "Дата заседания кафедры:", ""
            ).replace(" ", "")
            d = datetime.strptime(d, '%d.%m.%Y')
            data = date.isoformat(d)
            mm_work_programs_items(param, data)

            param = 'document_department'
            data = load_data.split("\r\n")[1].replace(
                "Протокол №", ""
            ).replace(" ", "")
            mm_work_programs_items(param, data)

            self.mm_work_programs = db_filter_req(
                "mm_work_programs",
                "curriculum_discipline_id",
                self.curriculum_discipline_id,
            )
        elif parameter in self.mm_sections_items:
            params = {"token": Apeks.TOKEN}
            data = {
                "table": "mm_sections",
                "filter[work_program_id]": self.work_program_id,
                "fields[" + self.mm_sections_items.get(parameter) +
                "]": str(load_data),
            }
            resp = requests.post(
                Apeks.URL + "/api/call/system-database/edit",
                params=params,
                data=data,
            )
            return resp.json()
        elif parameter in self.mm_work_programs_data_items:
            params = {"token": Apeks.TOKEN}
            data = {
                "table": "mm_work_programs_data",
                "filter[work_program_id]": self.work_program_id,
                "filter[field_id]": self.mm_work_programs_data_items.get(
                    parameter
                ),
                "fields[data]": str(load_data),
            }
            r = requests.post(
                Apeks.URL + "/api/call/system-database/edit",
                params=params,
                data=data,
            )
            return r.json()
        else:
            return "Wrong parameter"

    def get_signs(self):
        """Получение информации о согласовании программы."""
        signs_data = db_filter_req(
            'mm_work_programs_signs',
            'work_program_id',
            self.work_program_id
        )
        signs = []
        if signs_data:
            for sign in signs_data:
                signs.append(
                    f'{get_system_user_name(sign["user_id"])}\r\n' +
                    f'({sign["timestamp"]})'
                )
        else:
            signs.append("Не согласована")
        return signs


class WorkProgramBunchData:
    def __init__(self, education_plan_id, parameter):
        self.parameter = parameter
        self.education_plan_id = education_plan_id

    def all(self):
        disc_list = plan_curriculum_disciplines(self.education_plan_id)
        return self.wp_list_processing(disc_list)

    def department(self, department_id):
        disc_list = plan_department_disciplines(
            self.education_plan_id,
            department_id
        )
        return self.wp_list_processing(disc_list)

    def wp_list_processing(self, disc_list):
        result = {}
        for disc in disc_list:
            try:
                wp = WorkProgram(disc)
                try:
                    result[" ".join(disc_list[disc])] = [
                        wp.get(self.parameter),
                        disc
                    ]
                except IndexError:
                    result[" ".join(disc_list[disc])] = ["", disc]
            except IndexError:
                result[" ".join(disc_list[disc])] = [
                    "-->Программа отсутствует<--",
                    disc
                ]
        return result
