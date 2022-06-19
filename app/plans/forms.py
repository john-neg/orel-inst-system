from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField


class PlanForm(FlaskForm):
    data_delete = SubmitField("Полная очистка")
    file = FileField('Выберите файл Excel для загрузки')
    file_check = SubmitField("Проверка данных в файле")
    file_load = SubmitField("Загрузить данные")


class CompLoadForm(PlanForm):
    data_template = SubmitField("Шаблон")


class MatrixForm(PlanForm):
    data_template = SubmitField("Образец файла")
    make_matrix = SubmitField("Сформировать матрицу")


class IndicatorsFile(FlaskForm):
    file = FileField('Выберите файл Excel с индикаторами (из Google форм)')
    file_check = SubmitField("Проверка данных в файле")
    generate_report = SubmitField("Скачать список индикаторов в формате docx")


