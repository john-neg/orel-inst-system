from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length

from config import FlaskConfig
from app.db.models import User


class LoginForm(FlaskForm):
    """Класс аутентификации пользователей."""

    class Meta(FlaskForm.Meta):
        locales = ['ru_RU', 'ru']

        def get_translations(self, form):
            return super(FlaskForm.Meta, self).get_translations(form)

    username = StringField("Логин", validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить")
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    """Класс регистрации пользователей."""

    class Meta(FlaskForm.Meta):
        locales = ['ru_RU', 'ru']

        def get_translations(self, form):
            return super(FlaskForm.Meta, self).get_translations(form)

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Имя уже существует')

    username = StringField(
        'Логин', validators=[DataRequired(), Length(min=4, max=20)]
    )
    password = PasswordField(
        'Пароль', validators=[DataRequired(), Length(min=6, max=20)]
    )
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    role = SelectField("Права доступа", coerce=int, choices=[
            (FlaskConfig.ROLE_ADMIN, "Администратор"),
            (FlaskConfig.ROLE_USER, "Пользователь"),
            (FlaskConfig.ROLE_METOD, "Методист"),
            (FlaskConfig.ROLE_BIBL, "Библиотека"),
        ], default=FlaskConfig.ROLE_METOD, validators=[DataRequired()])
    submit = SubmitField('Зарегистрировать')
