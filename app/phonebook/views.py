from . import phonebook_bp
from flask import render_template, request, jsonify

from .classes import Abonents, Departments
from .func import get, search
from ..core.func.app_core import timed_lru_cache


@timed_lru_cache(360, maxsize=1024)
def get_departments():
    """Возвращает экземпляр класса для хранения списка подразделений."""
    return Departments()


@timed_lru_cache(360, maxsize=1024)
def get_abonents():
    """Возвращает экземпляр класса для хранения списка абонентов."""
    return Abonents()


@phonebook_bp.route('/phonebook/get_data', methods=['GET'])
async def get_data():
    if request.method == 'GET':
        departments = get_departments()
        abonents = get_abonents()
        data_get = request.args.get('get')
        data_search = request.args.get('search')
        response = None
        # обработка запроса 'get', запрос структуры конкретного подразделения по id
        if data_get:
            response = await get(data_get, departments, abonents)
        # обработка запроса 'search', поиск по введенному значению
        if data_search:
            response = await search(data_search, departments, abonents)
        return jsonify(response)
    return None


@phonebook_bp.route("/phonebook", methods=["GET"])
async def phonebook():
    return render_template("phonebook/phonebook.html")
