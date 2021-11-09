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


def staff_name(staff_id, department_id):  # сокращенное имя преподавателя без звания
    if ApeksStaff.staff[str(department_id)][str(staff_id)]['specialRank'] is None:
        return ApeksStaff.staff[str(department_id)][str(staff_id)]['shortName']
    else:
        rank_name = ApeksStaff.staff[str(department_id)][str(staff_id)]['specialRank']['name_short']
        return ApeksStaff.staff[str(department_id)][str(staff_id)]['shortName'].replace(rank_name + ' ', '')


def lessons_exp_cal(department_id, staff_id, month, year):  # формирование данных для экспорта iCAl

    def get_lessons(staff_id, month, year):  # получение списка занятий
        response = requests.get(app.config['URL'] + '/api/call/schedule-schedule/staff' + app.config['TOKEN']
                                + '&staff_id=' + str(staff_id) + '&month=' + str(month) + '&year=' + str(year))
        return response.json()['data']['lessons']

    def calendarname(i):  # формирование сборного имени для календаря
        class_type_name = lessons[i]['class_type_name']
        text = class_type_name + topic_code(i) + shortdiscname(lessons[i]['discipline_id']) + ' ' + lessons[i][
            'groupName']
        return text

    def timestart_cal(i):  # время начала занятия
        date = lessons[i]['date'].split('.')
        time = lessons[i]['lessonTime'].split(' - ')[0]
        utffix = str(int(time.split(':')[0]) - 3)
        if len(utffix) < 2:
            utffix = f'0{utffix}'
        return date[2] + date[1] + date[0] + 'T' + utffix + time.split(':')[1] + '00Z'

    def timeend_cal(i):  # время окончания занятия
        date = lessons[i]['date'].split('.')
        time = lessons[i]['lessonTime'].split(' - ')[1]
        utffix = str(int(time.split(':')[0]) - 3)
        if len(utffix) < 2:
            utffix = f'0{utffix}'
        return date[2] + date[1] + date[0] + 'T' + utffix + time.split(':')[1] + '00Z'

    def topic_name(i):  # получение темы занятия
        if lessons[i]['topic_name'] is None:
            topic_name = ' '
        else:
            topic_name = lessons[i]['topic_name']
        return topic_name

    def topic_code(i):  # получение № темы занятия
        if lessons[i]['topic_code'] != '' and lessons[i]['topic_code'] is not None:
            topic_code = ' (' + lessons[i]['topic_code'] + ') '
        else:
            topic_code = ' '
        return topic_code

    def shortdiscname(discipline_id):  # короткое имя дисциплины
        plan_disciplines = ApeksStaff.plan_disciplines
        for i in range(len(plan_disciplines)):
            if plan_disciplines[i]['id'] == str(discipline_id):
                return plan_disciplines[i]['name_short']

    lessons = get_lessons(staff_id, month, year)

    if not lessons:
        return 'no data'
    else:
        lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'CALSCALE:GREGORIAN',
            'METHOD:PUBLISH',
            'X-WR-TIMEZONE:Europe/Moscow',
            'BEGIN:VTIMEZONE',
            'TZID:Europe/Moscow',
            'X-LIC-LOCATION:Europe/Moscow',
            'BEGIN:STANDARD',
            'TZOFFSETFROM:+0300',
            'TZOFFSETTO:+0300',
            'TZNAME:MSK',
            'DTSTART:19700101T000000',
            'END:STANDARD',
            'END:VTIMEZONE',
            'BEGIN:VTIMEZONE',
            'TZID:Europe/Minsk',
            'X-LIC-LOCATION:Europe/Minsk',
            'BEGIN:STANDARD',
            'TZOFFSETFROM:+0300',
            'TZOFFSETTO:+0300',
            'TZNAME:+03',
            'DTSTART:19700101T000000',
            'END:STANDARD',
            'END:VTIMEZONE']

        with open(f'app/files/{staff_name(staff_id, department_id)} {month}-{year}.ics', "w") as f:
            for line in lines:
                f.write(line)
                f.write('\n')
            f.write('\n')
            for i in range(len(lessons)):
                f.write('BEGIN:VEVENT' + '\n')
                f.write('DTSTART:' + timestart_cal(i) + '\n')
                f.write('DTEND:' + timeend_cal(i) + '\n')
                f.write('DESCRIPTION:' + topic_code(i) + topic_name(i) + '\n')
                f.write('LOCATION:' + lessons[i]['classroom'] + '\n')
                f.write('SEQUENCE:0' + '\n')
                f.write('STATUS:CONFIRMED' + '\n')
                f.write('SUMMARY:' + calendarname(i) + '\n')
                f.write('TRANSP:OPAQUE' + '\n')
                f.write('BEGIN:VALARM' + '\n')
                f.write('ACTION:DISPLAY' + '\n')
                f.write('DESCRIPTION:This is an event reminder' + '\n')
                f.write('TRIGGER:-P0DT0H30M0S' + '\n')
                f.write('END:VALARM' + '\n')
                f.write('END:VEVENT' + '\n')
                f.write('\n')
            f.write('END:VCALENDAR')
        f.close()
    return f'{staff_name(staff_id, department_id)} {month}-{year}.ics'
