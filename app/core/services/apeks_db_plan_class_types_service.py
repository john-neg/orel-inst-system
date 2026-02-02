import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbPlanClassTypesService(ApeksApiDbService):
    """
    Класс для CRUD операций модели PlanClassTypes.

    Пример данных модели:
    {
        'id': '1',  // id типа занятия
        'name': 'Лекция',  // название типа занятия
        'name_short': 'лек'  // краткое название типа занятия
    }
    """


def get_apeks_db_plan_class_types_service(
        table: str = ApeksConfig.PLAN_CLASS_TYPES,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbPlanClassTypesService:
    """Возвращает CRUD сервис для таблицы plan_class_types"""

    return ApeksDbPlanClassTypesService(table=table, repository=repository, token=token)
