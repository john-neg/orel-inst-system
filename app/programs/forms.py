from datetime import date
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange
from app.main.forms import ChoosePlan


class FieldsForm(FlaskForm):
    wp_fields = SelectField(
        "Поле рабочей программы:",
        coerce=str,
        choices=[
            ("name", "Название программы"),
            ("date_department", "Дата и протокол заседания кафедры"),
            ("reviewers_ext", "Рецензенты"),
            ("purposes", "Цели дисциплины"),
            ("tasks", "Задачи дисциплины"),
            ("place_in_structure", "Место в структуре ООП"),
            (
                "no_next_disc",
                "Пояснение к таблице с последующими дисциплинами (информация об отсутствии)",
            ),
            ("templan_info", "Примечание к тематическому плану"),
            ("self_provision", "Обеспечение самостоятельной работы"),
            (
                "test_criteria",
                "Критерии оценки для сдачи промежуточной аттестации в форме тестирования",
            ),
            ("authorprint", "Автор(ы) рабочей программы (для печати)"),
            ("course_works", "Тематика курсовых работ"),
            ("practice", "Практикум"),
            ("control_works", "Тематика контрольных работ"),
            (
                "exam_form_desc",
                "Примерные оц. средства для пров. пром. атт. обучающихся по дисциплине",
            ),
            ("task_works", "Задачи учебные"),
            ("tests", "Тесты"),
            ("regulations", "Нормативные акты"),
            ("library_main", "Основная литература"),
            ("library_add", "Дополнительная литература"),
            ("library_np", "Научная продукция"),
            ("internet", "Ресурсы информационно-телекоммуникационной сети Интернет"),
            ("software", "Программное обеспечение"),
            ("ref_system", "Базы данных, информационно-справочные и поисковые системы"),
            ("materials_base", "Описание материально-технической базы"),
        ],
        validators=[DataRequired()],
    )
    fields_data = SubmitField("Выбрать")


class DepartmentWPCheck(FieldsForm):
    edu_spec = SelectField("Специальность:", coerce=str, validators=[DataRequired()])
    department = SelectField("Кафедра:", coerce=str, validators=[DataRequired()])
    year = SelectField(
        "Год",
        coerce=str,
        choices=[
            date.today().year - 5,
            date.today().year - 4,
            date.today().year - 3,
            date.today().year - 2,
            date.today().year - 1,
            date.today().year,
            date.today().year + 1,
        ],
        default=date.today().year,
        validators=[DataRequired()],
    )


class WorkProgramDatesUpdate(ChoosePlan):  # добавить валидаторы для дат
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


class WorkProgramFieldUpdate(FieldsForm):
    wp_field_edit = TextAreaField("Данные поля программы")
    field_update = SubmitField("Обновить")
