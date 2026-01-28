import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbPlanCurriculumDisciplinesService(ApeksApiDbService):
    """
    Класс для CRUD операций модели PlanCurriculumDisciplines.

    Пример данных модели:
    {
        'id': '18086',
        'education_plan': '345', // id учебного плана
        'code': 'Б.1.0.7',
        'discipline_id': '504',
        'department_id': '12'
    }
    """

    async def get_education_plan_ids_for_discipline(self, discipline_id: int) -> list:
        """
        Возвращает id учебных планов в которые входит дисциплина.
        
        :param discipline_id: id дисциплины для которой необходимо получить id учебных планов
        :type discipline_id: int
        :return: список id учебных планов
        :rtype: list
        """

        state_curriculum_disciplines = await self.get(discipline_id=discipline_id)
        enucation_plan_ids = [item['education_plan_id'] for item in state_curriculum_disciplines]
        return enucation_plan_ids


def get_apeks_db_plan_curriculum_disciplines_service(
        table: str = ApeksConfig.PLAN_CURRICULUM_DISCIPLINES,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbPlanCurriculumDisciplinesService:
    """Возвращает CRUD сервис для таблицы plan_curriculum_disciplines"""

    return ApeksDbPlanCurriculumDisciplinesService(table=table, repository=repository, token=token)
