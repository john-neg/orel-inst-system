import os

from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    TextAreaField, FloatField, IntegerField, SelectField,
)
from wtforms.validators import DataRequired, NumberRange

from app.common.func.app_core import read_json_file
from config import BASEDIR

PAYMENT_FILE_DIR = os.path.join(BASEDIR, "app", "tools", "payment", )


class PaymentForm(FlaskForm):
    rates_data = read_json_file(os.path.join(PAYMENT_FILE_DIR,
                                             "../../../tools/data/rates_data.json"))
    base_position = SelectField(
        label=rates_data.get('base_position').get('label'),
        coerce=int,
        choices=list(reversed([(val, key) for key, val in rates_data.get('base_position').get('data').items()])),
        validators=[DataRequired()]
    )
    years_of_duty = IntegerField(
        label=rates_data.get('years_of_duty').get('label'),
        validators=[DataRequired(), NumberRange(min=0, max=60, message="Введите число от 0 до 60")]
    )
    police_rank = SelectField(
        label=rates_data.get('police_rank').get('label'),
        coerce=int,
        choices=list(reversed([(val, key) for key, val in rates_data.get('police_rank').get('data').items()])),
        validators=[DataRequired()]
    )

