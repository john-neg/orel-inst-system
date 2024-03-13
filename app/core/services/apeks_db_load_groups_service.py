from config import ApeksConfig
from ..repository.apeks_api_repository import ApeksApiRepository
from ...core.services.base_apeks_api_service import ApeksApiDbService


class ApeksLoadGroupsService(ApeksApiDbService):
    """Класс для CRUD операций модели LoadGroups."""


def get_apeks_load_groups_service(
        table: str = ApeksConfig.LOAD_GROUPS_TABLE,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN,
) -> ApeksLoadGroupsService:
    """
    Возвращает CRUD сервис для таблицы load_groups.

    Пример данных модели:
    {'id': '46',
    'name': '17з2пд',
    'department_id': '24',
    'education_plan_id': '76',
    'flow': '1',
    'people_count': '14',
    'start_date': None,
    'hide_personal': '0',
    'active': '1',
    'self_registration': '0',
    'registration_end_date': None,
    'registration_ignore_limit': '0',
    'end_date': None}
    """
    return ApeksLoadGroupsService(table=table, repository=repository, token=token)
