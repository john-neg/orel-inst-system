from datetime import date
from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired


class LoadReportForm(FlaskForm):
    department = SelectField("Кафедра:", coerce=str, validators=[DataRequired()])
    year = SelectField(
        "Год",
        coerce=str,
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
        coerce=str,
        choices=[
            (1, "Январь"),
            (2, "Февраль"),
            (3, "Март"),
            (4, "Апрель"),
            (5, "Май"),
            (6, "Июнь"),
            (7, "Июль"),
            (8, "Август"),
            ('январь-август', "(Январь-Август) полугодие"),
            (9, "Сентябрь"),
            (10, "Октябрь"),
            (11, "Ноябрь"),
            (12, "Декабрь"),
            ('сентябрь-декабрь', "(Сентябрь-Декабрь) полугодие"),
        ],
        default=date.today().month,
        validators=[DataRequired()],
    )
