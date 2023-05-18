import os

from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField, TextAreaField, FloatField, \
    BooleanField
from wtforms.validators import DataRequired

from app import db
from config import BASEDIR

FILE_DIR = os.path.join(BASEDIR, "app", "tools", "data_payment")
DEFAULT_OPTIONS = [(0, "нет")]


def create_payment_form(
    rate_items: list[db.Model],
    addon_items: list[db.Model],
    single_items: list[db.Model],
    duty_coeff_items: list[db.Model],
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
                duty_coeff_items,
                key=lambda duty: int(duty.value),
            )
        ],
        validators=[DataRequired()],
    )
    setattr(PaymentForm, label, field)

    return PaymentForm(**kwargs)


class DocumentsForm(FlaskForm):
    """Класс формы для нормативных документов."""

    name = TextAreaField("Название документа", validators=[DataRequired()])
    submit = SubmitField("Сохранить")


def create_increase_form(
    rate_items: list[db.Model],
    document_items: list[db.Model],
    **kwargs,
):
    class IncreaseForm(FlaskForm):
        """Класс формы для сведений об индексациях."""

        name = StringField("Название", validators=[DataRequired()])
        value = FloatField(
            "Значение",
            validators=[
                DataRequired(
                    message=(
                        "Введите число (Например: ",
                        "для индексации на +5% число - 1.05",
                    )
                )
            ],
        )
        document_id = SelectField(
            "Документ",
            validators=[DataRequired()],
            choices=[(item.id, item.name) for item in document_items],
        )
        submit = SubmitField("Сохранить")

    # Добавляем переключатели для окладов
    for item in rate_items:
        label = item.slug
        field = SubmitField(label=item.payment_name)
        setattr(IncreaseForm, label, field)

    return IncreaseForm(**kwargs)


class RatesForm(FlaskForm):
    """Класс формы для базовых окладов."""

    name = StringField("Название", validators=[DataRequired()])
    payment_name = StringField("Название выплаты", validators=[DataRequired()])
    salary = BooleanField("Зарплата")
    pension = BooleanField("Пенсия")
    submit = SubmitField("Сохранить")




class DeleteForm(FlaskForm):
    """Форма удаления данных."""

    submit = SubmitField("Удалить")
