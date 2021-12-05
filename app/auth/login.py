from flask import render_template, redirect, url_for
from flask_login import logout_user, login_user, current_user, login_required
from app.auth import bp
from app.auth.forms import LoginForm
from app.auth.models import User


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


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
