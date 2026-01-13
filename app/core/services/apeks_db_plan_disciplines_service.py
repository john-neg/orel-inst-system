import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbPlanDisciplinesService(ApeksApiDbService):
    """
    Класс для CRUD операций модели PlanDisciplines.

    Пример данных модели:
    {
        'id': '15',
        'name': '',
        'name_short': '',
        'level': '',
        'auto_create': '',
        'department_id': ''
    }
    """

    async def get_disciplines(self, department_id: int) -> dict:
        """
        Возвращает список дисциплин, преподаваемых на кафедре.
        
        :param department_id: id кафедры, для которой необходимо получить список дисциплин
        :type department_id: int
        :return: список дисциплин
        :rtype: dict
        """
        state_disciplines = await self.get(department_id=department_id)
        return state_disciplines


def get_apeks_db_plan_disciplines_service(
        table: str = ApeksConfig.PLAN_DISCIPLINES,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbPlanDisciplinesService:
    """Возвращает CRUD сервис для таблицы plan_disciplines"""
    return ApeksDbPlanDisciplinesService(table=table, repository=repository, token=token)
