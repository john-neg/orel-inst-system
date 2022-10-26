import logging
import os

from flask import Flask
from flask.logging import create_logger
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_login import LoginManager

from config import FlaskConfig, ApeksConfig as Apeks, BASEDIR
from .auth import bp as login_bp
from .common.classes.MyModelView import MyModelView
from .db.database import db
from .db.func import init_db
from .db.models import User
from .library import bp as library_bp
from .load import bp as load_bp
from .main import bp as main_bp
from .plans import bp as plans_bp
from .programs import bp as programs_bp
from .schedule import bp as schedule_bp

login = LoginManager()
login.login_view = "auth.login"
admin = Admin()


def check_tokens() -> bool:
    """Проверяем переменные окружения."""
    required_env = {
        "SECRET_KEY": FlaskConfig.SECRET_KEY,
        "APEKS_URL": Apeks.URL,
        "APEKS_TOKEN": Apeks.TOKEN,
    }
    missing_env = []
    for key in required_env:
        if not required_env[key]:
            missing_env.append(key)
    if not missing_env:
        return True
    else:
        logging.critical(
            "Отсутствуют необходимые переменные окружения: " f'{", ".join(missing_env)}'
        )
        raise SystemExit(
            "Отсутствуют ключи доступа. Программа принудительно остановлена."
        )


def register_extensions(application):
    db.init_app(application)
    login.init_app(application)
    admin.init_app(application)
    create_logger(application)


def register_blueprints(application):
    application.register_blueprint(login_bp)
    application.register_blueprint(main_bp)
    application.register_blueprint(schedule_bp)
    application.register_blueprint(load_bp)
    application.register_blueprint(plans_bp, url_prefix="/plans")
    application.register_blueprint(programs_bp, url_prefix="/programs")
    application.register_blueprint(library_bp)


def create_app(config_class=FlaskConfig):

    app = Flask(__name__)
    app.config.from_object(config_class)
    check_tokens()
    register_extensions(app)
    register_blueprints(app)

    admin.add_link(MenuLink(name="Вернуться на основной сайт", category="", url="/"))
    admin.add_view(MyModelView(User, db.session))

    if not os.path.exists(os.path.join(BASEDIR, 'app.db')):
        with app.app_context():
            init_db()

    return app


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
