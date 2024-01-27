import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksStateStaffService(ApeksApiDbService):
    """
    Класс для CRUD операций модели StateStaff.

    Пример данных модели:
    {'id': '80',
     'family_name': 'Фамилия',
     'name': 'Имя',
     'surname': 'Отчество',
     'birthday': '1976-04-19',
     'academic_degree_level_id': '2',
     'academic_degree_type_id': '21',
     'academic_rank_id': '1',
     'special_rank_id': '14',
     'holiday_child_start': None,
     'holiday_child_end': None,
     'user_id': '34',
     'active': '1',
     'external': '0',
     'file_id': None}
    """

    pass


def process_state_staff_data(state_staff_data) -> dict:
    """
    Получение имен работников из числа постоянного состава.

    Parameters
    ----------
        state_staff_data:list
            данные из таблицы state_staff, содержащей имена работников.

    Returns
    ----------
        dict
            {id: {'full': 'полное имя',
                  'short': 'сокращенное имя',
                  'user_id': user_id}}
    """
    staff_dict = {}
    for staff in state_staff_data:
        family_name = staff.get("family_name", " ")
        first_name = staff.get("name", " ")
        second_name = staff.get("surname", " ")
        staff_dict[int(staff.get("id"))] = {
            "full": f"{family_name} {first_name} {second_name}",
            "short": f"{family_name} {first_name[0]}.{second_name[0]}.",
            "user_id": staff.get("user_id"),
        }
    logging.debug("Информация о преподавателях успешно передана")
    return staff_dict


def get_apeks_state_staff_service(
    table: str = ApeksConfig.STATE_STAFF_TABLE,
    repository: ApeksApiRepository = ApeksApiRepository(),
    token: str = ApeksConfig.TOKEN,
) -> ApeksStateStaffService:
    """Возвращает CRUD сервис для таблицы state_staff."""
    return ApeksStateStaffService(table=table, repository=repository, token=token)
