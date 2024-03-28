import asyncio

from . import bp_phbook, bp_phbook_get_data
from flask import render_template, request, jsonify

import datetime as dt
import time
import threading

from ..core.services.apeks_db_state_departments_service import get_db_apeks_state_departments_service
from ..core.services.apeks_db_state_staff_field_data_service import get_apeks_db_state_staff_field_data_service
from ..core.services.apeks_db_state_staff_history_service import get_db_apeks_state_staff_history_service
from ..core.services.apeks_db_state_staff_positions_service import get_apeks_db_state_staff_positions_service
from ..core.services.apeks_db_state_special_ranks_service import get_apeks_db_state_special_ranks_service
from ..core.services.apeks_db_state_staff_service import get_apeks_db_state_staff_service, process_state_staff_data
from ..core.services.base_apeks_api_service import data_processor
from ..staff.func import process_stable_staff_data

EXTENSION_NUMBER_LENGTH = 3  # длинна внутреннего телефонного номера абонента
UPDATE_INTERVAL = 600  # периодичность синхронизации данных с Апекс-ВУЗ (сек.)


class Departments:
    """
    Класс для хранения информации о подразделениях загруженной из Апекс-ВУЗ
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

    departments: list

    def __init__(self):
        self.departments = []

    async def update(self):
        state_departments_service = get_db_apeks_state_departments_service()
        deps = await state_departments_service.get()
        self.departments = []
        self.departments = [{
            'id': dep['id'],
            'title': dep['name'],
            'parent_id': dep['parent_id']
        } for dep in deps]

    async def get_all(self) -> list:
        if not self.departments:
            await self.update()
        return self.departments

    async def get_children(self, dep_id: int | str) -> list | None:
        dep_id = None if dep_id == '0' else dep_id
        deps = await self.get_all()
        return [{'id': dep['id'], 'title': dep['title']} for dep in deps if dep['parent_id'] == dep_id]

    async def get_department(self, dep_id) -> dict | None:
        if dep_id == '0':
            return {'id': '0', 'title': 'root', 'parent_id': '0'}
        deps = await self.get_all()
        for dep in deps:
            if dep['id'] == dep_id:
                return dep
        return None


class Abonents:  # класс для хранения данных о сотрудниках из Апекса
    """
    Класс для хранения информации о сотрудниках загруженной из Апекс-ВУЗ
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

    abonents: list

    def __init__(self):
        self.abonents = []

    async def update(self):
        working_date = dt.date.today()
        staff_history_service = get_db_apeks_state_staff_history_service()
        staff_history = await staff_history_service.get_staff_for_date(working_date)
        staff_ids = {  # id работающих на текущую дату сотрудников
            item.get('staff_id'): item
            for item in staff_history
            if item.get('vacancy_id') and item.get('value') == '1'
        }
        state_staff_service = get_apeks_db_state_staff_service()  # список сотрудников
        state_staff = process_state_staff_data(await state_staff_service.get())
        state_special_ranks_service = get_apeks_db_state_special_ranks_service()
        state_special_ranks = data_processor(await state_special_ranks_service.list())  # список рангов
        state_staff_positions_service = get_apeks_db_state_staff_positions_service()
        state_staff_positions = data_processor(await state_staff_positions_service.list())  # список должностей
        full_staff_data = process_stable_staff_data(
            staff_ids, state_staff_positions, state_staff, state_special_ranks
        )
        state_staff_field_data_service = get_apeks_db_state_staff_field_data_service()
        field_data = await state_staff_field_data_service.get(field_id='1')  # телефонные номера
        state_staff_field_data = data_processor(field_data, 'staff_id')
        self.abonents = []
        for item in full_staff_data:
            extension_number = []
            landline_number = []
            phone_rec = state_staff_field_data.get(item['staff_id'])
            if phone_rec:
                phones = phone_rec['data'].split(', ')  # разбиваем список телефонов
                for phone in phones:
                    # если длинна номера меньше заданного значения, то это внутренний номер
                    if len(phone) > EXTENSION_NUMBER_LENGTH:
                        landline_number.append(phone)
                    else:
                        extension_number.append(phone)
            abonent = {
                'id': item['staff_id'],
                'post': item['position'],
                'surname': item['full_name'].split(' ')[0],
                'name': item['full_name'].split(' ')[1],
                'patronymic': item['full_name'].split(' ')[2],
                'rank': item['rank'] if item['rank'] else '',
                'extension': extension_number,
                'landline': landline_number,
                'department': item['department_id']
            }
            self.abonents.append(abonent)

    async def get_all(self) -> list:
        if not self.abonents:
            await self.update()
        return self.abonents

    async def get_for_department(self, dep_id: int | str) -> list:
        abons = await self.get_all()
        return [abon for abon in abons if abon['department'] == dep_id]


