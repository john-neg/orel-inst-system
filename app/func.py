import xlsxwriter
from app import app
import requests
from app.models import ApeksData


def db_request(dbname):  # функция запроса к таблице БД без фильтра
    payload = {'token': app.config['TOKEN'],
               'table': dbname}
    response = requests.get(app.config['URL'] + '/api/call/system-database/get', params=payload)
    return response.json()['data']


def db_filter_req(dbname, sqltable,
                  sqlvalue):  # функция запроса к таблице БД (название таблицы БД, название поля БД, значение)
    payload = {'token': app.config['TOKEN'],
               'table': dbname,
               'filter[' + sqltable + ']': str(sqlvalue)}
    response = requests.get(app.config['URL'] + '/api/call/system-database/get', params=payload)
    return response.json()


def active_staff_id():  # getting ID of first active user (need to make general API data request)
    # getting ID of first active user
    payload = {'token': app.config['TOKEN'],
               'table': 'state_staff',
               'filter[active]': '1'}
    respond = requests.get(app.config['URL'] + '/api/call/system-database/get', params=payload).json()['data'][0]['id']
    return respond


def education_specialty():  # getting education_speciality data
    payload = {'token': app.config['TOKEN'],
               'table': 'plan_education_specialties'}
    request = requests.get(app.config['URL'] + '/api/call/system-database/get', params=payload)
    specialties = {}
    for i in request.json()['data']:
        specialties[i.get('id')] = i.get('name')
    return specialties


def education_plans(education_specialty_id):
    payload = {'token': app.config['TOKEN'],
               'table': 'plan_education_plans',
               'filter[data_type]': 'plan',
               'filter[education_specialty_id]': education_specialty_id,
               'filter[active]': '1'}
    request = requests.get(app.config['URL'] + '/api/call/system-database/get', params=payload)
    plans = {}
    for i in request.json()['data']:
        plans[i.get('id')] = i.get('name')
    return plans


def get_staff(department_id):  # getting staff ID and sorting by position at the department
    # getting staff range data
    payload_staff = {'token': app.config['TOKEN'],
                     'table': 'state_staff_positions'}
    state_staff_positions = requests.get(app.config['URL'] + '/api/call/system-database/get',
                                         params=payload_staff).json()['data']

    payload_history = {'token': app.config['TOKEN'],
                       'table': 'state_staff_history',
                       'filter[department_id]': str(department_id)}
    state_staff_history = requests.get(app.config['URL'] + '/api/call/system-database/get',
                                       params=payload_history).json()['data']

    def staff_sort(staff_id):  # getting sorting code by position
        position_id = ''
        for history in state_staff_history:
            if history.get('staff_id') == str(staff_id):
                position_id = history.get('position_id')
        for k in state_staff_positions:
            if k.get('id') == position_id:
                return k.get('sort')

    def short_staff_name(staff_id):  # short staff name without rank
        if ApeksData.staff[str(department_id)][str(staff_id)]['specialRank'] is None:
            return ApeksData.staff[str(department_id)][str(staff_id)]['shortName']
        else:
            rank_name = ApeksData.staff[str(department_id)][str(staff_id)]['specialRank']['name_short']
            return ApeksData.staff[str(department_id)][str(staff_id)]['shortName'].replace(rank_name + ' ', '')

    sort_dict = {}
    for i in ApeksData.staff[str(department_id)].keys():
        sort_dict[i] = int(staff_sort(i))
    a = sorted(sort_dict.items(), key=lambda x: x[1], reverse=True)

    prepod_dict = {}
    for i in range(len(a)):
        prepod_dict[a[i][0]] = short_staff_name(a[i][0])
    return prepod_dict


def staff_name(staff_id, department_id):  # short staff name without rank
    if ApeksData.staff[str(department_id)][str(staff_id)]['specialRank'] is None:
        return ApeksData.staff[str(department_id)][str(staff_id)]['shortName']
    else:
        rank_name = ApeksData.staff[str(department_id)][str(staff_id)]['specialRank']['name_short']
        return ApeksData.staff[str(department_id)][str(staff_id)]['shortName'].replace(rank_name + ' ', '')


def get_lessons(staff_id, month, year):  # getting staff lessons
    payload = {'token': app.config['TOKEN'],
               'staff_id': str(staff_id),
               'month': str(month),
               'year': str(year)}
    response = requests.get(app.config['URL'] + '/api/call/schedule-schedule/staff', params=payload)
    return response.json()['data']['lessons']


