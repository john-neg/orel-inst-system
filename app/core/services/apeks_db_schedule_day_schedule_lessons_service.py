import logging
from dataclasses import dataclass
from datetime import date

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository, ApeksApiEndpoints


@dataclass
class ApeksDbScheduleDayScheduleLessonsService(ApeksApiDbService):
    """
    Класс для CRUD операций модели ScheduleDayScheduleLessons.

    Пример данных модели:
    {
        'id': '288026',
        'discipline_id': '504',
        'class_type_id': '1',  // вид занятия Л/С/ПЗ
        'control_type_id': 'NULL',  // вид контроля зачет/экзамен...
        'date': '2025-09-02',  // дата занятия
        'lesson_time_id': '3',  // номер пары
        'topic_code': '1',  // номер темы
        'topic_name': '...',  // название темы
        'group_id': '506', // id группы, у которой проходит пара
        'join_with_next': 'NULL'  // сдвоена ли пара со следующей
    }
    """

    async def get_groups_studyng_discipline_for_period(
        self,
        discipline_id: int | str,
        start_date: date,
        end_date: date,
    ) -> list:
        """
        Возвращает id групп изучающих заданную дисциплину за указанный период.

        Parameters
        ----------
            discipline_id: int
                id дисциплины для которой необходимо получить id групп
            start_date: date
                начало периода
            end_date: date
                конец периода

        Returns
        -------
            list
                список id учебных групп
        """

        endpoint = ApeksApiEndpoints.DB_GET_ENDPOINT
        lessons_filter = f'discipline_id={discipline_id} AND date>=\'{start_date}\' AND date<=\'{end_date}\''
        params = {
            'token': self.token,
            'table': self.table,
            'filter': lessons_filter,
        }

        logging.debug(
            'Переданы параметры для запроса \'get_schedule_day_schedule_lessons\': '
            f'{params['filter']}'
        )


        return await self.repository.get(endpoint, params)





def get_apeks_db_schedule_day_schedule_lessons_service(
        table: str = ApeksConfig.SCHEDULE_DAY_SCHEDULE_LESSONS,
        repository: ApeksApiRepository = ApeksApiRepository(),
        token: str = ApeksConfig.TOKEN
) -> ApeksDbScheduleDayScheduleLessonsService:
    """Возвращает CRUD сервис для таблицы schedule_day_schedule_lessons"""

    return ApeksDbScheduleDayScheduleLessonsService(table=table, repository=repository, token=token)
