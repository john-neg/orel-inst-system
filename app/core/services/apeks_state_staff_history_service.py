import logging
from dataclasses import dataclass
from datetime import date
from typing import Optional

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiEndpoints, ApeksApiRepository


@dataclass
class ApeksStateStaffHistoryService(ApeksApiDbService):
    """
    Класс для CRUD операций модели StateStaffHistory.

    Пример данных модели:
    {'id': '673',
     'staff_id': '566',
     'department_id': '31',
     'position_id': '65',
     'vacancy_id': '155',
     'value': '1',
     'start_date': '2004-03-22',
     'end_date': None,
     'verified': '1',
     'timestamp': '2024-01-16 17:36:35'}
    """

    async def get_staff_for_date(
        self,
        req_date: date,
        department_id: Optional[int | str] = None,
    ):
        """
        Получение списка сотрудников на указанную дату.

        Parameters
        ----------
            req_date: date
                дата
            department_id: int|str|
                id подразделения
        """
        endpoint = ApeksApiEndpoints.DB_GET_ENDPOINT
        dept_filter = f" and department_id={department_id}" if department_id else ""
        params = {
            "token": self.token,
            "table": self.table,
            "filter": (
                f"start_date <= '{req_date}' and (end_date >= '{req_date}' "
                f"or end_date IS NULL){dept_filter}"
            ),
        }
        logging.debug(
            "Переданы параметры для запроса 'get_state_staff_history': "
            f"{params['filter']}"
        )
        return await self.repository.get(endpoint, params)


def get_apeks_state_staff_history_service(
    table: str = ApeksConfig.STATE_STAFF_HISTORY_TABLE,
    repository: ApeksApiRepository = ApeksApiRepository(),
    token: str = ApeksConfig.TOKEN,
) -> ApeksStateStaffHistoryService:
    """Возвращает CRUD сервис для таблицы state_staff_history."""
    return ApeksStateStaffHistoryService(
        table=table, repository=repository, token=token
    )
