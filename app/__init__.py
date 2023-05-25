
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask.logging import create_logger

from config import FlaskConfig, ApeksConfig, LoggerConfig
from app.auth import bp as login_bp
from app.common.extensions import login_manager
from app.db.database import db
from app.library import bp as library_bp
from app.load import bp as load_bp
from app.main import bp as main_bp
from app.plans import bp as plans_bp
from app.programs import bp as programs_bp
from app.schedule import bp as schedule_bp
from app.tools import bp as tools_bp


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
    login_manager.init_app(app)
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
            try:
                os.remove(os.path.join(temp_directory, file))
            except FileNotFoundError:
                pass

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
        db.init_app(app)
        # if not os.path.exists(os.path.join(BASEDIR, 'app.db')):
        #     init_db()

    return app
