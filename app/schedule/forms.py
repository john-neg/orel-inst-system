from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets.core import html_params

from config import ApeksConfig as Apeks
from ..core.forms import ChooseDepartment


class CalendarForm(ChooseDepartment):
    """Форма для экспорта расписания."""

    year = SelectField(
        "Год",
        coerce=int,
        validators=[DataRequired()],
    )
    month = SelectField(
        "Месяц",
        coerce=int,
        choices=[(k, v.title()) for k, v in Apeks.MONTH_DICT.items()],
        validators=[DataRequired()],
    )
    staff = SelectField("Преподаватель", coerce=int, validators=[DataRequired()])
    ical_exp = SubmitField("Экспорт в iCal")
    xlsx_exp = SubmitField("Экспорт в Excel")


class DisciplineForm(FlaskForm):
    '''Форма для вывода расписания дисциплины для группы.'''

    year = SelectField(
        "Год:",
        coerce=int,
        validators=[DataRequired()],
        render_kw={'onchange': 'this.form.submit()'}
    )

    department = SelectField(
        'Кафедра:',
        choices=[('0', '-- выберите кафедру --')],
        coerce=int,
        validators=[DataRequired()],
        render_kw={'onchange': 'this.form.submit()'}
    )

    discipline = SelectField(
        'Дисциплина:',
        choices=[('0', '-- выберите дисциплину --')],
        coerce=int,
        validators=[DataRequired()],
        render_kw = {'onchange': 'this.form.submit()'}
    )

    group = SelectField(
        'Группа:',
        choices=[('0', '-- выберите группу --')],
        coerce=int,
        validators=[DataRequired()],
        render_kw = {'onchange': 'this.form.submit()'},
        id='group_selector'
    )
