from flask_wtf import FlaskForm
from wtforms import SelectField, FileField, SubmitField
from wtforms.validators import DataRequired


class ChooseDepartment(FlaskForm):
    department = SelectField(
        "Кафедра:",
        coerce=int,
        validators=[DataRequired()]
    )
    dept_choose = SubmitField("Выбор")


class ChoosePlan(FlaskForm):
    edu_spec = SelectField(
        "Специальность:",
        coerce=str,
        validators=[DataRequired()]
    )
    spec_choose = SubmitField("Выбор")
    edu_plan = SelectField(
        "План:",
        coerce=str,
        validators=[DataRequired()]
    )
    plan_choose = SubmitField("Выбор")


class FileForm(FlaskForm):
    file = FileField('file')
    # upload = SubmitField("Проверка файла")
