from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from config import ApeksConfig as Apeks


@dataclass(repr=False, eq=False)
class EducationPlan:
    """
    Сведения об учебном плане и содержащихся в нем дисциплинах.

    Attributes:
    ----------
        education_plan_id: int | str
            id учебного плана
        plan_education_plans: Iterable
            данные из таблицы 'plan_education_plans' (filter - id:plan_id)
            (информация об учебном плане)
        plan_curriculum_disciplines: dict
            данные из таблицы 'plan_curriculum_disciplines'
            (filter - id:plan_id)
            (информация о дисциплинах плана)

    Methods:
    -------
        discipline_name (cur_disc_id: int | str) -> str:
            возвращает строку "КОД Название дисциплины" по ее id
    """

    education_plan_id: int | str
    plan_education_plans: Iterable
    plan_curriculum_disciplines: dict

    def __post_init__(self) -> None:
        self.plan_data = self.plan_education_plans[0]
        self.name = self.plan_data.get("name")

    def discipline_name(self, cur_disc_id: int | str) -> str:
        """
        Возвращает код и название дисциплины по ее id.

        Parameters
        ----------
            cur_disc_id: int | str
                id дисциплины (curriculum_discipline_id).

        Returns
        -------
            str
                "КОД Название дисциплины".
        """
        return (
            f"{self.plan_curriculum_disciplines[cur_disc_id].get('code')} "
            f"{self.plan_curriculum_disciplines[cur_disc_id].get('name')}"
        )


@dataclass(repr=False, eq=False)
class EducationPlanWorkPrograms(EducationPlan):
    """
    Сведения об учебном плане и содержащихся в нем дисциплинах
    и рабочих программах.

    Attributes:
    ----------
        education_plan_id: int | str
            id учебного плана
        plan_education_plans: Iterable
            данные из таблицы 'plan_education_plans' (filter - id:plan_id)
            (информация об учебном плане)
        plan_curriculum_disciplines: dict
            данные из таблицы 'plan_curriculum_disciplines'
            (filter - id:plan_id)
            (информация о дисциплинах плана)
        work_programs_data: dict
            данные о рабочих программах
            вывод функции 'get_work_programs_data'

    Methods:
    -------
        discipline_name (cur_disc_id: int | str) -> str:
            возвращает строку "КОД Название дисциплины" по ее id
        wp_analyze

        library_content() -> dict:
            возвращает данные об обеспечении рабочих программ
    """

    work_programs_data: dict

    def __post_init__(self):
        super().__post_init__()
        self.disc_wp_match = {disc: [] for disc in self.plan_curriculum_disciplines}
        self.wrong_name, self.duplicate, self.non_exist = self.wp_analyze()

    def wp_analyze(self) -> [dict, dict, dict]:
        wrong_name, non_exist, duplicate = {}, {}, {}
        for wp in self.work_programs_data:
            disc_id = int(self.work_programs_data[wp].get("curriculum_discipline_id"))
            self.disc_wp_match.get(disc_id).append(wp)
            wp_name = self.work_programs_data[wp].get("name")
            plan_disc_name = self.plan_curriculum_disciplines[disc_id].get("name")
            if wp_name != plan_disc_name:
                wrong_name[disc_id] = [plan_disc_name, wp_name]
        for disc in self.disc_wp_match:
            code = self.plan_curriculum_disciplines[disc].get("code")
            name = self.plan_curriculum_disciplines[disc].get("name")
            if not self.disc_wp_match.get(disc):
                non_exist[disc] = f"{code} {name}"
            elif len(self.disc_wp_match.get(disc)) > 1:
                duplicate[disc] = f"{code} {name}"
        return wrong_name, duplicate, non_exist

    def library_content(self) -> dict:
        library_fields = [
            Apeks.MM_WORK_PROGRAMS_DATA.get("library_main"),
            Apeks.MM_WORK_PROGRAMS_DATA.get("library_add"),
            Apeks.MM_WORK_PROGRAMS_DATA.get("library_np"),
            Apeks.MM_WORK_PROGRAMS_DATA.get("internet"),
            Apeks.MM_WORK_PROGRAMS_DATA.get("ref_system"),
        ]
        content = {}
        for disc_id in self.disc_wp_match:
            if not self.disc_wp_match[disc_id]:
                field_dict = {}
                for field in library_fields:
                    field_dict[field] = "Нет программы"
                content[
                    self.plan_curriculum_disciplines[disc_id].get("name")
                ] = field_dict
            else:
                # если программа не одна показываем только последнюю
                wp_id = self.disc_wp_match[disc_id][-1]
                field_dict = {}
                for field in library_fields:
                    field_dict[field] = self.work_programs_data[wp_id]["fields"].get(
                        field
                    )
                content[self.work_programs_data[wp_id].get("name")] = field_dict
        return content


