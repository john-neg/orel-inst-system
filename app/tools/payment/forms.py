import os

from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField, TextAreaField
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
            choices=[(key, val) for key, val in item.get_current_values().items()],
            validators=[DataRequired()],
        )
        setattr(PaymentForm, label, field)

    # Добавляем надбавки с множественными значениями
    for item in addon_items:
        label = item.slug
        choices = [(0, "нет")]
        choices.extend([(key, val) for key, val in item.get_values().items()])
        field = SelectField(
            label=item.name,
            coerce=int,
            choices=choices,
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
        coerce=int,
        choices=[
            (duty.id, duty.name)
            for duty in sorted(
                PaymentPensionDutyCoefficient.get_all(),
                key=lambda duty: int(duty.value),
            )
        ],
        validators=[DataRequired()],
    )
    setattr(PaymentForm, label, field)

    return PaymentForm(**kwargs)


class DocumentsAddForm(FlaskForm):

    name = TextAreaField("Название документа", validators=[DataRequired()])
    submit = SubmitField("Добавить документ")


class DocumentsEditForm(FlaskForm):

    name = TextAreaField("Название документа", validators=[DataRequired()])
    submit = SubmitField("Сохранить изменения")


class DeleteForm(FlaskForm):
    """Форма удаления данных."""

    submit = SubmitField("Удалить")
