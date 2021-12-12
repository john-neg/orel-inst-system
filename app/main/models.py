from app.main.func import plan_curriculum_disciplines


class EducationPlan:
    def __init__(self, education_plan_id):
        self.education_plan_id = education_plan_id
        self.disciplines = plan_curriculum_disciplines(education_plan_id)

    def discipline_name(self, curriculum_discipline_id):
        """Получение кода и названия дисциплины"""
        return f"{self.disciplines[str(curriculum_discipline_id)][0]} {self.disciplines[str(curriculum_discipline_id)][1]}"
