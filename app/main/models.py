from calendar import monthrange
from datetime import date

from openpyxl.styles import Side, NamedStyle, Font, Border, Alignment, PatternFill
from app.main.func import plan_curriculum_disciplines, db_filter_req, db_request


class EducationPlan:
    def __init__(self, education_plan_id):
        self.education_plan_id = education_plan_id
        self.disciplines = plan_curriculum_disciplines(education_plan_id)
        self.name = self.get_name()

    def get_name(self):
        """Get education plan name"""
        return db_filter_req("plan_education_plans", "id", self.education_plan_id)[0]["name"]

    def discipline_name(self, curriculum_discipline_id):
        """Get code and discipline name"""
        return f"{self.disciplines[str(curriculum_discipline_id)][0]} {self.disciplines[str(curriculum_discipline_id)][1]}"


class EducationStaff:
    def __init__(self, year, month):
        self.year = year
        if month == 'январь-август':
            self.start_month = 1
            self.end_month = 8
        elif month == 'сентябрь-декабрь':
            self.start_month = 9
            self.end_month = 12
        else:
            self.start_month = int(month)
            self.end_month = int(month)
        self.state_staff_history = db_request('state_staff_history')
        self.state_staff = self.get_state_staff()
        self.state_staff_positions = db_request('state_staff_positions')

    def get_state_staff(self):
        staff_list = {}
        resp = db_request('state_staff')
        for staff in resp:
            family_name = staff.get("family_name")
            family_name = family_name if family_name else 'X'
            first_name = staff.get("name")
            first_name = first_name[0] if first_name else 'X'
            second_name = staff.get("surname")
            second_name = second_name[0] if second_name else 'X'
            staff_list[staff.get('id')] = f'{family_name} {first_name}.{second_name}.'
        return staff_list

    def staff_list(self, department_id):
        """List of department workers which was active on selected month"""
        staff_list = []
        exclude_list = {'12': "инструктора произв. обучения",
                        '13': "начальник кабинета",
                        '14': "специалист по УМР",
                        '15': "зав. кабинетом", }

        dept_history = []
        for record in self.state_staff_history:
            if record.get('department_id') == str(department_id):
                dept_history.append(record)

        for staff in dept_history:
            if staff.get('position_id') not in exclude_list:
                if staff.get('end_date') is not None:
                    if date.fromisoformat(staff.get('end_date')) > date(self.year, self.start_month, 1):
                        staff_list.append(staff)
                else:
                    if date.fromisoformat(staff.get('start_date')) <= date(self.year, self.end_month,
                                                                           monthrange(self.year, self.end_month)[1]):
                        staff_list.append(staff)

        def staff_sort(staff_id):
            """getting sorting code by position"""
            position_id = ""
            for sort_staff in staff_list:
                if sort_staff.get("staff_id") == str(staff_id):
                    position_id = sort_staff.get("position_id")
            for k in self.state_staff_positions:
                if k.get("id") == position_id:
                    return k.get("sort")

        sort_dict = {}
        for i in staff_list:
            sort_dict[i['staff_id']] = int(staff_sort(i['staff_id']))
        a = sorted(sort_dict.items(), key=lambda x: x[1], reverse=True)
        prepod_dict = {}
        for i in range(len(a)):
            prepod_dict[a[i][0]] = self.state_staff.get(a[i][0])
        return prepod_dict


class ExcelStyle(object):
    """Styles for Excel export"""
    ThinBorder = Side(style="thin", color="000000")
    ThickBorder = Side(style="thick", color="000000")
    AllBorder = Border(
        left=ThinBorder, right=ThinBorder, top=ThinBorder, bottom=ThinBorder
    )

    Header = NamedStyle(name="header")
    Header.font = Font(name="Times New Roman", size=12, bold=True)
    Header.border = AllBorder
    Header.alignment = Alignment(wrap_text=True)

    Base = NamedStyle(name="base")
    Base.font = Font(name="Times New Roman", size=11)
    Base.border = AllBorder
    Base.alignment = Alignment(wrap_text=True)

    Number = NamedStyle(name="number")
    Number.font = Font(name="Times New Roman", size=9)
    Number.border = AllBorder
    Number.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True, shrink_to_fit=True)

    BaseBold = NamedStyle(name="base_bold")
    BaseBold.font = Font(name="Times New Roman", size=11, bold=True)
    BaseBold.border = AllBorder
    BaseBold.alignment = Alignment(wrap_text=True)

    GreyFill = PatternFill(
        start_color="CCCCCC", end_color="CCCCCC", fill_type="solid"
    )
