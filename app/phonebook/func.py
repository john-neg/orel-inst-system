from .classes import Abonents, Departments


def find_by_key(iterable: list, key: str, value: str | int) -> int:
    """
    Поиск по списку словарей по заданному ключу.

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


async def build_branch(path: list, branch: dict, departments: Departments, abonents: Abonents):
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
    departments: Departments
        данные о подразделениях
    abonents: Abonents
        данные об абонентах

    Returns
    -------
    После каждого вызова, к дереву будут добавляться новые ветки, которые были указаны в параметре path

    """
    if not branch:
        branch["id"] = path[0]
        branch["title"] = (await departments.get_department(path[0]))["title"]
    if not branch.get("departments"):
        branch["departments"] = await departments.get_children(path[0])
    if not branch.get("abonents"):
        branch["abonents"] = await abonents.get_for_department(path[0])
    if len(path) > 2:
        if not branch.get("show"):
            branch["show"] = {"departments": []}
        b = set(branch["show"]["departments"])
        b.add(path[1])
        branch["show"]["departments"] = list(b)
        await build_branch(
            path[1:],
            branch["departments"][find_by_key(branch["departments"], "id", path[1])],
            departments,
            abonents
        )
    else:
        if not branch.get("show"):
            branch["show"] = {"abonents": []}
        b = set(branch["show"]["abonents"])
        b.add(path[1])
        branch["show"]["abonents"] = list(b)
        return


async def search(search_str: str, departments: Departments, abonents: Abonents) -> dict:
    """
    Поиск информации в базе Апекс-ВУЗ по введенной строке.

    Parameters
    ----------
        search_str: str
            строка поиска
        departments: Departments
            данные о подразделениях
        abonents: Abonents
            данные об абонентах

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
        if (
            lower_search_str in abon["surname"].lower()
            or lower_search_str in abon["name"].lower()
            or lower_search_str in abon["patronymic"].lower()
            or lower_search_str in "".join(abon["extension"])
            or lower_search_str in "".join(abon["landline"])
        ):
            path = [abon["id"]]
            parent = abon["department"]
            while parent:
                path.append(parent)
                parent = (await departments.get_department(parent))["parent_id"]
            path.append("0")
            await build_branch(path[::-1], response, departments, abonents)
    return response


async def get(dep_id: int | str, departments: Departments, abonents: Abonents) -> dict:
    """
    Получение информации о структуре подразделения по его id.

    Parameters
    ----------
        dep_id: int | str
            id подразделения.
        departments: Departments
            данные о подразделениях
        abonents: Abonents
            данные об абонентах

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
        "id": dep_id,
        "title": (await departments.get_department(dep_id))["title"],
        "departments": await departments.get_children(dep_id),
        "abonents": await abonents.get_for_department(dep_id),
    }
    return response
