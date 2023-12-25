from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

from config import ApeksConfig as Apeks


class StableStaffForm(FlaskForm):
    finish_edit = SubmitField("Завершить редактирование")
    enable_edit = SubmitField("Разрешить редактирование")
    make_report = SubmitField("Сформировать отчет")
