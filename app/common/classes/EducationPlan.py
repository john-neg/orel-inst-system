from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EducationPlan:
    """
    Сведения об учебном плане и содержащихся в нем дисциплинах.

    Attributes:
    ----------
        education_plan_id: int | str
            id учебного плана
        plan_education_plans: list
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
    plan_education_plans: list
    plan_curriculum_disciplines: dict

    def __post_init__(self) -> None:
        self.plan_data = self.plan_education_plans[0]
        self.name = self.plan_data.get('name')

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
            f"{self.plan_curriculum_disciplines[int(cur_disc_id)][0]} "
            f"{self.plan_curriculum_disciplines[int(cur_disc_id)][1]}"
        )
