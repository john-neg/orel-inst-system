from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms_sqlalchemy.fields import QuerySelectField

from ..core.services.db_users_service import get_users_roles_service

users_roles_service = get_users_roles_service()


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

    username = StringField("Логин", validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField(
        "Пароль", validators=[DataRequired(), Length(min=6, max=20)]
    )
    password2 = PasswordField(
        "Повторите пароль", validators=[DataRequired(), EqualTo("password")]
    )
    role = QuerySelectField(
        "Роль (группа)",
        validators=[DataRequired()],
        query_factory=users_roles_service.list,
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
        query_factory=users_roles_service.list,
        allow_blank=False,
    )
    submit = SubmitField("Сохранить")


def create_roles_form(permissions_items, **kwargs):
    class UsersRolesForm(FlaskForm):
        """Класс формы редактирования ролей пользователей."""

        slug = StringField("Код", validators=[DataRequired()])
        name = StringField("Название", validators=[DataRequired()])
        submit = SubmitField("Сохранить")

    # Добавляем переключатели для прав доступа
    for obj in sorted(permissions_items):
        label = f"permission_{obj.slug}"
        field = SubmitField(label=obj.name)
        setattr(UsersRolesForm, label, field)

    return UsersRolesForm(**kwargs)
