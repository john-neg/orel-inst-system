from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.fields.form import FormField
from wtforms.fields.list import FieldList
from wtforms.fields.simple import StringField, HiddenField
from wtforms.validators import DataRequired

from config import ApeksConfig as Apeks
from ..db.database import db

# FILE_DIR = os.path.join(BASEDIR, "app", "tools", "data_payment")
DEFAULT_OPTIONS = ("0", "В строю")


class StableStaffForm(FlaskForm):
    finish_edit = SubmitField("Завершить редактирование")
    enable_edit = SubmitField("Разрешить редактирование")
    make_report = SubmitField("Сформировать отчет")


# class StaffPersonForm(FlaskForm):
#     staff_id = HiddenField("id", validators=[DataRequired()])
#     staff_name = HiddenField("Фамилия И.О.")
#     position = HiddenField("Должность")
#     current_status = SelectField(
#         "Местонахождение",
#         coerce=str,
#         validators=[DataRequired()],
#     )
#
#
# class DepartmentEditForm(FlaskForm):
#     staff_list = FieldList(FormField(StaffPersonForm))
    # submit = SubmitField("Сохранить")

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
            label='Местонахождение',
            coerce=str,
            choices=[("0", "В строю"), *[(item.slug, item.name) for item in busy_types]],
            validators=[DataRequired()],
        )
        setattr(StaffEditForm, label, field)

    return StaffEditForm(**kwargs)

# class StaffEditForm(FlaskForm):
#     # finish_edit = SubmitField("Завершить редактирование")
#     # enable_edit = SubmitField("Разрешить редактирование")
#     submit = SubmitField("Сохранить")
