import logging

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from ldap3.core.exceptions import LDAPSessionTerminatedByServerError, LDAPSocketOpenError, LDAPSocketReceiveError

from config import FlaskConfig, PermissionsConfig, ApeksConfig
from . import bp
from .forms import UserEditForm, UserLoginForm, UserRegisterForm, create_roles_form
from .func import permission_required, has_permission
from .ldap_data import get_user_data
from ..core.extensions import login_manager
from ..core.forms import ObjectDeleteForm
from ..core.services.db_users_services import (
    get_users_permissions_service,
    get_users_roles_service,
    get_users_service,
)


@login_manager.user_loader
def load_user(user_id):
    users_service = get_users_service()
    return users_service.get(id=user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("auth.login", next=request.path))


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
        user = users_service.get(username=username)  # проверяем есть ли пользователь в локальной базе
        if FlaskConfig.LDAP_AUTH:
            try:
                name, ldap_groups = get_user_data(username, password)  # пытаемся получить данные пользователя из ldap
                if not user and ldap_groups:  # если польз. нет в локальной базе, но есть в ldap создаем в базе нового
                    user_role = users_roles_service.get(
                        slug=PermissionsConfig.ROLE_USER
                    )
                    user = users_service.create_user(
                        username=username,
                        password=password,
                        role_id=user_role.id,
                    )
                    message = f"Создан новый пользователь: {username}"
                    flash(message, category="info")
                    logging.info(message)
                elif user and ldap_groups:  # если пользователь есть и в базе и в ldap
                    if not users_service.check_password(user.password_hash, password):
                        # если пароль в ldap и в базе не совпадают обновляем пароль в базе
                        user = users_service.update_user(user.id, password=password)
                        message = f"Обновлен пароль пользователя: {username}"
                        flash(message, category="info")
                        logging.info(message)
            except LDAPSessionTerminatedByServerError:
                message = "Ошибка связи с сервером авторизации"
                flash(message, category="warning")
                logging.info(message)
            except (LDAPSocketOpenError, LDAPSocketReceiveError):
                message = "Нет связи с сервером авторизации"
                flash(message, category="warning")
                logging.info(message)

        if user is None or not users_service.check_password(  # если пользователь не найден или пароль не верный
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
        return redirect(request.args.get("next") or url_for("main.index"))
    return render_template(
        "auth/login.html",
        title="Авторизация",
        form=form,
    )


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/users", methods=["GET", "POST"])
@permission_required(PermissionsConfig.USERS_EDIT_PERMISSION)
@login_required
def users():
    users_service = get_users_service()
    paginated_data = users_service.paginated()
    return render_template(
        "auth/users.html",
        title="Пользователи",
        paginated_data=paginated_data,
    )


@bp.route("/users_register", methods=["GET", "POST"])
@permission_required(PermissionsConfig.USERS_EDIT_PERMISSION)
@login_required
def users_register():
    users_service = get_users_service()
    form = UserRegisterForm()
    if request.method == "POST" and form.validate_on_submit():
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
        "auth/users_register.html",
        title="Регистрация нового пользователя",
        form=form,
    )


@bp.route("/users_edit/<int:user_id>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.USERS_EDIT_PERMISSION)
@login_required
def users_edit(user_id):
    users_service = get_users_service()
    user = users_service.get(id=user_id)
    if not user:
        flash(f"Пользователь не найден!", category="danger")
        return redirect(url_for("auth.users"))
    form = UserEditForm()
    form.username.data = user.username
    form.role.data = user.role
    if request.method == "POST" and form.validate_on_submit():
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
        "auth/users_edit.html",
        title="Редактирование пользователя",
        form=form,
    )


