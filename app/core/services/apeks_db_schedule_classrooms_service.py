import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbScheduleClassroomsService(ApeksApiDbService):
    """
    Класс для CRUD операций модели ScheduleClassrooms.

    Пример данных модели:
    {
        'id': '34',  // id аудитории
        'building_id': '4',  // id здания (корпуса)
        'name': '209'  // номер класса (название)
    }
    """


def get_apeks_db_schedule_classrooms_service(
        table: str = ApeksConfig.SCHEDULE_CLASSROOMS,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbScheduleClassroomsService:
    """Возвращает CRUD сервис для таблицы schedule_classrooms"""

    return ApeksDbScheduleClassroomsService(table=table, repository=repository, token=token)
