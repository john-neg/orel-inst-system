from config import ApeksConfig
from ..repository.apeks_api_repository import ApeksApiRepository
from ...core.services.base_apeks_api_service import ApeksApiDbService


class ApeksStudentStudentsGroupsService(ApeksApiDbService):
    """
    Класс для CRUD операций модели StudentStudentsGroups.

    Пример данных модели:
    {'student_id': '1176',
    'group_id': '183',
    'subgroup_id': None,
    'financing': None,
    'start_date': None,
    'end_date': None,
    'prev_group_id': None,
    'status': '1'}
    """

    pass


def get_apeks_student_students_groups_service(
    table: str = ApeksConfig.STUDENT_STUDENTS_GROUPS_TABLE,
    repository: ApeksApiRepository = ApeksApiRepository(),
    token: str = ApeksConfig.TOKEN,
) -> ApeksStudentStudentsGroupsService:
    """Возвращает CRUD сервис для таблицы student_students_groups."""
    return ApeksStudentStudentsGroupsService(
        table=table, repository=repository, token=token
    )
