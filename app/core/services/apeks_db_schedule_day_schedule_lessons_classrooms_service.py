import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbScheduleDayScheduleLessonsClassroomsService(ApeksApiDbService):
    """
    Класс для CRUD операций модели ScheduleDayScheduleLessonsClassrooms.

    Пример данных модели:
    {
        'lesson_id': '288026',  // id занятия (пары)
        'classroom_id': '34',  // id аудитории
    }
    """


def get_apeks_db_schedule_day_schedule_lessons_classrooms_service(
        table: str = ApeksConfig.SCHEDULE_DAY_SCHEDULE_LESSONS_CLASSROOMS,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbScheduleDayScheduleLessonsClassroomsService:
    """Возвращает CRUD сервис для таблицы schedule_day_schedule_lessons_classrooms"""

    return ApeksDbScheduleDayScheduleLessonsClassroomsService(table=table, repository=repository, token=token)
