from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbStateSpecialRanksService(ApeksApiDbService):
    """
    Класс для CRUID операций модели StateSpecialRanks

    Пример модели:
    {'id': '1',
     'name': 'some rank',
     'name_short': 'sm. rnk.'}
    """

    pass


def get_apeks_db_state_special_ranks_service(
        table: str = ApeksConfig.TABLES.get('state_special_ranks'),
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbStateSpecialRanksService:
    """ Возвращает CRUID сервис для таблицы state_special_ranks"""
    return ApeksDbStateSpecialRanksService(
        table=table, repository=repository, token=token
    )
