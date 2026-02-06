import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbScheduleLessonTimesService(ApeksApiDbService):
    """
    Класс для CRUD операций модели ScheduleLessonTimes.

    Пример данных модели:
    {
        'id': '1',  // id пары
        'hour_from': '8'  // начало пары
        'minute_from': '40'
        'hour_to': '10'  // конец пары
        'minute_to': '10'
    }
    """


def get_apeks_db_schedule_lesson_times_service(
        table: str = ApeksConfig.SCHEDULE_LESSON_TIMES,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbScheduleLessonTimesService:
    """Возвращает CRUD сервис для таблицы schedule_lesson_times"""

    return ApeksDbScheduleLessonTimesService(table=table, repository=repository, token=token)
