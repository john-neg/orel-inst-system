from __future__ import annotations

from dataclasses import dataclass

from config import ApeksConfig as Apeks


@dataclass(repr=False, eq=False)
class WorkProgram:
    """
    Сведения о рабочей программе.

    Attributes:
    ----------
        work_programs_data: dict
            данные о рабочих программах
            вывод функции 'get_work_programs_data'

    Methods:
    -------
        get_parameter_info(self, wp_id, parameter: str) -> str:
            возвращает информацию содержащуюся в поле рабочей программы
    """

    wp_id: int | str
    work_programs_data: dict

    def __post_init__(self) -> None:
        self.name = self.work_programs_data.get("name")

    def get_parameter_info(self, parameter: str) -> str:
        """"""
        if parameter in Apeks.MM_SECTIONS:
            if parameter in self.work_programs_data[self.wp_id]['sections']:
                return self.work_programs_data[self.wp_id]['sections'].get(parameter)
            else:
                return "non_exist"
        elif parameter in Apeks.MM_WORK_PROGRAMS_DATA:
            field_id = Apeks.MM_WORK_PROGRAMS_DATA.get(parameter)
            if field_id in self.work_programs_data[self.wp_id]['fields']:
                return self.work_programs_data[self.wp_id]['fields'].get(field_id)
            else:
                return "non_exist"
        elif parameter == "department_data":
            date_department = self.work_programs_data[self.wp_id].get('date_department')
            document_department = self.work_programs_data[self.wp_id].get('document_department')
            if date_department:
                d = date_department.split("-")
                date_department = f"{d[-1]}.{d[-2]}.{d[-3]}"
            else:
                date_department = "[Не заполнена]"
            if document_department is None:
                document_department = "[Отсутствует]"
            return f"Дата заседания кафедры: {date_department}\r\nПротокол № {document_department}"
        else:
            return self.work_programs_data[self.wp_id].get(parameter)