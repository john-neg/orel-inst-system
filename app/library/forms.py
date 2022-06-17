from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField


class LibraryForm(FlaskForm):
    library_load_temp = SubmitField("Шаблон")
    library_plan_content = SubmitField()
    file = FileField('Выберите файл Excel для загрузки')
    library_check = SubmitField("Проверка данных в файле")
    library_update = SubmitField("Загрузить данные")
