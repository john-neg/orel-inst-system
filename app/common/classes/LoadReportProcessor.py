from __future__ import annotations

from dataclasses import dataclass

from openpyxl import load_workbook
from openpyxl.styles import Font

from app.common.classes.ExcelStyle import ExcelStyle
from app.common.classes.LessonsData import LessonsData
from config import FlaskConfig, ApeksConfig as Apeks


@dataclass
class LoadReportProcessor(LessonsData):
    """
    Класс формирует отчет о нагрузке по кафедрам

    Attributes:
    ----------
        department_id: int
            id кафедры

    Methods:
    -------


    """
    year: int | str
    month_start: int | str
    month_end: int | str
    department_id: int
    departments: dict
    department_staff: dict

    def __post_init__(self) -> None:
        super().__post_init__()
        self.staff_list = self.department_staff
        self.load_data = {}
        self.unprocessed = []
        self.process_load_data()
        self.file_period = (
            Apeks.MONTH_DICT[int(self.month_start)]
            if self.month_start == self.month_end
            else f"{Apeks.MONTH_DICT[int(self.month_start)]}-"
            f"{Apeks.MONTH_DICT[int(self.month_end)]}"
        )
        self.filename = (
            f"{self.departments.get(self.department_id).get('short')} "
            f"{self.file_period} {self.year}.xlsx"
        )

    def add_load(
        self, staff_id: int, l_type: str, s_type: str, value: float = 2
    ) -> None:
        """
        Добавляет нагрузку в хранилище 'load_data'

        Parameters
        ----------
            staff_id: int
                id преподавателя
            l_type: str
                тип занятия
            s_type: str
                тип обучающегося
            value: float = 2
                значение
        """
        self.load_data[staff_id][l_type][s_type] += value

    def get_load(self, staff_id: int) -> dict:
        """
        Возвращает нагрузку преподавателя их хранилища 'load_data'

        Parameters
        ----------
            staff_id: int
                id преподавателя

        Returns
        -------
            dict
                {'short_name': {'exam': {'adj': 0,
                               'dpo': 0,
                               'och': 0,
                               'prof_p': 0,
                               'zo_high': 0,
                               'zo_mid': 0},

        """
        staff_load = {self.staff_list[staff_id]: self.load_data[staff_id]}
        return staff_load

    def process_load_data(self) -> None:
        """Рассчитывает нагрузку по преподавателям"""
        lesson_types = Apeks.LOAD_LESSON_TYPES + Apeks.LOAD_CONTROL_TYPES
        for staff_id in self.staff_list:
            self.load_data[staff_id] = {}
            for l_type in lesson_types:
                self.load_data[staff_id][l_type] = {}
                for s_type in Apeks.LOAD_STUDENT_TYPES:
                    self.load_data[staff_id][l_type][s_type] = 0
        for lesson in self.structured_lessons:
            department_id = lesson.get("department_id")
            if department_id:
                if int(department_id) == self.department_id:
                    staff_id = lesson.get("staff_id")
                    l_type = self.get_lesson_type(lesson)
                    s_type = self.get_student_type(lesson)
                    if staff_id and l_type and s_type:
                        if l_type in Apeks.LOAD_LESSON_TYPES:
                            self.add_load(staff_id, l_type, s_type)
                    else:
                        self.unprocessed.append(lesson)
        for control in self.control_lessons:
            department_id = control.get("department_id")
            if department_id:
                if int(department_id) == self.department_id:
                    staff_id = control.get("staff_id")
                    l_type = self.get_lesson_type(control)
                    s_type = self.get_student_type(control)
                    if staff_id and l_type and s_type:
                        if l_type in Apeks.LOAD_CONTROL_TYPES:
                            value = self.get_control_hours(control)
                            self.add_load(staff_id, l_type, s_type, value)
                else:
                    self.unprocessed.append(control)

    def generate_report(self) -> None:
        """Формирование отчета о нагрузке в Excel."""

        wb = load_workbook(FlaskConfig.TEMP_FILE_DIR + "load_report_temp.xlsx")
        ws = wb.active
        ws.title = (
            f"{self.year}-{self.file_period} "
            f"{self.departments.get(self.department_id).get('short')}"
        )
        ws.cell(1, 1).value = "Кафедра " + self.departments.get(
            self.department_id
        ).get("full")
        ws.cell(2, 1).value = f"отчет о нагрузке за {self.file_period} {self.year}"
        row = 8
        for prepod in self.load_data:
            # Style apply
            for i in range(2, 73):
                ws.cell(row, i).style = ExcelStyle.Number
            # Prepod Name
            ws.cell(row, 1).value = self.staff_list[prepod]
            ws.cell(row, 1).style = ExcelStyle.Base
            for l_type in self.load_data[prepod]:
                if l_type == "lecture":
                    column = 2
                elif l_type == "seminar":
                    column = 8
                elif l_type == "pract":
                    column = 14
                elif l_type == "group_cons":
                    column = 24
                    if self.load_data[prepod][l_type]["dpo"]:
                        del self.load_data[prepod][l_type]["dpo"]
                elif l_type == "zachet":
                    column = 29
                elif l_type == "exam":
                    column = 35
                elif l_type == "final_att":
                    column = 59
                else:
                    column = 73
                for key, val in self.load_data[prepod][l_type].items():
                    val = "" if val == 0 else val
                    ws.cell(row, column).value = val
                    if val and val % 1 > 0:
                        ws.cell(row, column).number_format = "0.00"
                    column += 1
            ws.cell(row, 72).value = f"=SUM(B{str(row)}:BS{str(row)})"
            row += 1
        # Total
        ws.cell(row, 1).value = "Итого"
        ws.cell(row, 1).style = ExcelStyle.BaseBold
        for col in range(2, 73):
            ltr = ws.cell(row, col).column_letter
            ws.cell(row, col).value = (
                f"=IF(SUM({ltr}8:{ltr}{str(row - 1)})>0,"
                f'SUM({ltr}8:{ltr}{str(row - 1)}),"")'
            )
            ws.cell(row, col).style = ExcelStyle.Number
            ws.cell(row, col).font = Font(name="Times New Roman", size=10, bold=True)
        wb.save(FlaskConfig.EXPORT_FILE_DIR + self.filename)


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
# department_id = 12
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
#     load = LoadReportProcessor(
#         year=year,
#         month_start=month_start,
#         month_end=month_end,
#         department_id=department_id,
#         departments=staff.departments,
#         department_staff=staff.department_staff(department_id),
#         schedule_lessons=await check_api_db_response(
#             await get_lessons(year, month_start, month_end)
#             ),
#         schedule_lessons_staff=await check_api_db_response(
#             await api_get_db_table(Apeks.TABLES.get("schedule_day_schedule_lessons_staff"))
#         ),
#         load_groups=await check_api_db_response(
#             await api_get_db_table(Apeks.TABLES.get("load_groups"))
#         ),
#         load_subgroups=await check_api_db_response(
#                     await api_get_db_table(Apeks.TABLES.get("load_subgroups"))
#                 ),
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
#     pprint(load.get_load(32))
#
#
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
#     loop.close()