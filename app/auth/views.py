import logging

from flask import render_template, redirect, url_for, flash, request
from flask_login import logout_user, login_user, current_user, login_required
from sqlalchemy import select

from app.auth.forms import UserRegisterForm, UserLoginForm, UserDeleteForm, UserEditForm
from app.common.extensions import login_manager
from app.db.database import db
from app.db.models import User
from config import FlaskConfig
from . import bp
from ..common.func.app_core import get_paginated_data


@login_manager.user_loader
def load_user(user_id):
    with db.session() as session:
        return session.get(User, user_id)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = UserLoginForm()
    if form.validate_on_submit():
        with db.session() as session:
            user = session.scalars(
                select(User).filter_by(username=form.username.data).limit(1)
            ).first()
        if user is None or not user.check_password(form.password.data):
            error = "Неверный логин или пароль"
            return render_template(
                "auth/login.html", title="Авторизация", form=form, error=error
            )
        login_user(user)
        logging.info(f"Успешная авторизация - {user}")
        return redirect(url_for("main.index"))
    return render_template("auth/login.html", title="Авторизация", form=form)


@bp.route("/users", methods=["GET", "POST"])
@login_required
def users():
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for("main.index"))
    paginated_data = get_paginated_data(User.query)
    return render_template(
        "auth/users.html", title="Пользователи", paginated_data=paginated_data
    )


@bp.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for("main.index"))
    form = UserRegisterForm()
    if form.validate_on_submit():
        new_user = User.add_user(
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
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for("main.index"))
    user = db.session.get(User, int(user_id))

    if not user:
        flash(f"Пользователь не найден!", category="danger")
        return redirect(url_for("auth.users"))

    form = UserEditForm()
    form.username.data = user.username
    form.role.data = user.role

    if form.validate_on_submit():
        user.edit_user(
            username=request.form.get("username"),
            password=request.form.get("password"),
            role_id=request.form.get("role"),
        )
        logging.info(
            f"'{current_user}' отредактировал данные " f"пользователя - {user.username}"
        )
        flash(
            f"Информация о пользователе {user.username} " f"успешно изменена.",
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
    if current_user.role.slug != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for("main.index"))

    form = UserDeleteForm()
    with db.session() as session:
        user = session.get(User, user_id)

    if not user:
        flash(f"Пользователь не найден!", category="danger")
        return redirect(url_for("auth.users"))

    if current_user.id == user_id:
        flash(f"Нельзя удалить самого себя!", category="danger")
        return redirect(url_for("auth.users"))

    if form.validate_on_submit():
        user.delete_user(user_id)

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
