from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, BooleanField, SubmitField, IntegerField
from datetime import date
from wtforms.validators import DataRequired, Length, NumberRange


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


class ChoosePlan(FlaskForm):
    edu_spec = SelectField('Специальность:', coerce=str, validators=[DataRequired()])
    edu_plan = SelectField('План:', coerce=str, validators=[DataRequired()])


class WorkProgramUpdate(ChoosePlan):  # добавить валидаторы для дат
    date_methodical = StringField('Дата методического совета', validators=[DataRequired(), Length(min=10, max=10, message='Формат даты - ГГГГ-ММ-ДД')])
    document_methodical = IntegerField('Номер документа методического совета', validators=[DataRequired(), NumberRange(min=1, max=99)])
    date_academic = StringField('Дата Ученого совета', validators=[DataRequired(), Length(min=10, max=10)])
    document_academic = IntegerField('Номер документа Ученого совета', validators=[DataRequired(), NumberRange(min=1, max=99)])
    date_approval = StringField('Дата утверждения', validators=[DataRequired(), Length(min=10, max=10)])
