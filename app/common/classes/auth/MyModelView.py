from flask import url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from werkzeug.utils import redirect

from config import FlaskConfig


class MyModelView(ModelView):
    def is_accessible(self):
        return (
                current_user.is_authenticated
                and current_user.role == FlaskConfig.ROLE_ADMIN
        )

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("main.index"))
