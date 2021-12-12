from openpyxl.styles import Side, NamedStyle, Font, Border, Alignment, PatternFill
from app.main.func import plan_curriculum_disciplines, db_filter_req


class EducationPlan:
    def __init__(self, education_plan_id):
        self.education_plan_id = education_plan_id
        self.disciplines = plan_curriculum_disciplines(education_plan_id)
        self.name = self.get_name()

    def get_name(self):
        return db_filter_req("plan_education_plans", "id", self.education_plan_id)[0]["name"]

    def discipline_name(self, curriculum_discipline_id):
        """Получение кода и названия дисциплины"""
        return f"{self.disciplines[str(curriculum_discipline_id)][0]} {self.disciplines[str(curriculum_discipline_id)][1]}"


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
