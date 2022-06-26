import logging
import os

from flask import Flask
from flask.logging import create_logger
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from auth.models import User, init_db
from common.classes.MyModelView import MyModelView
from config import FlaskConfig, ApeksConfig as Apeks, BASEDIR

db = SQLAlchemy()
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
        return False


def create_app(config_class=FlaskConfig):

    app = Flask(__name__)
    app.config.from_object(config_class)

    if not check_tokens():
        raise SystemExit("Программа принудительно остановлена.")

    db.init_app(app)
    login.init_app(app)
    admin.init_app(app)
    create_logger(app)

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

    admin.add_link(MenuLink(name="Вернуться на основной сайт", category="", url="/"))
    admin.add_view(MyModelView(User, db.session))

    if not os.path.exists(os.path.join(BASEDIR, 'app.db')):
        with app.app_context():
            init_db()

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

    return app


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
