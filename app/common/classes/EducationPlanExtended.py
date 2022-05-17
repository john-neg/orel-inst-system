from __future__ import annotations

from dataclasses import dataclass

from app.common.classes.EducationPlan import EducationPlan


@dataclass
class EducationPlanExtended(EducationPlan):
    """
    Расширенные сведения об учебном плане и содержащихся в нем дисциплинах.

    Attributes:
    ----------
        plan_education_levels: list
            данные из таблицы 'plan_education_levels'
            (информация об уровнях образования)
        plan_education_specialties: list
            данные из таблицы 'plan_education_specialties'
            (информация о специальностях)
        plan_education_groups: list
            данные из таблицы 'plan_education_groups'
            (информация о группах специальностей)
        plan_education_specializations: list
            данные из таблицы 'plan_education_specializations'
            (информация о специализациях)
        plan_education_plans_education_forms: list
            данные из таблицы 'plan_education_plans_education_forms'
            (информация о формах обучения для планов)
        plan_education_forms: list
            данные из таблицы 'plan_education_forms'
            (информация о видах форм обучения)
        plan_qualifications: list
            данные из таблицы 'plan_qualifications'
            (информация о квалификации)
        plan_education_specializations_narrow: list
            данные из таблицы 'plan_education_specializations_narrow'
            (информация об узких специализациях)
        mm_work_programs: dict
            данные из таблицы 'mm_work_programs'
            (информация о рабочих программах плана с ключом id программы)

    Methods:
    -------
        get_field_data (plan_table_data: list, source_field_id: int | str,
            target_field_name: str, source_field_name: str = "id") -> str:
            обрабатывает данные таблиц выделяя нужные значения полей
    """

    plan_education_levels: list
    plan_education_specialties: list
    plan_education_groups: list
    plan_education_specializations: list
    plan_education_plans_education_forms: list
    plan_education_forms: list
    plan_qualifications: list
    plan_education_specializations_narrow: list
    mm_work_programs: dict

    def __post_init__(self) -> None:
        super().__post_init__()
        # self.plan_data = self.plan_education_plans[0]
        # self.name = self.plan_data.get("name")
        self.education_level_id = self.plan_data.get("education_level_id")
        self.specialty_id = self.plan_data.get("education_specialty_id")
        self.specialization_id = self.plan_data.get("education_specialization_id")
        self.qualification_id = self.plan_data.get("qualification_id")
        self.specialization_narrow_id = self.plan_data.get(
            "education_specialization_narrow_id"
        )
        self.approval_date = self.plan_data.get("approval_date")
        self.education_level_code = self.get_field_data(
            self.plan_education_levels, self.education_level_id, "code"
        )
        self.specialty_code = self.get_field_data(
            self.plan_education_specialties, self.specialty_id, "code"
        )
        self.specialty = self.get_field_data(
            self.plan_education_specialties, self.specialty_id, "name"
        )
        self.education_group_id = self.get_field_data(
            self.plan_education_specialties, self.specialty_id, "education_group_id"
        )
        self.education_group_code = self.get_field_data(
            self.plan_education_groups, self.education_group_id, "code"
        )
        self.specialization = self.get_field_data(
            self.plan_education_specializations, self.specialization_id, "name"
        )
        self.education_form_id = self.get_field_data(
            self.plan_education_plans_education_forms,
            self.education_plan_id,
            "education_form_id",
            source_field_name="education_plan_id",
        )
        self.education_form = self.get_field_data(
            self.plan_education_forms, self.education_form_id, "name"
        )
        self.qualification = self.get_field_data(
            self.plan_qualifications, self.qualification_id, "name"
        ).lower()
        self.specialization_narrow = self.get_field_data(
            self.plan_education_specializations_narrow,
            self.specialization_narrow_id,
            "name",
        )

    @staticmethod
    def get_field_data(
        plan_table_data: list,
        source_field_id: int | str,
        target_field_name: str,
        source_field_name: str = "id",
    ) -> str:
        for data in plan_table_data:
            if data.get(source_field_name) == str(source_field_id):
                return data.get(target_field_name)