@dataclass(repr=False, eq=False)
class EducationPlanCompetencies(EducationPlan):
    """
    Сведения об учебном плане и содержащихся в нем дисциплинах
    и компетенциях.
    Для правильной работы отчетов сведения из таблицы "plan_curriculum_disciplines"
    необходимо передавать с помощью функции "get_plan_curriculum_disciplines"
    с параметром disc_filter=False.

    Attributes:
    ----------
        plan_competencies: dict
            данные из таблицы 'plan_competencies'
            (информация о компетенциях плана)
        discipline_competencies: dict
            данные из таблицы 'plan_curriculum_discipline_competencies'
            (информация о связях дисциплин и компетенций)

    Methods:
    -------
        named_disc_comp_relations()  -> dict:
            возвращает данные о связях дисциплин и компетенций с названиями.

    """

    plan_competencies: dict
    discipline_competencies: dict

    def named_disc_comp_relations(self) -> dict:
        """
        Возвращает данные о связях дисциплин и компетенций с названиями.

        Returns
        -------
            dict
                {discipline_name: [comp_name]}
        """
        relations = {}
        for disc in self.discipline_competencies:
            relations[self.discipline_name(disc)] = [
                (f"{self.plan_competencies[comp].get('code')} - "
                 f"{self.plan_competencies[comp].get('description')}")
                for comp in self.discipline_competencies[disc]
            ]
        return relations


@dataclass(repr=False, eq=False)
class EducationPlanIndicators(EducationPlanCompetencies, EducationPlanWorkPrograms):
    """
    Сведения об учебном плане, содержащихся в нем дисциплинах, компетенциях
    рабочих программах.

    Attributes:
    ----------
        'work_programs_data': dict
            вывод функции 'get_work_programs_data' c параметром 'competencies = True'
    """

    def __post_init__(self):
        super().__post_init__()
        self.plan_no_control_data = []
        self.program_control_extra_levels = []
        self.program_comp_level_delete = []
        self.analyze_control_data()

    def analyze_control_data(self) -> None:
        for wp_val in self.work_programs_data.values():
            if not wp_val.get("control_works"):
                self.plan_no_control_data.append(wp_val.get("name"))
            if len(wp_val.get("competency_levels")) > 1:
                self.program_control_extra_levels.append(wp_val.get("name"))
                for level, value in wp_val.get("competency_levels").items():
                    if level != 1:
                        self.program_comp_level_delete.append(value.get('id'))


@dataclass(repr=False, eq=False)
class EducationPlanExtended(EducationPlanWorkPrograms):
    """
    Расширенные сведения об учебном плане и содержащихся в нем дисциплинах.

    Attributes:
    ----------
        plan_education_levels: Iterable
            данные из таблицы 'plan_education_levels'
            (информация об уровнях образования)
        plan_education_specialties: Iterable
            данные из таблицы 'plan_education_specialties'
            (информация о специальностях)
        plan_education_groups: Iterable
            данные из таблицы 'plan_education_groups'
            (информация о группах специальностей)
        plan_education_specializations: Iterable
            данные из таблицы 'plan_education_specializations'
            (информация о специализациях)
        plan_education_plans_education_forms: Iterable
            данные из таблицы 'plan_education_plans_education_forms'
            (информация о формах обучения для планов)
        plan_education_forms: Iterable
            данные из таблицы 'plan_education_forms'
            (информация о видах форм обучения)
        plan_qualifications: Iterable
            данные из таблицы 'plan_qualifications'
            (информация о квалификации)
        plan_education_specializations_narrow: Iterable
            данные из таблицы 'plan_education_specializations_narrow'
            (информация об узких специализациях)

    Methods:
    -------
        get_field_data (plan_table_data: list, source_field_id: int | str,
            target_field_name: str, source_field_name: str = "id") -> str:
            обрабатывает данные таблиц выделяя нужные значения полей
    """

    plan_education_levels: Iterable
    plan_education_specialties: Iterable
    plan_education_groups: Iterable
    plan_education_specializations: Iterable
    plan_education_plans_education_forms: Iterable
    plan_education_forms: Iterable
    plan_qualifications: Iterable
    plan_education_specializations_narrow: Iterable

    def __post_init__(self) -> None:
        super().__post_init__()
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
        plan_table_data: Iterable,
        source_field_id: int | str,
        target_field_name: str,
        source_field_name: str = "id",
    ) -> str:
        for data in plan_table_data:
            if data.get(source_field_name) == str(source_field_id):
                return data.get(target_field_name)
