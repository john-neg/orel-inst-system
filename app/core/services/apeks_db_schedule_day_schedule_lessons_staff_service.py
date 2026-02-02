import logging
from dataclasses import dataclass
from datetime import date

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository, ApeksApiEndpoints
from ..services.apeks_db_state_staff_service import get_apeks_db_state_staff_service


@dataclass
class ApeksDbScheduleDayScheduleLessonsStaffService(ApeksApiDbService):
    '''
    Класс для CRUD операций модели ScheduleDayScheduleLessonsStaff.

    Пример данных модели:
    {
        'lesson_id': '288026',  // id занятия (пары)
        'staff_id': '33'  // id преподавателя, ведущего занятие
    }
    '''


def get_apeks_db_schedule_day_schedule_lessons_staff_service(
        table: str = ApeksConfig.SCHEDULE_DAY_SCHEDULE_LESSONS_STAFF,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbScheduleDayScheduleLessonsStaffService:
    '''Возвращает CRUD сервис для таблицы schedule_day_schedule_lessons_staff'''

    return ApeksDbScheduleDayScheduleLessonsStaffService(table=table, repository=repository, token=token)
