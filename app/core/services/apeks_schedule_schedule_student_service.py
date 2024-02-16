import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiBaseService
from ..repository.apeks_api_repository import ApeksApiEndpoints, ApeksApiRepository


@dataclass
class ApeksScheduleScheduleStudentService(ApeksApiBaseService):
    """
    Сервис для точки доступа /api/call/schedule-schedule/student.

    Attributes:
    ----------
    endpoint: ApeksApiEndpoints
        название точки доступа к API АпексВУЗ
    repository: ApeksApiRepository
        репозиторий для запросов к API АпексВУЗ
    token: str
        токен доступа к API АпексВУЗ

    Methods:
    -------
    get(group_id, month, year):
        выполняет GET-запрос к точке доступа.
    """

    async def get(
        self,
        group_id: str | int | None = None,
        month: str | int | None = None,
        year: str | int | None = None,
    ):
        params = {"token": self.token}
        if group_id is not None:
            params["group_id"] = str(group_id)
        if month is not None:
            params["month"] = str(month)
        if year is not None:
            params["year"] = str(year)
        response_data = await self.repository.get(self.endpoint, params=params)
        logging.debug(
            f"Выполнен запрос к API АпексВУЗ {self.endpoint}. Параметры - "
            f"staff_id: {str(group_id)}, month: {str(month)}, year: {str(year)}"
        )
        return response_data


def get_apeks_schedule_schedule_student_service(
    endpoint: ApeksApiEndpoints = ApeksApiEndpoints.STUDENT_SCHEDULE_ENDPOINT.value,
    repository: ApeksApiRepository = ApeksApiRepository(),
    token: str = ApeksConfig.TOKEN,
) -> ApeksScheduleScheduleStudentService:
    """Возвращает сервис для точки доступа /api/call/schedule-schedule/student."""
    return ApeksScheduleScheduleStudentService(
        endpoint=endpoint, repository=repository, token=token
    )
