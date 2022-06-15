from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
    SubmitField,
    IntegerField,
    TextAreaField,
    BooleanField,
)
from wtforms.validators import DataRequired, Length, NumberRange

from app.common.forms import ChoosePlan
from config import ApeksConfig as Apeks


class FieldsForm(FlaskForm):
    wp_fields = SelectField(
        "Поле рабочей программы:",
        coerce=str,
        choices=[
            ("name", "Название программы"),
            ("department_data", "Дата и протокол заседания кафедры"),
            ("reviewers_ext", "Рецензенты"),
            ("purposes", "Цели дисциплины"),
            ("tasks", "Задачи дисциплины"),
            ("place_in_structure", "Место в структуре ООП"),
            ("knowledge", "Знать"),
            ("skills", "Уметь"),
            ("abilities", "Владеть"),
            ("ownerships", "Навыки"),
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


class WorkProgramDatesUpdate(ChoosePlan):
    # TODO добавить валидаторы для дат
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


class TitlePagesGenerator(FlaskForm):
    organization_name = TextAreaField(
        "Название образовательной организации",
        validators=[DataRequired()],
    )
    wp_approval_info = TextAreaField(
        "Информация об утверждении",
        default=(
            "УТВЕРЖДАЮ\n"
            + "Начальник Орловского\n"
            + "юридического института МВД России\n"
            + "имени В.В. Лукьянова"
        ),
        validators=[DataRequired()],
    )
    chief_rank = StringField(
        "Звание руководителя",
        validators=[DataRequired()],
    )
    chief_name = StringField(
        "Имя руководителя",
        validators=[DataRequired()],
    )
    wp_approval_day = StringField(
        "День",
        validators=[DataRequired()],
    )
    wp_approval_month = SelectField(
        "Месяц",
        coerce=int,
        choices=[
            (
                k,
                v.replace("й", "я")
                .replace("ь", "я")
                .replace("рт", "рта")
                .replace("ст", "ста"),
            )
            for k, v in Apeks.MONTH_DICT.items()
        ],
        validators=[DataRequired()],
    )
    wp_approval_year = StringField(
        "Год",
        validators=[DataRequired()],
    )
    wp_type_name = StringField(
        "Тип рабочей программы",
        default="Рабочая программа учебной дисциплины",
        validators=[DataRequired()],
    )
    wp_speciality_type = SelectField(
        "Тип - специальность / направление подготовки:",
        coerce=str,
        choices=[
            ("bak", "по направлению подготовки"),
            ("spec", "по специальности"),
        ],
        validators=[DataRequired()],
    )
    wp_speciality = StringField(
        "Название специальности:",
        validators=[DataRequired()],
    )
    wp_specialization_type = SelectField(
        "Тип - профиль / специализация:",
        coerce=str,
        choices=[
            ("bak", "профиль образовательной программы"),
            ("spec", "специализация"),
        ],
        validators=[DataRequired()],
    )
    wp_specialization = StringField(
        "Специализация:",
        validators=[DataRequired()],
    )
    wp_foreigners = BooleanField("Иностранные слушатели:")
    wp_education_form = StringField(
        "Форма обучения:",
        validators=[DataRequired()],
    )
    wp_year = StringField(
        "Год набора:",
        validators=[DataRequired()],
    )
    wp_qualification = StringField(
        "Квалификация:",
        validators=[DataRequired()],
    )
    switch_qualification = BooleanField(
        "Квалификация:",
        validators=[],
    )
    wp_narrow_specialization = StringField(
        "Узкая специализация:",
        validators=[],
    )
    switch_narrow_spec = BooleanField(
        "Узкая специализация:",
        validators=[],
    )
    switch_foreign = BooleanField(
        "Иностранные слушатели",
        validators=[],
    )
    title_pages = SubmitField("Сформировать титульные листы")
