import logging
from dataclasses import dataclass

from config import ApeksConfig
from .base_apeks_api_service import ApeksApiDbService
from ..repository.apeks_api_repository import ApeksApiRepository


@dataclass
class ApeksDbStateDepartmentsService(ApeksApiDbService):
    """
    Класс для CRUD операций модели StateDepartments.

    Пример данных модели:
    {'id': '2',
     'name': 'Правовая группа',
     'name_short': 'Правовая группа',
     'parent_id': '28',
     'contains_staff': '1',
     'type': None,
     'active': '1',
     'branch_id': None},
    """

    async def get_departments(self, department_filter=None) -> dict:
        """
        Получение информации о подразделениях.

        :param department_filter: Фильтр по типу подразделения
                                  (department, kafedra, faculty, other).
        :return: dict {id: {'full': 'полное название',
                            'short': 'сокращенное название',
                            'type': 'тип подразделения'}}}
        """
        state_departments = await self.list()

        filters = {
            "department": ApeksConfig.DEPT_TYPES[ApeksConfig.TYPE_DEPARTM],
            "kafedra": ApeksConfig.DEPT_TYPES[ApeksConfig.TYPE_KAFEDRA],
            "faculty": ApeksConfig.DEPT_TYPES[ApeksConfig.TYPE_FACULTY],
            "other": "Иные",
        }

        # Получаем id групп подразделений по типам, и группы подразделений
        groups_by_type = {}
        departments_groups = {}
        for dept in state_departments:
            if dept.get("type"):
                if dept.get("contains_staff") == "0":
                    dept_type = ApeksConfig.DEPT_TYPES[dept.get("type")]
                else:
                    dept_type = "Иные"
                group_type = groups_by_type.setdefault(dept_type, [])
                group_type.append(dept.get("id"))
            else:
                parent_id = dept.get("parent_id") or "Other"
                group = departments_groups.setdefault(parent_id, [])
                group.append(dept)

        if departments_groups.get("Other"):
            groups_by_type["Иные"] = ["Other"]

        dept_dict = {}
        for group_type in groups_by_type:
            for group_id in groups_by_type[group_type]:
                dept_group = departments_groups.get(group_id)
                if dept_group:
                    for dept in dept_group:
                        dept_dict[dept["id"]] = {
                            "full": dept.get("name"),
                            "short": dept.get("name_short"),
                            "type": group_type,
                        }

        logging.debug("Информация о подразделениях успешно передана")

        if filters.get(department_filter):
            return dict(
                filter(
                    lambda x: x[1]["type"] == filters.get(department_filter),
                    dept_dict.items(),
                )
            )
        else:
            return dept_dict


def get_db_apeks_state_departments_service(
    table: str = ApeksConfig.STATE_DEPARTMENTS_TABLE,
    repository: ApeksApiRepository = ApeksApiRepository(),
    token: str = ApeksConfig.TOKEN,
) -> ApeksDbStateDepartmentsService:
    """Возвращает CRUD сервис для таблицы state_departments."""
    return ApeksDbStateDepartmentsService(table=table, repository=repository, token=token)
