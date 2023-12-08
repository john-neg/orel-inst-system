import os

from flask_wtf import FlaskForm
from wtforms import (
    SubmitField,
    SelectField,
    StringField,
    TextAreaField,
    FloatField,
    BooleanField,
    IntegerField,
    FieldList,
    FormField,
)
from wtforms.validators import DataRequired, NumberRange

from config import BASEDIR
from ...db.database import db

FILE_DIR = os.path.join(BASEDIR, "app", "tools", "data_payment")
DEFAULT_OPTIONS = [(0, "нет")]


def create_payment_form(
    rate_items: list[db.Model],
    addon_items: list[db.Model],
    single_items: list[db.Model],
    pension_duty_items: list[db.Model],
    **kwargs,
):
    class PaymentForm(FlaskForm):
        """Класс формы расчета денежного содержания."""

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
    if pension_duty_items:
        label = "pension_duty_years"
        field = SelectField(
            label="Выслуга (полных) лет для расчета пенсии",
            coerce=int,
            choices=[
                (duty.id, duty.name)
                for duty in sorted(
                    pension_duty_items,
                    key=lambda duty: int(duty.value),
                )
            ],
            validators=[DataRequired()],
        )
        setattr(PaymentForm, label, field)

    return PaymentForm(**kwargs)


class DocumentsForm(FlaskForm):
    """Класс формы нормативных документов."""

    name = TextAreaField("Название документа", validators=[DataRequired()])
    submit = SubmitField("Сохранить")


def create_increase_form(
    rate_items: list[db.Model],
    document_items: list[db.Model],
    **kwargs,
):
    class IncreaseForm(FlaskForm):
        """Класс формы сведений об индексациях."""

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
    """Класс формы базовых окладов."""

    name = StringField("Название", validators=[DataRequired()])
    payment_name = StringField("Название выплаты", validators=[DataRequired()])
    salary = BooleanField("Зарплата")
    pension = BooleanField("Пенсия")
    submit = SubmitField("Сохранить")


def create_addons_form(
    rate_items: list[db.Model],
    **kwargs,
):
    class AddonsForm(FlaskForm):
        """Класс формы надбавок с множественным значением."""

        name = StringField("Название", validators=[DataRequired()])
        payment_name = StringField("Название надбавки", validators=[DataRequired()])
        salary = BooleanField("Зарплата")
        pension = BooleanField("Пенсия")
        submit = SubmitField("Сохранить")

    # Добавляем переключатели для окладов
    for item in rate_items:
        label = item.slug
        field = SubmitField(label=item.payment_name)
        setattr(AddonsForm, label, field)

    return AddonsForm(**kwargs)


def create_single_addons_form(
    rate_items: list[db.Model],
    document_items: list[db.Model],
    **kwargs,
):
    class SingleAddonsForm(FlaskForm):
        """Класс формы фиксированных надбавок."""

        name = StringField("Название", validators=[DataRequired()])
        value = FloatField(
            "Значение",
            validators=[
                DataRequired(
                    message="Введите число (Например: для надбавки 5% число - 0.05)"
                )
            ],
        )
        payment_name = StringField("Название надбавки", validators=[DataRequired()])
        description = TextAreaField("Описание (пункт документа)")
        document_id = SelectField(
            "Нормативный документ",
            validators=[DataRequired()],
            choices=[(item.id, item.name) for item in document_items],
        )
        salary = BooleanField("Зарплата")
        pension = BooleanField("Пенсия")
        default_state = BooleanField("Использовать по умолчанию")
        submit = SubmitField("Сохранить")

    # Добавляем переключатели для окладов
    for item in rate_items:
        label = item.slug
        field = SubmitField(label=item.payment_name)
        setattr(SingleAddonsForm, label, field)

    return SingleAddonsForm(**kwargs)


def create_rate_values_form(
    rate_items: list[db.Model],
    document_items: list[db.Model],
    **kwargs,
):
    class RatesValuesForm(FlaskForm):
        """Класс формы значений базовых окладов."""

        name = StringField("Название", validators=[DataRequired()])
        value = IntegerField(
            "Значение",
            validators=[
                NumberRange(min=1, message="Введите целое положительное число")
            ],
        )
        description = TextAreaField("Описание (пункт документа)")
        rate_id = SelectField(
            "Базовый оклад",
            validators=[DataRequired()],
            choices=[(item.id, item.name) for item in rate_items],
        )
        document_id = SelectField(
            "Нормативный документ",
            validators=[DataRequired()],
            choices=[(item.id, item.name) for item in document_items],
        )
        submit = SubmitField("Сохранить")

    return RatesValuesForm(**kwargs)


def create_addons_values_form(
    addons_items: list[db.Model],
    document_items: list[db.Model],
    **kwargs,
):
    class AddonsValuesForm(FlaskForm):
        """Класс формы значений надбавок с множественным выбором."""

        name = StringField("Название", validators=[DataRequired()])
        value = FloatField(
            "Значение",
            validators=[
                DataRequired(
                    message="Введите число (Например: для надбавки 5% число - 0.05)"
                )
            ],
        )
        description = TextAreaField("Описание (пункт документа)")
        addon_id = SelectField(
            "Надбавка",
            validators=[DataRequired()],
            choices=[(item.id, item.name) for item in addons_items],
        )
        document_id = SelectField(
            "Нормативный документ",
            validators=[DataRequired()],
            choices=[(item.id, item.name) for item in document_items],
        )
        submit = SubmitField("Сохранить")

    return AddonsValuesForm(**kwargs)


def create_pension_duty_form(
    document_items: list[db.Model],
    **kwargs,
):
    class PensionDutyForm(FlaskForm):
        """Класс формы пенсионных коэффициентов."""

        name = StringField("Название", validators=[DataRequired()])
        value = FloatField(
            "Значение",
            validators=[
                DataRequired(
                    message=(
                        "Введите число (Например: для коэффициента 50% число - 0.5)",
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

    return PensionDutyForm(**kwargs)


def create_global_coefficient_form(
    document_items: list[db.Model],
    **kwargs,
):
    class GlobalCoefficientForm(FlaskForm):
        """Класс формы глобальных коэффициентов."""

        name = StringField("Название", validators=[DataRequired()])
        value = FloatField(
            "Значение",
            validators=[
                DataRequired(
                    message=(
                        "Введите число (Например: для коэффициента 5% число - 0.05)",
                    )
                )
            ],
        )
        payment_name = StringField("Название выплаты", validators=[DataRequired()])
        description = TextAreaField("Описание (пункт документа)")
        salary = BooleanField("Зарплата")
        pension = BooleanField("Пенсия")
        FieldList(FormField)
        document_id = SelectField(
            "Документ",
            validators=[DataRequired()],
            choices=[(item.id, item.name) for item in document_items],
        )
        submit = SubmitField("Сохранить")

    return GlobalCoefficientForm(**kwargs)


class DeleteForm(FlaskForm):
    """Класс формы удаления данных."""

    submit = SubmitField("Удалить")
