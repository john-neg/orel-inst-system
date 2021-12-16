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
        return db_filter_req("plan_education_plans", "id", self.education_plan_id)[0]["name"]

    def discipline_name(self, curriculum_discipline_id):
        """Get code and discipline name"""
        return f"{self.disciplines[str(curriculum_discipline_id)][0]} {self.disciplines[str(curriculum_discipline_id)][1]}"


class EducationStaff:
    def __init__(self, year, month, department_id):
        self.year = year
        self.month = month
        self.department_id = str(department_id)
        self.state_staff_history = db_filter_req('state_staff_history', 'department_id', self.department_id)

    def staff_list(self):
        """List of department workers which was active on selected month"""
        staff_list = []
        state_staff_positions = db_request('state_staff_positions')
        exclude_list = {'12': "инструктора произв. обучения",
                        '13': "начальник кабинета",
                        '14': "специалист по УМР",
                        '15': "зав. кабинетом", }

        for staff in self.state_staff_history:
            if staff.get('position_id') not in exclude_list:
                if staff.get('end_date') is not None:
                    if date.fromisoformat(staff.get('end_date')) > date(self.year, self.month, 1):
                        staff_list.append(staff)
                else:
                    if date.fromisoformat(staff.get('start_date')) <= date(self.year, self.month,
                                                                           monthrange(self.year, self.month)[1]):
                        staff_list.append(staff)

        def staff_sort(staff_id):
            """getting sorting code by position"""
            position_id = ""
            for sort_staff in staff_list:
                if sort_staff.get("staff_id") == str(staff_id):
                    position_id = sort_staff.get("position_id")
            for k in state_staff_positions:
                if k.get("id") == position_id:
                    return k.get("sort")

        def staff_name(staff_id):
            """getting staff name from DB"""
            resp = db_filter_req("state_staff", "id", staff_id)
            return f'{resp[0].get("family_name")} {resp[0].get("name")[0]}.{resp[0].get("surname")[0]}.'

        sort_dict = {}
        for i in staff_list:
            sort_dict[i['staff_id']] = int(staff_sort(i['staff_id']))
        a = sorted(sort_dict.items(), key=lambda x: x[1], reverse=True)
        prepod_dict = {}
        for i in range(len(a)):
            prepod_dict[a[i][0]] = staff_name(a[i][0])
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

    BaseBold = NamedStyle(name="base_bold")
    BaseBold.font = Font(name="Times New Roman", size=11, bold=True)
    BaseBold.border = AllBorder
    BaseBold.alignment = Alignment(wrap_text=True)

    GreyFill = PatternFill(
        start_color="CCCCCC", end_color="CCCCCC", fill_type="solid"
    )
