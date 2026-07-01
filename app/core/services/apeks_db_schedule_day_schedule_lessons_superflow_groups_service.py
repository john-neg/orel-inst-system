import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbScheduleDayScheduleLessonsSuperflowGroupsService(ApeksApiDbService):
    """
    Класс для CRUD операций модели ScheduleDayScheduleLessonsSuperflowGroups.

    Пример данных модели:
    {
        'lesson_id': '158837',  // id занятия (пары)
        'group_id': '506',  // id группы
    }
    """


def get_apeks_db_schedule_day_schedule_lessons_superflow_groups_service(
        table: str = ApeksConfig.SCHEDULE_DAY_SCHEDULE_LESSONS_SUPERFLOW_GROUPS,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbScheduleDayScheduleLessonsSuperflowGroupsService:
    """Возвращает CRUD сервис для таблицы schedule_day_schedule_lessons_superflow_groups"""

    return ApeksDbScheduleDayScheduleLessonsSuperflowGroupsService(table=table, repository=repository, token=token)
