from flask import Flask, url_for
from flask_admin import Admin, AdminIndexView
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect

from config import FlaskConfig

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
admin = Admin()


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return (
            current_user.is_authenticated
            and current_user.role == FlaskConfig.ROLE_ADMIN
        )

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("main.index"))


def create_app(config_class=FlaskConfig):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    admin.init_app(app, index_view=MyAdminIndexView())

    from app.auth import bp as login_bp
    app.register_blueprint(login_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.schedule import bp as schedule_bp
    app.register_blueprint(schedule_bp)

    from app.load import bp as load_bp
    app.register_blueprint(load_bp)

    from app.plans import bp as plans_bp
    app.register_blueprint(plans_bp, url_prefix="/plans")

    from app.programs import bp as programs_bp
    app.register_blueprint(programs_bp, url_prefix="/programs")

    from app.library import bp as library_bp
    app.register_blueprint(library_bp)

    return app
