from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository

@dataclass
class ApeksDbSystemSettingsService(ApeksApiDbService):
    '''
    Класс для CRUD операций модели SystemSettings.

    Пример данных модели:
    {'id': '1',
     'user_id': 'NULL',
     'setting': 'system.ou.short_name',
     'value': 'ОрЮИ МВД России имени В.В. Лукьянова'}
    '''


def get_apeks_db_system_settings_service(
        table: str = ApeksConfig.SYSTEM_SETTINGS_TABLE,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbSystemSettingsService:
    """Возвращает CRUD сервис для таблицы system_settings."""
    return ApeksDbSystemSettingsService(
        table=table, repository=repository, token=token
    )
