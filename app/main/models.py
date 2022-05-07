from app.main.func import plan_curriculum_disciplines, db_filter_req


class EducationPlan:
    def __init__(self, education_plan_id):
        self.education_plan_id = education_plan_id
        self.disciplines = plan_curriculum_disciplines(education_plan_id)
        self.name = self.get_name()

    def get_name(self):
        """Get education plan name."""
        return db_filter_req("plan_education_plans", "id", self.education_plan_id)[0][
            "name"
        ]

    def discipline_name(self, curriculum_discipline_id):
        """Get code and discipline name."""
        return (
            f"{self.disciplines[str(curriculum_discipline_id)][0]} "
            f"{self.disciplines[str(curriculum_discipline_id)][1]}"
        )
