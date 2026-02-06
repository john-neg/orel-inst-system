import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbStudentJournalLessonsSuperflowGroupsService(ApeksApiDbService):
    """
    Класс для CRUD операций модели StudentJournalLessonsSuperflowGroups.

    Пример данных модели:
    {
        'journal_lessons_id': '158837',  // id занятия (пары)
        'group_id': '506',  // id группы
    }
    """


def get_apeks_db_student_journal_lessons_superflow_groups_service(
        table: str = ApeksConfig.STUDENT_JOURNAL_LESSONS_SUPERFLOW_GROUPS,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbStudentJournalLessonsSuperflowGroupsService:
    """Возвращает CRUD сервис для таблицы student_journal_lessons_superflow_groups"""

    return ApeksDbStudentJournalLessonsSuperflowGroupsService(table=table, repository=repository, token=token)
