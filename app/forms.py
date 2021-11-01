from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextAreaField, SelectField, validators
from datetime import date
from app.func import departments


class CalendarForm(Form):
    def dict_to_form(self, dict_name=departments()):
        for k, v in dict_name.items():
            setattr(self, k, v)
    department = SelectField('Кафедра', coerce=str, choices=[dict_to_form()])

    month = SelectField('Месяц', coerce=str, choices=[
        (1, 'Январь'),
        (2, 'Февраль'),
        (3, 'Март'),
        (4, 'Апрель'),
        (5, 'Май'),
        (6, 'Июнь'),
        (7, 'Июль'),
        (8, 'Август'),
        (9, 'Сентябрь'),
        (10, 'Октябрь'),
        (11, 'Ноябрь'),
        (12, 'Декабрь'),
    ])

    year = SelectField('Год', coerce=str, choices=[
        date.today().year - 1,
        date.today().year,
        date.today().year + 1,
    ])
