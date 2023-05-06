import os
from dataclasses import dataclass

from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    TextAreaField, FloatField, IntegerField, SelectField,
)
from wtforms.validators import DataRequired, NumberRange

from app import db
from app.common.func.app_core import read_json_file, transliterate
from config import BASEDIR

FILE_DIR = os.path.join(BASEDIR, "app", "tools", "data_payment", )


def create_payment_form(base_items, **kwargs):
    class PaymentForm(FlaskForm):
        pass

    # base_items: list[db.Model]

    for base_item in base_items:
        label = f"base_{transliterate(base_item.name)}"
        field = SelectField(
            label=base_item.name,
            coerce=int,
            choices=list(reversed(
                [(val, key) for key, val in base_item.get_current_values().items()])),
            validators=[DataRequired()]
        )
        setattr(PaymentForm, label, field)

    return PaymentForm(**kwargs)
    # # base_data = read_json_file(os.path.join(FILE_DIR, "base_data.json"))
    #
    # base_position = SelectField(
    #     # label=rates_data.get('base_position').get('label'),
    #     coerce=int,
    #     # choices=list(reversed([(val, key) for key, val in rates_data.get('base_position').get('data').items()])),
    #     validators=[DataRequired()]
    # )
    # # years_of_duty = IntegerField(
    # #     label=rates_data.get('years_of_duty').get('label'),
    # #     validators=[DataRequired(), NumberRange(min=0, max=60, message="Введите число от 0 до 60")]
    # # )
    # police_rank = SelectField(
    #     # label=rates_data.get('police_rank').get('label'),
    #     coerce=int,
    #     # choices=list(reversed([(val, key) for key, val in rates_data.get('police_rank').get('data').items()])),
    #     validators=[DataRequired()]
    # )
