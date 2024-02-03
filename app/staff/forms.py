import datetime

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.fields.datetime import DateField
from wtforms.fields.simple import StringField, BooleanField
from wtforms.validators import DataRequired, Regexp

from ..core.db.database import db


class StaffForm(FlaskForm):
    """Форма для просмотра информации по строевой записке."""

    document_date = DateField("Дата документа", default=datetime.date.today())
    make_report = SubmitField("Выбрать")


class StaffReportForm(FlaskForm):
    """Форма для отчетов по наличию личного состава."""

    document_start_date = DateField(
        "Дата начала",
    )
    document_end_date = DateField("Дата окончания", default=datetime.date.today())


class StableStaffForm(FlaskForm):
    """Форма для заполнения данных"""

    finish_edit = SubmitField("Завершить редактирование")
    enable_edit = SubmitField("Разрешить редактирование")
    make_report = SubmitField("Сформировать отчет")


def create_staff_edit_form(
    staff_data: list[dict[str, str]],
    busy_types: list[db.Model],
    **kwargs,
):
    """Конструктор формы StaffEditForm."""

    class StaffEditForm(FlaskForm):
        """Класс формы заполнения личного состава подразделения."""

        submit = SubmitField("Сохранить")

    # Добавляем людей
    for staff in staff_data:
        label = f"staff_id_{staff.get('staff_id')}"
        field = SelectField(
            label="Местонахождение",
            coerce=str,
            choices=[
                ("0", "В строю"),
                *[(item.slug, item.name) for item in busy_types],
            ],
            validators=[DataRequired()],
        )
        setattr(StaffEditForm, label, field)

    return StaffEditForm(**kwargs)


class StaffStableBusyTypesForm(FlaskForm):
    """Класс формы причин отсутствия постоянного состава."""

    slug = StringField(
        "Код",
        validators=[
            DataRequired(),
            Regexp(
                r"^[\w_-]+",
                message="Допускаются только маленькие буквы "
                "латинского алфавита, цифры и подчеркивания",
            ),
        ],
    )
    name = StringField("Название", validators=[DataRequired()])
    is_active = BooleanField("Действует")
    submit = SubmitField("Сохранить")
