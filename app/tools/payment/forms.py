import os

from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired

from app import db
from app.db.payment_models import PaymentPensionDutyCoefficient
from config import BASEDIR

FILE_DIR = os.path.join(BASEDIR, "app", "tools", "data_payment")
DEFAULT_OPTIONS = [(0, "нет")]


def create_payment_form(
    rate_items: list[db.Model],
    addon_items: list[db.Model],
    single_items: list[db.Model],
    **kwargs,
):
    class PaymentForm(FlaskForm):
        """Класс формы для расчета денежного содержания."""

        calculate = SubmitField("Рассчитать")

    # Добавляем оклады
    for item in rate_items:
        label = item.slug
        field = SelectField(
            label=item.name,
            coerce=int,
            choices=list(
                reversed([(key, val) for key, val in item.get_current_items().items()])
            ),
            validators=[DataRequired()],
        )
        setattr(PaymentForm, label, field)

    # Добавляем надбавки с множественными значениями
    for item in addon_items:
        label = item.slug
        choices = [(0, "нет")]
        choices.extend([(val, key) for key, val in item.get_values().items()])
        field = SelectField(
            label=item.name,
            coerce=float,
            choices=choices,
            validators=[DataRequired()],
        )
        setattr(PaymentForm, label, field)

    # Добавляем надбавки с единичным значением
    for item in single_items:
        label = item.slug
        field = SubmitField(
            label=item.name,
            default=item.default_state,
        )
        setattr(PaymentForm, label, field)

    # Добавляем поле для расчета пенсии в зависимости от выслуги лет
    label = "pension_duty_years"
    field = SelectField(
        label="Выслуга (полных) лет для расчета пенсии",
        coerce=float,
        choices=list(
            [
                (coeff.value, coeff.name)
                for coeff in PaymentPensionDutyCoefficient.get_all()
            ]
        ),
        validators=[DataRequired()],
    )
    setattr(PaymentForm, label, field)

    return PaymentForm(**kwargs)
