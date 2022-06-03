from flask import render_template, redirect, url_for, flash
from flask_admin.menu import MenuLink
from flask_login import logout_user, login_user, current_user, login_required

from app import db, admin
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.auth.models import User
from app.common.auth.MyModelView import MyModelView
from config import FlaskConfig


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            error = "Неверный логин или пароль"
            return render_template(
                "auth/login.html", title="Авторизация", form=form, error=error
            )
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("main.index"))
    return render_template("auth/login.html", title="Авторизация", form=form)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated and current_user.role != FlaskConfig.ROLE_ADMIN:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
    return render_template(
        "auth/register.html",
        title="Регистрация нового пользователя",
        form=form,
        active="admin",
    )


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


admin.add_link(MenuLink(name="Вернуться на основной сайт", category="", url="/"))
admin.add_view(MyModelView(User, db.session))
