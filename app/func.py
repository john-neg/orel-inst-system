from app import app
import requests
from app.classes import ApeksStaff


def get_staff(department_id):  # получение списка id преподавателей кафедры и расстановка по должностям
    state_staff_positions = requests.get(app.config['URL'] + '/api/call/system-database/get' + app.config['TOKEN']
                                         + '&table=state_staff_positions').json()['data']
    state_staff_history = requests.get(app.config['URL'] + '/api/call/system-database/get' + app.config['TOKEN']
                                       + '&table=state_staff_history' + '&filter[department_id]='
                                       + str(department_id)).json()['data']

    def staff_sort(staff_id):  # получение кода сортировки л/с по должности
        position_id = ''
        for history in state_staff_history:
            if history.get('staff_id') == str(staff_id):
                position_id = history.get('position_id')
        for k in state_staff_positions:
            if k.get('id') == position_id:
                return k.get('sort')

    def staff_name(staff_id):  # сокращенное имя преподавателя без звания
        if ApeksStaff.staff[str(department_id)][str(staff_id)]['specialRank'] is None:
            return ApeksStaff.staff[str(department_id)][str(staff_id)]['shortName']
        else:
            rank_name = ApeksStaff.staff[str(department_id)][str(staff_id)]['specialRank']['name_short']
            return ApeksStaff.staff[str(department_id)][str(staff_id)]['shortName'].replace(rank_name + ' ', '')

    sort_dict = {}
    for i in ApeksStaff.staff[str(department_id)].keys():
        sort_dict[i] = int(staff_sort(i))
    a = sorted(sort_dict.items(), key=lambda x: x[1], reverse=True)

    prepod_dict = {}
    for i in range(len(a)):
        prepod_dict[a[i][0]] = staff_name(a[i][0])
    return prepod_dict
