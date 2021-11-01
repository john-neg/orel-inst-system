from app import app
import requests
from datetime import date
# import config


def active_staff_id():  # ID of first active staff member
    return requests.get(app.config['URL'] + '/api/call/system-database/get' + app.config['TOKEN']
                        + '&table=state_staff'
                        + '&filter[active]=1').json()['data'][0]['id']


def departments():
    data = requests.get(app.config['URL'] + '/api/call/schedule-schedule/staff' + app.config['TOKEN']
                        + '&staff_id=' + active_staff_id()
                        + '&month=' + date.today().strftime('%m')
                        + '&year=' + date.today().strftime('%Y'))
    return data.json()['data']['departments']


def staff():
    data = requests.get(app.config['URL'] + '/api/call/schedule-schedule/staff' + app.config['TOKEN']
                        + '&staff_id=' + active_staff_id()
                        + '&month=' + date.today().strftime('%m')
                        + '&year=' + date.today().strftime('%Y'))
    return data.json()['data']['staff']
