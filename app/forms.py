from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, BooleanField, SubmitField
from datetime import date
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Войти')


class CalendarForm(FlaskForm):
    department = SelectField('Кафедра:', coerce=str, validators=[DataRequired()])
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


class CompetenciesLoad(FlaskForm):
    edu_spec = SelectField('Специальность:', coerce=str, validators=[DataRequired()])
    edu_plans = SelectField('План:', coerce=str, validators=[DataRequired()])