departments = Departments()  # экземпляр класса для хранения списка подразделений
abonents = Abonents()  # экземпляр класса для хранения списка абонентов


# обновление (синхронизация) сведений содержащихся в экземплярах классов Departments и Abonents
# с данными из Апекс-ВУЗ
def update(is_run: threading.Event):
    while is_run.is_set():
        asyncio.run(departments.update())
        asyncio.run(abonents.update())
        time.sleep(UPDATE_INTERVAL)


updater_run = threading.Event()
updater_run.set()
updater = threading.Thread(target=update, args=(updater_run,), daemon=True)
updater.start()
# to stop update call: update_run.clear()


def find_by_key(iterable: list, key: str, value: str | int) -> int:
    """
    Поиск по списку словарей по заданному ключу
    Parameters
    ----------
    iterable: list
        список словарей
    key: str
        ключ по которому производится поиск
    value
        искомая величина

    Returns
    -------
    index: int
        индекс найденного словаря в списке, у которого значение заданного ключа соответствует заданной величине

    """
    for index, dict_ in enumerate(iterable):
        if key in dict_ and dict_[key] == value:
            return index


async def build_branch(path: list, branch: dict):
    """
    Построение дерева из найденных путей к абонентам.

    Parameters
    ----------
    path: list
        узлы дерева, через которые необходимо пройти, чтобы добраться до абонента (путь к абоненту по дереву).
        в формате: [0, 28, 29, 353], где 0 - корень дерева, 353 - id абонента
    branch: dict
        дерево к которому будет добавлен указанный путь
        пустое дерево, представляет собой пустой словарь {}
        заполненное дерево:
        {
            'id': 'id',
            'title': 'название подразделения',
            'show': {
                'abonents': ['id', 'id', ...],
                'departments': ['id', 'id', ...]
            } | None,
            'abonents': [
                {
                    'id': 'id',
                    'post': 'должность',
                    'surname': 'Фамилия',
                    'name': 'Имя',
                    'patronymic': 'Отчество',
                    'rank': 'звание',
                    'extension': ['тлф', 'тлф', ...],
                    'landline': ['тлф', 'тлф', ...]
                },
                ...
            ] | None,
            'deparments': [
                {
                    'id': 'id',
                    'title': 'название подразделения',
                    'show': {...},
                    'abonents': [...] | None,
                    'departments': [...] | None
                },
                ...
            ] | None
        }

    Returns
    -------
    После каждого вызова, к дереву будут добавляться новые ветки, которые были указаны в параметре path

    """
    if not branch:
        branch['id'] = path[0]
        branch['title'] = (await departments.get_department(path[0]))['title']
    if not branch.get('departments'):
        branch['departments'] = await departments.get_children(path[0])
    if not branch.get('abonents'):
        branch['abonents'] = await abonents.get_for_department(path[0])
    if len(path) > 2:
        if not branch.get('show'):
            branch['show'] = {'departments': []}
        b = set(branch['show']['departments'])
        b.add(path[1])
        branch['show']['departments'] = list(b)
        await build_branch(path[1:], branch['departments'][find_by_key(branch['departments'], 'id', path[1])])
    else:
        if not branch.get('show'):
            branch['show'] = {'abonents': []}
        b = set(branch['show']['abonents'])
        b.add(path[1])
        branch['show']['abonents'] = list(b)
        return


