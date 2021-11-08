from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from datetime import date
from wtforms.validators import DataRequired


class DepartmentForm(FlaskForm):
    department = SelectField('Кафедра:', coerce=str, validators=[DataRequired()])
    submit = SubmitField('Выбор')


class CalendarForm(DepartmentForm):
    year = SelectField('Год', coerce=str, choices=[
        date.today().year - 1,
        date.today().year,
        date.today().year + 1,
        ], default=date.today().year, validators=[DataRequired()])
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
        ], default=date.today().month, validators=[DataRequired()])
    prepod = SelectField('Преподаватель', coerce=str, validators=[DataRequired()])
    get_ical = SubmitField('Экспорт в формате iCal')
    get_xlsx = SubmitField('Экспорт в формате Excel')
