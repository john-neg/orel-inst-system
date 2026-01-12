import datetime as dt
from dataclasses import dataclass, field

from ..core.services.apeks_db_state_departments_service import (
    get_db_apeks_state_departments_service,
)
from ..core.services.apeks_db_state_special_ranks_service import (
    get_apeks_db_state_special_ranks_service,
)
from ..core.services.apeks_db_state_staff_field_data_service import (
    get_apeks_db_state_staff_field_data_service,
)
from ..core.services.apeks_db_state_staff_history_service import (
    get_db_apeks_state_staff_history_service,
)
from ..core.services.apeks_db_state_staff_positions_service import (
    get_apeks_db_state_staff_positions_service,
)
from ..core.services.apeks_db_state_staff_service import (
    get_apeks_db_state_staff_service,
    process_state_staff_data,
)
from ..core.services.base_apeks_api_service import data_processor
from ..staff.func import process_stable_staff_data

EXTENSION_NUMBER_LENGTH = 3


@dataclass
class Departments:
    """
    Класс для хранения информации о подразделениях загруженной из Апекс-ВУЗ.

    Attributes:
    ----------
        departments: list
            список словарей с информацией о подразделениях в формате:
            departments [
                { 'id': 'id', 'title': 'название подразделения', 'parent_id': 'вышестоящее подразделение' },
                {...}, ...
            ]

    Methods:
    -------
        get_children (dep_id: int | str) -> list
            список подразделений, входящих в состав подразделения с заданным id
        get_department(dep_id: int | str) -> dict
            информация о подразделении с заданным id
    """

    departments: list = field(default_factory=list)

    async def update(self):
        state_departments_service = get_db_apeks_state_departments_service()
        departments = await state_departments_service.get()

        # TODO проработать вопрос отображения сразу двух справочников
        # branch_id = None
        # if has_permission(PermissionsConfig.USER_HEAD_OFFICE_PERMISSION):
        #     branch_id = None
        # if has_permission(PermissionsConfig.USER_BRANCH_OFFICE_1_PERMISSION):
        #     branch_id = '1'
        branch_id = None

        self.departments = [
            {"id": dep["id"], "title": dep["name"], "parent_id": dep["parent_id"]}
            for dep in departments if dep.get("branch_id") == branch_id
        ]

    async def get_all(self) -> list:
        if not self.departments:
            await self.update()
        return self.departments

    async def get_children(self, dep_id: int | str) -> list | None:
        dep_id = None if dep_id == "0" else dep_id
        departments = await self.get_all()
        return [
            {"id": dep["id"], "title": dep["title"]}
            for dep in departments
            if dep["parent_id"] == dep_id
        ]

    async def get_department(self, dep_id) -> dict | None:
        if dep_id == "0":
            return {"id": "0", "title": "root", "parent_id": "0"}
        departments = await self.get_all()
        for dep in departments:
            if dep["id"] == dep_id:
                return dep
        return None


@dataclass
class Abonents:
    """
    Класс для хранения информации о сотрудниках загруженной из Апекс-ВУЗ.

    Attributes:
    ----------
        abonents: list
            список словарей с информацией о сотрудниках в формате:
            abonents [
                {
                    'id': 'id',
                    'post': 'должность',
                    'surname': 'Фамилия',
                    'name': 'Имя',
                    'patronymic': 'Отчество',
                    'rank': 'звание',
                    'extension': ['тлф', 'тлф', ...],
                    'landline': ['тлф', 'тлф', ...],
                    'department': 'название подразделения'
                },
                {...}, ...
            ]

    Methods:
    -------
        get_for_department(self, dep_id: int | str) -> list
            список абонентов, входящих в состав подразделения с заданным id
        get_all() -> list
            полный список абонентов
    """

    abonents: list = field(default_factory=list)

    async def update(self):
        working_date = dt.date.today()
        staff_history_service = get_db_apeks_state_staff_history_service()
        staff_history = await staff_history_service.get_staff_for_date(working_date)
        # id работающих на текущую дату сотрудников
        staff_ids = {
            item.get("staff_id"): item
            for item in staff_history
            if item.get("vacancy_id") and item.get("value") == "1"
        }
        # список сотрудников
        state_staff_service = get_apeks_db_state_staff_service()
        state_staff = process_state_staff_data(await state_staff_service.get())
        state_special_ranks_service = get_apeks_db_state_special_ranks_service()
        # список рангов
        state_special_ranks = data_processor(await state_special_ranks_service.list())
        state_staff_positions_service = get_apeks_db_state_staff_positions_service()
        # список должностей
        state_staff_positions = data_processor(
            await state_staff_positions_service.list()
        )
        full_staff_data = process_stable_staff_data(
            staff_ids, state_staff_positions, state_staff, state_special_ranks
        )
        state_staff_field_data_service = get_apeks_db_state_staff_field_data_service()
        # телефонные номера
        field_data = await state_staff_field_data_service.get(field_id="1")
        state_staff_field_data = data_processor(field_data, "staff_id")
        self.abonents = []
        for item in full_staff_data:
            extension_number = []
            landline_number = []
            phone_rec = state_staff_field_data.get(item["staff_id"])
            if phone_rec:
                # разбиваем список телефонов
                phones = phone_rec["data"].split(", ")
                # если длинна номера меньше заданного значения, то это внутренний номер
                for phone in phones:
                    if len(phone) > EXTENSION_NUMBER_LENGTH:
                        landline_number.append(phone)
                    else:
                        extension_number.append(phone)
            abonent = {
                "id": item["staff_id"],
                "post": item["position"],
                "surname": item["full_name"].split(" ")[0],
                "name": item["full_name"].split(" ")[1],
                "patronymic": item["full_name"].split(" ")[2],
                "rank": item["rank"] if item["rank"] else "",
                "extension": extension_number,
                "landline": landline_number,
                "department": item["department_id"],
            }
            self.abonents.append(abonent)

    async def get_all(self) -> list:
        if not self.abonents:
            await self.update()
        return self.abonents

    async def get_for_department(self, dep_id: int | str) -> list:
        abons = await self.get_all()
        return [abon for abon in abons if abon["department"] == dep_id]