async def search(search_str: str) -> dict:
    """
    Поиск информации в базе Апекс-ВУЗ по введенной строке.

    Parameters
    ----------
        search_str: str
            строка поиска.

    Returns
    ----------
        dict
            {
                'id': 'id',
                'title': 'название подразделения',
                'show': {
                    'abonents': ['id', 'id', ...],   - если необходимо отобразить только выбранных дочерних абонентов
                    'departments': ['id', 'id', ...]   - если необходимо отобразить только выбранные дочерние подразделения
                } | None,   - если необходимо отображать все дочерние объекты
                'abonents': [
                    {
                        'id': 'id',
                        'post': 'должность',
                        'surname': 'Фамилия',
                        'name': 'Имя',
                        'patronymic': 'Отчество',
                        'rank': 'звание',
                        'extension': ['тлф', 'тлф', ...],
                        'landline': ['тлф', 'тлф', ...]
                    },
                    ...
                ] | None,
                'deparments': [
                    {
                        'id': 'id',
                        'title': 'название подразделения',
                        'show': {...},
                        'abonents': [...] | None,   - заполняются, только если необходимо отобразить эту информацию
                        'departments': [...] | None   - заполняются, только если необходимо отобразить эту информацию
                    },
                    ...
                ] | None
            }
    """
    lower_search_str = search_str.lower()
    abons = await abonents.get_all()
    response = {}
    for abon in abons:
        if lower_search_str in abon['surname'].lower() or \
                lower_search_str in abon['name'].lower() or \
                lower_search_str in abon['patronymic'].lower() or \
                lower_search_str in ''.join(abon['extension']) or \
                lower_search_str in ''.join(abon['landline']):
            path = [abon['id']]
            parent = abon['department']
            while parent:
                path.append(parent)
                parent = (await departments.get_department(parent))['parent_id']
            path.append('0')
            await build_branch(path[::-1], response)
    return response


async def get(dep_id: int | str) -> dict:
    """
    Получение информации о структуре подразделения по его id.

    Parameters
    ----------
        dep_id: int | str
            id подразделения.

    Returns
    ----------
        dict
            {
                'id': 'id',
                'title': 'название подразделения',
                'show': {
                    'abonents': ['id', 'id', ...],   - если необходимо отобразить только выбранных дочерних абонентов
                    'departments': ['id', 'id', ...]   - если необходимо отобразить только выбранные дочерние подразделения
                } | None,   - если необходимо отображать все дочерние объекты
                'abonents': [
                    {
                        'id': 'id',
                        'post': 'должность',
                        'surname': 'Фамилия',
                        'name': 'Имя',
                        'patronymic': 'Отчество',
                        'rank': 'звание',
                        'extension': ['тлф', 'тлф', ...],
                        'landline': ['тлф', 'тлф', ...]
                    },
                    ...
                ] | None,
                'deparments': [
                    {
                        'id': 'id',
                        'title': 'название подразделения',
                        'show': {...},
                        'abonents': [...] | None,   - заполняются, только если необходимо отобразить эту информацию
                        'departments': [...] | None   - заполняются, только если необходимо отобразить эту информацию
                    },
                    ...
                ] | None
            }
    """
    response = {
        'id': dep_id,
        'title': (await departments.get_department(dep_id))['title'],
        'departments': await departments.get_children(dep_id),
        'abonents': await abonents.get_for_department(dep_id)
    }
    return response


@bp_phbook_get_data.route('/phonebook/get_data', methods=['GET'])
async def get_data():
    if request.method == 'GET':
        data_get = request.args.get('get')
        data_search = request.args.get('search')
        response = None
        if data_get:  # обработка запроса 'get', запрос структуры конкретного подразделения по id
            response = await get(data_get)
        if data_search:  # обработка запроса 'search', поиск по введенному значению
            response = await search(data_search)
        return jsonify(response)
    return None


@bp_phbook.route("/phonebook", methods=["GET"])
async def phonebook():
    return render_template("phonebook/phonebook.html")
