import requests
from app import app
from datetime import date


class ApeksStaff:
    active_staff_id = requests.get(app.config['URL'] + '/api/call/system-database/get' + app.config['TOKEN']
                                   + '&table=state_staff' + '&filter[active]=1').json()['data'][0]['id']
    data = requests.get(app.config['URL'] + '/api/call/schedule-schedule/staff' + app.config['TOKEN']
                        + '&staff_id=' + active_staff_id
                        + '&month=' + date.today().strftime('%m')
                        + '&year=' + date.today().strftime('%Y'))
    staff = data.json()['data']['staff']
    departments = data.json()['data']['departments']
    plan_disciplines = requests.get(app.config['URL'] + '/api/call/system-database/get' + app.config['TOKEN']
                                    + '&table=plan_disciplines' + '&filter[level]=3').json()['data']
