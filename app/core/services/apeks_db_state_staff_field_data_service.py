from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbStateStaffFieldDataService(ApeksApiDbService):
    """
    Класс для CRUID операций модели StateStaffFieldData

    Пример данных модели:
    {'id': '43',
     'staff_id': '6',
     'field_id': '1',
     'data': '518, 41 45 47'}
    """

    pass


def get_apeks_db_state_staff_field_data_service(
        table: str = ApeksConfig.TABLES.get('state_staff_field_data'),
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbStateStaffFieldDataService:
    """ Возвращает CRUID сервис для таблицы state_staff_field_data"""
    return ApeksDbStateStaffFieldDataService(
        table=table, repository=repository, token=token
    )
