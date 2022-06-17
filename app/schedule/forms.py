from datetime import date

from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

from common.forms import ChooseDepartment
from config import ApeksConfig as Apeks


class CalendarForm(ChooseDepartment):
    year = SelectField(
        "Год",
        coerce=int,
        choices=[
            date.today().year - 1,
            date.today().year,
            date.today().year + 1,
        ],
        default=date.today().year,
        validators=[DataRequired()],
    )
    month = SelectField(
        "Месяц",
        coerce=int,
        choices=[(k, v.title()) for k, v in Apeks.MONTH_DICT.items()],
        default=date.today().month,
        validators=[DataRequired()],
    )
    staff = SelectField("Преподаватель", coerce=int, validators=[DataRequired()])
    ical_exp = SubmitField("Экспорт в iCal")
    xlsx_exp = SubmitField("Экспорт в Excel")
