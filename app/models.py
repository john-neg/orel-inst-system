import config
import requests
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login
from datetime import date


class ApeksData:
    # getting ID of first active user (need to make general API data request)
    payload = {'table': 'state_staff',
               'filter[active]': '1'}
    active_staff_id = requests.get(app.config['URL'] + '/api/call/system-database/get?token='
                                   + app.config['TOKEN'], params=payload).json()['data'][0]['id']

    # getting data about organisation structure
    payload = {'staff_id': active_staff_id,
               'month': date.today().strftime('%m'),
               'year': date.today().strftime('%Y')}
    data = requests.get(app.config['URL'] + '/api/call/schedule-schedule/staff?token='
                        + app.config['TOKEN'], params=payload)
    # getting data about recent staff
    staff = data.json()['data']['staff']
    # getting data about divisions
    departments = data.json()['data']['departments']
    # getting data about disciplines
    payload = {'table': 'plan_disciplines',
               'filter[level]': '3'}
    plan_disciplines = requests.get(app.config['URL'] + '/api/call/system-database/get?token='
                                    + app.config['TOKEN'], params=payload).json()['data']


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Integer(), default=config.ROLE_USER)

    def __repr__(self):
        return '{}'.format(self.username)

    def get_role_id(self):
        return '{}'.format(self.role)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
