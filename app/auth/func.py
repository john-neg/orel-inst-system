from functools import wraps

from flask import current_app, flash, url_for
from flask_login import current_user


def has_permission(*args):
    if current_user.is_authenticated and set(args).intersection(
        set(map(str, current_user.role.permissions))
    ):
        return True
    return False


def permission_required(*permissions):
    """
    Декоратор проверяет, что у пользователя есть необходимые права доступа.
    """

    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.redirect(url_for("auth.login"))
            if not has_permission(*permissions):
                flash("Отсутствуют необходимые права доступа", "danger")
                return current_app.redirect(url_for("main.index"))
            return func(*args, **kwargs)

        return decorated_view

    return wrapper
