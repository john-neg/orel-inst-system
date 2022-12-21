from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

from config import ApeksConfig as Apeks
from app.common.forms import ChooseDepartment


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
