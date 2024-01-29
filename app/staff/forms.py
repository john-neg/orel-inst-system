import datetime

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.fields.datetime import DateField
from wtforms.validators import DataRequired, Length

from ..core.db.database import db


class StaffForm(FlaskForm):
    document_date = DateField(
        "Дата документа",
        default=datetime.date.today()
    )
    make_report = SubmitField("Сформировать отчет")


class StableStaffForm(FlaskForm):
    """Форма для заполнения данных """

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
