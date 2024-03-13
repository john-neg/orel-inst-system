from ...core.repository.apeks_api_repository import ApeksApiRepository
from ...core.services.base_apeks_api_service import ApeksApiDbService
from config import ApeksConfig


class ApeksStudentStudentsService(ApeksApiDbService):
    """
    Класс для CRUD операций модели StudentStudents.

    Пример данных модели:
    {'id': '1199',
    'family_name': 'Иванов',
    'name': 'Иван',
    'surname': 'Иванович',
    'sex': 'F',
    'birthday': '2001-08-24',
    'user_id': '1100',
    'special_rank_id': None,
    'file_id': None,
    'employer_id': None,
    'job_position_id': None,
    'external_id': '4703'}
    """


def get_apeks_student_students_service(
        table: str = ApeksConfig.STUDENT_STUDENTS_TABLE,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN,
) -> ApeksStudentStudentsService:
    """Возвращает CRUD сервис для таблицы student_students."""
    return ApeksStudentStudentsService(table=table, repository=repository, token=token)
