from app import app
from app.func import *
from flask import render_template
import config
from datetime import date

# ID of first active staff member
base_staff_id = requests.get(app.config['URL'] + '/api/call/system-database/get' + app.config['TOKEN']
                                + '&table=state_staff'
                                + '&filter[active]=1').json()['data'][0]['id']

# getting base Apeks-VUZ schedule API data
schedule_data_raw = requests.get(app.config['URL'] + '/api/call/schedule-schedule/staff' + app.config['TOKEN']
                                 + '&staff_id=' + base_staff_id
                                 + '&month=' + date.today().strftime('%m')
                                 + '&year=' + date.today().strftime('%Y'))
schedule_data = schedule_data_raw.json()['data']
departments = schedule_data['departments']
staff = schedule_data['staff']

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/calendar')
def calendar():
    return render_template('calendar.html', departments=departments)

@app.route('/competencies')
def competencies():
    return render_template('competencies.html')