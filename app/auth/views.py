import logging

from flask import render_template, redirect, url_for, flash, request
from flask_login import logout_user, login_user, current_user, login_required
from ldap3.core.exceptions import LDAPSocketOpenError

from config import FlaskConfig
from . import bp
from ..auth.forms import UserRegisterForm, UserLoginForm, UserDeleteForm, UserEditForm
from ..common.extensions import login_manager
from ..common.func.ldap_data import get_user_data
from ..services.users_roles_service import get_users_roles_service
from ..services.users_service import get_users_service


@login_manager.user_loader
def load_user(user_id):
    users_service = get_users_service()
    return users_service.get(id=user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("auth.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    users_service = get_users_service()
    users_roles_service = get_users_roles_service()
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = UserLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = users_service.get(username=username)

        if FlaskConfig.LDAP_AUTH:
            try:
                name, ldap_groups = get_user_data(username, password)
                if not user and ldap_groups:
                    user_role = users_roles_service.get(slug=FlaskConfig.ROLE_USER)
                    user = users_service.create_user(
                        username=username,
                        password=password,
                        role_id=user_role.id,
                    )
                    message = f"Создан новый пользователь: {username}"
                    flash(message, category="info")
                    logging.info(message)
                elif user and ldap_groups:
                    if not users_service.check_password(user.password_hash, password):
                        user = users_service.update_user(user.id, password=password)
                        message = f"Обновлен пароль пользователя: {username}"
                        flash(message, category="info")
                        logging.info(message)
            except LDAPSocketOpenError:
                message = "Нет связи с сервером авторизации"
                flash(message, category="warning")
                logging.info(message)

        if user is None or not users_service.check_password(
            user.password_hash, password
        ):
            error = "Неверный логин или пароль"
            return render_template(
                "auth/login.html",
                title="Авторизация",
                form=form,
                error=error,
            )
        login_user(
            user,
            remember=form.remember_me,
            duration=FlaskConfig.USER_LOGIN_DURATION,
        )
        logging.info(f"Успешная авторизация - {user}")
        return redirect(url_for("main.index"))
    return render_template(
        "auth/login.html",
        title="Авторизация",
        form=form,
    )


@bp.route("/users", methods=["GET", "POST"])
@login_required
def users():
    users_service = get_users_service()
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for("main.index"))
    paginated_data = users_service.paginated()
    return render_template(
        "auth/users.html",
        title="Пользователи",
        paginated_data=paginated_data,
    )


@bp.route("/register", methods=["GET", "POST"])
@login_required
def register():
    users_service = get_users_service()
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for("main.index"))
    form = UserRegisterForm()
    if form.validate_on_submit():
        new_user = users_service.create_user(
            username=form.username.data,
            password=form.password.data,
            role_id=form.role.data.id,
        )
        message = (
            "Зарегистрирован новый пользователь - "
            f"{new_user} (Права - {form.role.data})"
        )
        logging.info(message)
        flash(message, category="success")
        return redirect(url_for("auth.users"))
    return render_template(
        "auth/register.html",
        title="Регистрация нового пользователя",
        form=form,
    )


@bp.route("/edit/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit(user_id):
    users_service = get_users_service()
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for("main.index"))
    user = users_service.get(id=user_id)
    if not user:
        flash(f"Пользователь не найден!", category="danger")
        return redirect(url_for("auth.users"))
    form = UserEditForm()
    form.username.data = user.username
    form.role.data = user.role
    if form.validate_on_submit():
        users_service.update_user(
            user_id,
            username=request.form.get("username"),
            password=request.form.get("password"),
            role_id=request.form.get("role"),
        )
        logging.info(
            f"'{current_user}' отредактировал данные пользователя - {user.username}"
        )
        flash(
            f"Информация о пользователе {user.username} успешно изменена",
            category="success",
        )
        return redirect(url_for("auth.users"))
    return render_template(
        "auth/edit.html",
        title="Редактирование пользователя",
        form=form,
    )


@bp.route("/delete/<int:user_id>", methods=["GET", "POST"])
@login_required
def delete(user_id):
    users_service = get_users_service()
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for("main.index"))
    form = UserDeleteForm()
    user = users_service.get(id=user_id)
    if not user:
        flash(f"Пользователь не найден!", category="danger")
        return redirect(url_for("auth.users"))
    if current_user.id == user_id:
        flash(f"Нельзя удалить самого себя!", category="danger")
        return redirect(url_for("auth.users"))
    if form.validate_on_submit():
        users_service.delete(user_id)
        logging.info(f"'{current_user}' удалил пользователя - {user.username}")
        flash(f"Пользователь {user.username} - удален.", category="success")
        return redirect(url_for("auth.users"))
    return render_template(
        "auth/delete.html",
        title="Удаление пользователя",
        form=form,
        username=user.username,
    )


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
