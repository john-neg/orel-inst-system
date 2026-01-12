from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbStateDepartmentsTypesService(ApeksApiDbService):
    '''
    Класс для CRUD операций модели StateDepartmentsTypesService.

    Пример данных модели:
    {'id': '1',
     'department_id': 4,  # id подразделения
     'type': '1'}  # тип подразделения 1 - кафедра 2 - факультет
    '''

def get_apeks_db_state_departments_types_service(
    table: str = ApeksConfig.STATE_DEPARTMENTS_TYPES_TABLE,
    repository: ApeksApiRepository = ApeksApiRepository(),
    token: str = ApeksConfig.TOKEN
) -> ApeksDbStateDepartmentsTypesService:
    """Возвращает CRUD сервис для таблицы state_departments_types."""
    return ApeksDbStateDepartmentsTypesService(
        table=table, repository=repository, token=token
    )
