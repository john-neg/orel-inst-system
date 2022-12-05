from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired


class LoadReportForm(FlaskForm):
    department = SelectField("Кафедра:", coerce=int, validators=[DataRequired()])
    year = SelectField(
        "Год",
        coerce=int,
        validators=[DataRequired()],
    )
    month = SelectField(
        "Месяц",
        coerce=str,
        choices=[
            ('1-1', "Январь"),
            ('2-2', "Февраль"),
            ('3-3', "Март"),
            ('4-4', "Апрель"),
            ('5-5', "Май"),
            ('6-6', "Июнь"),
            ('7-7', "Июль"),
            ('8-8', "Август"),
            ('1-8', "(Январь-Август) полугодие"),
            ('9-9', "Сентябрь"),
            ('10-10', "Октябрь"),
            ('11-11', "Ноябрь"),
            ('12-12', "Декабрь"),
            ('9-12', "(Сентябрь-Декабрь) полугодие"),
        ],
        validators=[DataRequired()],
    )
    load_report = SubmitField('Cформировать')
