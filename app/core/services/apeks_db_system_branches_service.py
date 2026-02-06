from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository

@dataclass
class ApeksDbSystemBranchesService(ApeksApiDbService):
    '''
    Класс для CRUD операций модели SystemBranchesService.

    Пример данных модели:
    {'id': '1',
     'name': 'Бобруйский филиал',
     'active': '1'}
    '''


def get_apeks_db_system_branches_service(
        table: str = ApeksConfig.SYSTEM_BRANCHES_TABLE,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbSystemBranchesService:
    """Возвращает CRUD сервис для таблицы system_branches."""
    return ApeksDbSystemBranchesService(
        table=table, repository=repository, token=token
    )
