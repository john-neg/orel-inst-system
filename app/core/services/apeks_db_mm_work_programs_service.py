import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbMMWorkProgramsService(ApeksApiDbService):
    """
    Класс для CRUD операций модели MMWorkPrograms.

    Пример данных модели:
    {
        'id': '7575',  // id рабочей программы дисциплины
        'curriculum_discipline_id': '18086',  // id дисциплины входящей в учебный план
        'name': 'ИКТвПСД'  // название дисциплины
    }
    """


def get_apeks_db_mm_work_programs_service(
        table: str = ApeksConfig.MM_WORK_PROGRAMS_TABLE,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbMMWorkProgramsService:
    """Возвращает CRUD сервис для таблицы mm_work_programs"""

    return ApeksDbMMWorkProgramsService(table=table, repository=repository, token=token)
