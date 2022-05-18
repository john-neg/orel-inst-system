from datetime import date

from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired
from config import ApeksConfig as Apeks


class CalendarForm(FlaskForm):
    department = SelectField("Кафедра:", coerce=int, validators=[DataRequired()])
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
