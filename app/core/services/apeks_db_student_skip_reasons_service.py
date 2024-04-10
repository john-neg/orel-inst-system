from ...core.repository.apeks_api_repository import ApeksApiRepository
from ...core.services.base_apeks_api_service import ApeksApiDbService
from config import ApeksConfig


class ApeksDbStudentSkipReasonsService(ApeksApiDbService):
    """
    Класс для CRUD операций модели StudentSkipReasons.

    Пример данных модели:
    {'id': '1', 'name': 'Наряд', 'name_short': 'н', 'weight': '10'}
    """


def get_apeks_db_student_skip_reasons_service(
        table: str = ApeksConfig.STUDENT_SKIP_REASONS,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN,
) -> ApeksDbStudentSkipReasonsService:
    """Возвращает CRUD сервис для таблицы student_skip_reasons."""
    return ApeksDbStudentSkipReasonsService(table=table, repository=repository, token=token)
