import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbScheduleBuildingsService(ApeksApiDbService):
    """
    Класс для CRUD операций модели ScheduleBuildings.

    Пример данных модели:
    {
        'id': '4',  // id здания (корпуса)
        'name_short': 'Г'  // название корпуса
    }
    """


def get_apeks_db_schedule_buildings_service(
        table: str = ApeksConfig.SCHEDULE_BUILDINGS,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbScheduleBuildingsService:
    """Возвращает CRUD сервис для таблицы schedule_buildings"""

    return ApeksDbScheduleBuildingsService(table=table, repository=repository, token=token)
