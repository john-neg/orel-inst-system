from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbStateVacanciesService(ApeksApiDbService):
    """
    Класс для CRUD операций модели StateVacancies.

    Пример данных модели:
    {'id': '256',
     'department_id': '27',
     'position_id': '86',
     'has_rank': '1',
     'value': '1'}
    """

    pass


def get_apeks_db_state_vacancies_service(
    table: str = ApeksConfig.STATE_VACANCIES_TABLE,
    repository: ApeksApiRepository = ApeksApiRepository(),
    token: str = ApeksConfig.TOKEN,
) -> ApeksDbStateVacanciesService:
    """Возвращает CRUD сервис для таблицы state_vacancies."""
    return ApeksDbStateVacanciesService(
        table=table, repository=repository, token=token
    )
