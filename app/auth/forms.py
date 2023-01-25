from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Length
from wtforms_sqlalchemy.fields import QuerySelectField

from app.db.models import User, UserRoles


class UserLoginForm(FlaskForm):
    """Форма аутентификации пользователей."""

    class Meta(FlaskForm.Meta):
        locales = ["ru_RU", "ru"]

        def get_translations(self, form):
            return super(FlaskForm.Meta, self).get_translations(form)

    username = StringField("Логин", validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить")
    submit = SubmitField("Войти")


class UserRegisterForm(FlaskForm):
    """Форма регистрации пользователя."""

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Имя уже существует")

    username = StringField("Логин", validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField(
        "Пароль", validators=[DataRequired(), Length(min=6, max=20)]
    )
    password2 = PasswordField(
        "Повторите пароль", validators=[DataRequired(), EqualTo("password")]
    )
    role = QuerySelectField(
        "Права доступа",
        validators=[DataRequired()],
        query_factory=UserRoles.available_roles,
        allow_blank=False,
    )
    submit = SubmitField("Зарегистрировать")


class UserEditForm(FlaskForm):
    """Форма редактирования пользователя."""

    username = StringField("Логин", validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField("Новый пароль")
    password2 = PasswordField("Повторите пароль", validators=[EqualTo("password")])
    role = QuerySelectField(
        "Права доступа",
        validators=[DataRequired()],
        query_factory=UserRoles.available_roles,
        allow_blank=False,
    )
    submit = SubmitField("Сохранить")


class UserDeleteForm(FlaskForm):
    """Форма удаления пользователя."""

    submit = SubmitField("Удалить")