def shortdiscname(discipline_id):  # discipline short name
    plan_disciplines = ApeksData.plan_disciplines
    for i in range(len(plan_disciplines)):
        if plan_disciplines[i]['id'] == str(discipline_id):
            return plan_disciplines[i]['name_short']


# 5) template строки или значения, как для ical, лучше выносить из кода
# 6) некоторые функции функций наводят на мысль, что лучше сделать их классами
# 4) Прямое обращение к словарю опасно, так как можно получить ненайденный ключ. Лучше делать get и делать catch ошибок

def lessons_ical_exp(department_id, staff_id, month, year):  # формирование данных для экспорта iCAl

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
            name = ' '
        else:
            name = lessons[i]['topic_name']
        return name

    def topic_code(i):  # получение № темы занятия
        if lessons[i]['topic_code'] != '' and lessons[i]['topic_code'] is not None:
            code = ' (' + lessons[i]['topic_code'] + ') '
        else:
            code = ' '
        return code

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
            for lesson in range(len(lessons)):
                f.write('BEGIN:VEVENT' + '\n')
                f.write('DTSTART:' + timestart_cal(lesson) + '\n')
                f.write('DTEND:' + timeend_cal(lesson) + '\n')
                f.write('DESCRIPTION:' + topic_code(lesson) + topic_name(lesson) + '\n')
                f.write('LOCATION:' + lessons[lesson]['classroom'] + '\n')
                f.write('SEQUENCE:0' + '\n')
                f.write('STATUS:CONFIRMED' + '\n')
                f.write('SUMMARY:' + calendarname(lesson) + '\n')
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


def lessons_xlsx_exp(department_id, staff_id, month, year):  # выгрузка занятий в формате xlsx

    def calendarname(i):  # формирование сборного имени для календаря
        class_type_name = lessons[i]['class_type_name']
        text = class_type_name + topic_code(i) + shortdiscname(lessons[i]['discipline_id']) + ' ' + lessons[i][
            'groupName']
        return text

    def timestart(i):  # время начала занятия
        time = lessons[i]['lessonTime'].split(' - ')
        fulltime = lessons[i]['date'] + ' ' + time[0]
        return fulltime

    def topic_name(i):  # получение темы занятия
        if lessons[i]['topic_name'] is None:
            name = ' '
        else:
            name = lessons[i]['topic_name']
        return name

    def topic_code(i):  # получение № темы занятия
        if lessons[i]['topic_code'] != '' and lessons[i]['topic_code'] is not None:
            code = ' (' + lessons[i]['topic_code'] + ') '
        else:
            code = ' '
        return code

    lessons = get_lessons(staff_id, month, year)

    if not lessons:
        return 'no data'
    else:
        workbook = xlsxwriter.Workbook(f'app/files/{staff_name(staff_id, department_id)} {month}-{year}.xlsx')
        worksheet = workbook.add_worksheet(staff_name(staff_id, department_id))

        bold = workbook.add_format({'bold': True})
        worksheet.write('A1', 'Расписание на месяц ' + str(month) + '-' + str(year), bold)
        worksheet.write('B1', staff_name(staff_id, department_id), bold)

        a = str(3)  # отступ сверху

        # Write some data headers.
        worksheet.write('A' + a, 'Дата/время', bold)
        worksheet.write('B' + a, 'Занятие', bold)
        worksheet.write('C' + a, 'Место', bold)
        worksheet.write('D' + a, 'Тема', bold)

        # Worksheet set columns width
        worksheet.set_column(0, 0, 15)
        worksheet.set_column(1, 1, 60)
        worksheet.set_column(2, 2, 15)
        worksheet.set_column(3, 4, 50)

        # Some data we want to write to the worksheet.

        lessonexport = ()
        for lesson in range(len(lessons)):
            export = ([
                          timestart(lesson),
                          calendarname(lesson),
                          lessons[lesson]['classroom'],
                          topic_name(lesson),
                      ],)
            lessonexport += export

        # Start from the first cell below the headers.
        row = 3
        col = 0

        # Iterate over the data and write it out row by row.
        for lesson in lessonexport:
            for a in range(len(lesson)):
                worksheet.write(row, col + a, lesson[a])
            row += 1

        workbook.close()
        return f'{staff_name(staff_id, department_id)} {month}-{year}.xlsx'
