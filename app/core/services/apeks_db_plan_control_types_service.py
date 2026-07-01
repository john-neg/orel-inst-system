import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbPlanControlTypesService(ApeksApiDbService):
    """
    Класс для CRUD операций модели PlanControlTypes.

    Пример данных модели:
    {
        'id': '1',  // id вида контрольного занятия
        'name': 'Лекция',  // название вида контрольного занятия
        'name_short': 'лек'  // краткое название вида контрольного занятия
    }
    """


def get_apeks_db_plan_control_types_service(
        table: str = ApeksConfig.PLAN_CONTROL_TYPES,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbPlanControlTypesService:
    """Возвращает CRUD сервис для таблицы plan_control_types"""

    return ApeksDbPlanControlTypesService(table=table, repository=repository, token=token)