@bp.route("/users_delete/<int:user_id>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.USERS_EDIT_PERMISSION)
@login_required
def users_delete(user_id):
    users_service = get_users_service()
    form = ObjectDeleteForm()
    user = users_service.get(id=user_id)
    if not user:
        flash(f"Пользователь не найден!", category="danger")
        return redirect(url_for("auth.users"))
    if current_user.id == user_id:
        flash(f"Нельзя удалить самого себя!", category="danger")
        return redirect(url_for("auth.users"))
    if request.method == "POST" and form.validate_on_submit():
        users_service.delete(user_id)
        logging.info(f"'{current_user}' удалил пользователя - {user.username}")
        flash(f"Пользователь {user.username} - удален.", category="success")
        return redirect(url_for("auth.users"))
    return render_template(
        "auth/users_delete.html",
        title="Удаление пользователя",
        form=form,
        username=user.username,
    )


@bp.route("/roles", methods=["GET", "POST"])
@permission_required(PermissionsConfig.USERS_EDIT_PERMISSION)
@login_required
def roles():
    roles_service = get_users_roles_service()
    paginated_data = roles_service.paginated()
    return render_template(
        "auth/roles.html",
        title="Роли (группы) пользователей",
        paginated_data=paginated_data,
    )


@bp.route("/roles_add", methods=["GET", "POST"])
@permission_required(PermissionsConfig.USERS_EDIT_PERMISSION)
@login_required
def roles_add():
    roles_service = get_users_roles_service()
    users_permissions_service = get_users_permissions_service()
    permissions_items = users_permissions_service.list()
    form = create_roles_form(permissions_items)
    if request.method == "POST" and form.validate_on_submit():
        roles_service.create(
            slug=request.form.get("slug"),
            name=request.form.get("name"),
            permissions=[
                obj
                for obj in permissions_items
                if request.form.get(f"permission_{obj.slug}")
            ],
        )
        logging.info(f"'{current_user}' добавил роль - {request.form.get('name')}")
        flash(
            f"Роль {request.form.get('name')} успешно добавлена",
            category="success",
        )
        return redirect(url_for("auth.roles"))
    return render_template(
        "auth/roles_edit.html",
        title="Добавить",
        form=form,
    )


@bp.route("/roles_edit/<int:id_>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.USERS_EDIT_PERMISSION)
@login_required
def roles_edit(id_):
    roles_service = get_users_roles_service()
    users_permissions_service = get_users_permissions_service()
    permissions_items = users_permissions_service.list()
    role = roles_service.get(id=id_)
    if not role:
        flash(f"Роль не найдена!", category="danger")
        return redirect(url_for("auth.roles"))
    form = create_roles_form(permissions_items)
    form.slug.data = role.slug
    form.name.data = role.name
    for obj in role.permissions:
        form.__getattribute__(f"permission_{obj.slug}").data = True
    if request.method == "POST" and form.validate_on_submit():
        if role.slug in PermissionsConfig.BASE_ROLES:
            flash("Базовая роль не может быть изменена", category="danger")
            return redirect(url_for("auth.roles"))
        roles_service.update(
            id_,
            slug=request.form.get("slug"),
            name=request.form.get("name"),
            permissions=[
                obj
                for obj in permissions_items
                if request.form.get(f"permission_{obj.slug}")
            ],
        )
        logging.info(
            f"'{current_user}' отредактировал роль - {request.form.get('name')}"
        )
        flash(
            f"Роль {request.form.get('name')} успешно изменена",
            category="success",
        )
        return redirect(url_for("auth.roles"))
    return render_template(
        "auth/roles_edit.html",
        title="Изменить",
        form=form,
    )


@bp.route("/roles_delete/<int:id_>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.USERS_EDIT_PERMISSION)
@login_required
def roles_delete(id_):
    roles_service = get_users_roles_service()
    form = ObjectDeleteForm()
    role = roles_service.get(id=id_)
    if not role:
        flash(f"Роль не найдена!", category="danger")
        return redirect(url_for("auth.roles"))
    if role.slug in PermissionsConfig.BASE_ROLES:
        flash(f"Нельзя удалить базовые роли!", category="danger")
        return redirect(url_for("auth.roles"))
    role_name = role.name
    if request.method == "POST" and form.validate_on_submit():
        users_service = get_users_service()
        users_with_role = users_service.list(role_id=id_)
        if users_with_role:
            default_role = roles_service.get(slug=PermissionsConfig.ROLE_USER)
            for user in users_with_role:
                users_service.update(id_=user.id, role_id=default_role.id)
        roles_service.delete(id_)
        logging.info(f"'{current_user}' удалил роль - {role_name}")
        flash(f"Роль {role_name} - удалена.", category="success")
        return redirect(url_for("auth.roles"))
    return render_template(
        "auth/roles_delete.html",
        title="Удаление пользователя",
        form=form,
        name=role_name,
    )
