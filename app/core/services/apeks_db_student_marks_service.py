from ...core.repository.apeks_api_repository import ApeksApiRepository
from ...core.services.base_apeks_api_service import ApeksApiDbService
from config import ApeksConfig


class ApeksDbStudentMarksService(ApeksApiDbService):
    """
    Класс для CRUD операций модели StudentMarks.

    Пример данных модели:
    {'id': '799817',
    'journal_lesson_id': '101744',
    'student_id': '1678',
    'mark_type_id': '1',
    'mark_value_id': None,
    'skip_reason_id': '9',
    'is_debt': '0',
    'document_type_id': None,
    'parent_id': None,
    'datetime': '2024-04-04 07:47:20',
    'date_retake': None,
    'points': None,
    'comments': '',
    'document_can_correct': None,
    'user_id': '1'}
    """


def get_apeks_db_student_marks_service(
        table: str = ApeksConfig.STUDENT_MARKS_TABLE,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN,
) -> ApeksDbStudentMarksService:
    """Возвращает CRUD сервис для таблицы student_marks."""
    return ApeksDbStudentMarksService(table=table, repository=repository, token=token)
