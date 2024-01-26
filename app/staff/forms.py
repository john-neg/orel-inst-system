from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired

from ..core.db.database import db


class StableStaffForm(FlaskForm):
    finish_edit = SubmitField("Завершить редактирование")
    enable_edit = SubmitField("Разрешить редактирование")
    make_report = SubmitField("Сформировать отчет")


def create_staff_edit_form(
    staff_data: list[dict[str, str]],
    busy_types: list[db.Model],
    **kwargs,
):
    class StaffEditForm(FlaskForm):
        """Класс формы наличия личного состава."""

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
