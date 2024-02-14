from ...core.repository.apeks_api_repository import ApeksApiRepository
from ...core.services.base_apeks_api_service import ApeksApiDbService
from config import ApeksConfig


class ApeksStudentStudentHistoryService(ApeksApiDbService):
    """
    Класс для CRUD операций модели StudentStudentHistory.

    Пример данных модели:
    {'id': '4602',
    'student_id': '1687',
    'type': '6',
    'comments': '',
    'data': None,
    'start_date': '2023-09-11',
    'document_number': '№701 л/с',
    'group_id': '310'}
    """

    pass


def get_apeks_student_student_history_service(
    table: str = ApeksConfig.STUDENT_STUDENT_HISTORY_TABLE,
    repository: ApeksApiRepository = ApeksApiRepository(),
    token: str = ApeksConfig.TOKEN,
) -> ApeksStudentStudentHistoryService:
    """Возвращает CRUD сервис для таблицы student_student_history."""
    return ApeksStudentStudentHistoryService(
        table=table, repository=repository, token=token
    )
