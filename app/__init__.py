import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask.logging import create_logger
from flask_admin.menu import MenuLink

from config import FlaskConfig, ApeksConfig, LoggerConfig, BASEDIR
from .auth import bp as login_bp
from .db.AdminModelView import AdminModelView
from .common.extensions import login, admin
from .db.database import db_session, init_db
from .db.models import User
from .library import bp as library_bp
from .load import bp as load_bp
from .main import bp as main_bp
from .plans import bp as plans_bp
from .programs import bp as programs_bp
from .schedule import bp as schedule_bp
from .tools import bp as tools_bp


def check_tokens() -> bool:
    """Проверяем переменные окружения."""
    required_env = {
        "SECRET_KEY": FlaskConfig.SECRET_KEY,
        "APEKS_URL": ApeksConfig.URL,
        "APEKS_TOKEN": ApeksConfig.TOKEN,
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


def register_extensions(app):
    login.init_app(app)
    admin.init_app(app)
    create_logger(app)


def register_blueprints(app):
    app.register_blueprint(login_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(load_bp)
    app.register_blueprint(plans_bp, url_prefix="/plans")
    app.register_blueprint(programs_bp, url_prefix="/programs")
    app.register_blueprint(library_bp)
    app.register_blueprint(tools_bp, url_prefix="/tools")


def create_app(config_class=FlaskConfig):
    """Flask - Application factory."""

    # Создание директорий если отсутствуют
    for local_directory in (
            FlaskConfig.TEMP_FILE_DIR,
            FlaskConfig.EXPORT_FILE_DIR,
            FlaskConfig.UPLOAD_FILE_DIR,
            FlaskConfig.LOG_FILE_DIR,
    ):
        if not os.path.exists(local_directory):
            os.mkdir(local_directory, 0o755)

    # Очистка временных директорий
    for temp_directory in (
            FlaskConfig.EXPORT_FILE_DIR,
            FlaskConfig.UPLOAD_FILE_DIR,
    ):
        for file in os.listdir(temp_directory):
            os.remove(os.path.join(temp_directory, file))

    # Logger Configuration
    logging.basicConfig(
        level=LoggerConfig.LEVEL,
        format=LoggerConfig.FORMAT,
        handlers=[
            logging.StreamHandler(stream=sys.stdout),
            RotatingFileHandler(
                LoggerConfig.LOG_FILE,
                maxBytes=LoggerConfig.MAX_BYTES,
                backupCount=LoggerConfig.BACKUP_COUNT
            ),
        ],
    )

    app = Flask(__name__)
    app.config.from_object(config_class)
    check_tokens()
    register_extensions(app)

    with app.app_context():
        register_blueprints(app)
        login.login_view = "auth.login"

        if not os.path.exists(os.path.join(BASEDIR, 'app.db')):
            init_db()

        admin.add_link(
            MenuLink(name="Вернуться на основной сайт", category="", url="/")
        )
        admin.add_view(AdminModelView(User, db_session))

        @app.teardown_appcontext
        def shutdown_session(exception=None):
            db_session.remove()

    return app
