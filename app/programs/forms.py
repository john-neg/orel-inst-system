from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange


class WorkProgramDatesUpdate(FlaskForm):  # добавить валидаторы для дат
    edu_spec = SelectField("Специальность:", coerce=str, validators=[DataRequired()])
    edu_plan = SelectField(
        "План:", coerce=str, validators=[DataRequired()], validate_choice=False
    )
    date_methodical = StringField(
        "Дата методического совета",
        validators=[Length(min=10, max=10, message="Формат даты - ГГГГ-ММ-ДД")],
    )
    document_methodical = IntegerField(
        "Номер документа методического совета",
        validators=[NumberRange(max=99, message="Номер протокола от 1 до 99")],
    )
    date_academic = StringField(
        "Дата Ученого совета",
        validators=[Length(min=10, max=10, message="Формат даты - ГГГГ-ММ-ДД")],
    )
    document_academic = IntegerField(
        "Номер документа Ученого совета",
        validators=[NumberRange(max=99, message="Номер протокола (от 1 до 99)")],
    )
    date_approval = StringField(
        "Дата утверждения",
        validators=[Length(min=10, max=10, message="Формат даты - ГГГГ-ММ-ДД")],
    )
    wp_dates_update = SubmitField("Обновить данные")
