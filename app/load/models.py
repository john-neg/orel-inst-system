from copy import copy

from openpyxl import load_workbook
from openpyxl.styles import Font

from app.load.func import lessons_staff, load_subgroups, load_groups, plan_education_plans_education_forms, \
    plan_education_plans, get_lessons, get_lesson_type, get_student_type
from app.main.func import get_departments
from app.main.models import EducationStaff, ExcelStyle
from config import FlaskConfig


class LoadData:
    def __init__(self, year, month):
        self.year = year
        self.month = month
        self.departments = get_departments()
        self.prepod_dept_structure = self.prepod_dept_structure()
        self.lesson_staff = lessons_staff()
        self.load_subgroups = load_subgroups()
        self.load_groups = load_groups()
        self.plan_education_plans_education_forms = plan_education_plans_education_forms()
        self.plan_education_plans = plan_education_plans()
        self.structured_lessons = self.process_lessons()

    def prepod_dept_structure(self):
        """Department Id for prepod in current month ( {staff_id:department_id} )"""
        structure = {}
        staff = EducationStaff(self.year, self.month)
        for d in self.departments:
            staff_list = staff.staff_list(d)
            for s in staff_list:
                structure[s] = d
        return structure

    def process_lessons(self):
        """Current month lessons list with all data for load report"""
        structured_lessons = []
        for lesson in get_lessons(self.year, self.month):
            if not lesson.get('group_id'):
                if lesson.get('subgroup_id'):
                    lesson['group_id'] = self.load_subgroups.get(lesson['subgroup_id'])
            education_plan_id = self.load_groups.get(lesson.get('group_id'))['education_plan_id']
            education_form_id = self.plan_education_plans_education_forms.get(education_plan_id)
            education_level_id = self.plan_education_plans.get(education_plan_id)['education_level_id']
            lesson['education_plan_id'] = education_plan_id
            lesson['education_form_id'] = education_form_id
            lesson['education_level_id'] = education_level_id
            if lesson.get('id') in self.lesson_staff:
                for prep in self.lesson_staff[lesson['id']]:
                    less_copy = copy(lesson)
                    less_copy['staff_id'] = prep
                    less_copy['department_id'] = self.prepod_dept_structure.get(prep)
                    structured_lessons.append(less_copy)
        return structured_lessons

    def unknown_lessons(self):
        """Lessons with inactive staff (which doesn't work in department in selected time)"""
        unknown = []
        for les in self.structured_lessons:
            if not les.get('department_id'):
                unknown.append(les)
        return unknown

    def department_lessons(self, department_id):
        """Select department lessons for load report"""
        dept_lessons = []
        for les in self.structured_lessons:
            if les.get('department_id') == str(department_id):
                dept_lessons.append(les)
        return dept_lessons


class DeptPrepodLoad:
    def __init__(self, staff_list):
        self.load = {}
        self.staff_list = staff_list
        lesson_types = ['lecture', 'seminar', 'pract', 'group_cons', 'zachet', 'exams', 'final_att']
        student_types = ["och", "zo_high", "zo_mid", "adj", "prof_p", "dpo"]
        for staff_id in staff_list:
            self.load[staff_id] = {}
            for l_type in lesson_types:
                self.load[staff_id][l_type] = {}
                for s_type in student_types:
                    self.load[staff_id][l_type][s_type] = 0

    def add_load(self, staff_id, l_type, s_type, value=2):
        self.load[staff_id][l_type][s_type] += value

    def get_load(self, staff_id):
        prep_load = {self.staff_list[staff_id]: self.load[staff_id]}
        return prep_load


class LoadReport:
    def __init__(self, year, month, department_id):
        self.year = year
        self.month = month
        self.department_id = str(department_id)
        self.staff_list = EducationStaff(year, month).staff_list(department_id)
        self.load = LoadData(year, month)
        self.dept_load = DeptPrepodLoad(self.staff_list)
        self.unprocessed = []
        for lesson in self.load.structured_lessons:
            if lesson.get('department_id') == self.department_id:
                staff_id = lesson.get('staff_id')
                l_type = get_lesson_type(lesson)
                s_type = get_student_type(lesson)
                if staff_id and l_type and s_type:
                    self.dept_load.add_load(staff_id, l_type, s_type)
                else:
                    self.unprocessed.append(lesson)
        self.data = self.dept_load.load
        self.filename = f'{self.year}-{self.month} {self.load.departments.get(self.department_id)[1]}.xlsx'

    def generate_report(self):
        wb = load_workbook(FlaskConfig.TEMP_FILE_DIR + "load_report_temp.xlsx")
        ws = wb.active
        ws.title = f'{self.year}-{self.month} {self.load.departments.get(self.department_id)[1]}'
        ws.cell(1, 1).value = self.load.departments.get(self.department_id)[0]
        ws.cell(2, 1).value = f'отчет о нагрузке за {self.month} - {self.year}'
        row = 8
        for prepod in self.data:
            # Style apply
            for i in range(2, 73):
                ws.cell(row, i).style = ExcelStyle.Number
            # Prepod Name
            ws.cell(row, 1).value = self.staff_list[prepod]
            ws.cell(row, 1).style = ExcelStyle.Base
            for l_type in self.data[prepod]:
                if l_type == 'lecture':
                    column = 2
                elif l_type == 'seminar':
                    column = 8
                elif l_type == 'pract':
                    column = 14
                elif l_type == 'group_cons':
                    column = 24
                    if self.data[prepod][l_type]['dpo']:
                        del self.data[prepod][l_type]['dpo']
                elif l_type == 'zachet':
                    column = 29
                elif l_type == 'exams':
                    column = 35
                elif l_type == 'final_att':
                    column = 59
                else:
                    column = 73
                for key, val in self.data[prepod][l_type].items():
                    val = "" if val == 0 else val
                    ws.cell(row, column).value = val
                    if val and val % 1 > 0:
                        ws.cell(row, column).number_format = '0.00'
                    column += 1
            ws.cell(row, 72).value = "=SUM(B"+str(row)+":BS"+str(row)+")"
            row += 1
            # Total
            ws.cell(row, 1).value = "Итого"
            ws.cell(row, 1).style = ExcelStyle.BaseBold
            for col in range(2, 73):
                letter = ws.cell(row, col).column_letter
                ws.cell(row, col).value = "=IF(SUM("+letter+"8:"+letter+str(row-1)+")>0,SUM("+letter+"8:"+letter+str(row-1)+"),\"\")"
                ws.cell(row, col).style = ExcelStyle.Number
                ws.cell(row, col).font = Font(name="Times New Roman", size=10, bold=True)
        wb.save(FlaskConfig.EXPORT_FILE_DIR + self.filename)
