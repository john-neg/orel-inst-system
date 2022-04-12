from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo

from config import FlaskConfig as Config
from app.auth.models import User


class LoginForm(FlaskForm):
    username = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить")
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    role = SelectField("Права доступа", coerce=int, choices=[
            (Config.ROLE_ADMIN, "Администратор"),
            (Config.ROLE_USER, "Пользователь"),
            (Config.ROLE_METOD, "Методист"),
            (Config.ROLE_BIBL, "Библиотека"),
        ], default=Config.ROLE_METOD, validators=[DataRequired()])
    submit = SubmitField('Зарегистрировать')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Имя уже существует')
