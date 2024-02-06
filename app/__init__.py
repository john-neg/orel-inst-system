import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask.logging import create_logger

from config import (
    ApeksConfig,
    FlaskConfig,
    LoggerConfig,
    MongoDBSettings,
    PermissionsConfig,
)
from .auth import bp as login_bp
from .auth.func import has_permission
from .core.db.database import db
from .core.extensions import login_manager
from .core.services.db_users_service import (
    get_users_permissions_service,
    get_users_roles_service,
    get_users_service,
)
from .library import bp as library_bp
from .main import bp as main_bp
from .plans import bp as plans_bp
from .programs import bp as programs_bp
from .reports import bp as reports_bp
from .schedule import bp as schedule_bp
from .staff import bp as staff_bp
from .tools import bp as tools_bp


def check_tokens() -> bool:
    """Проверяет наличие переменных окружения."""
    required_env = {
        "SECRET_KEY": FlaskConfig.SECRET_KEY,
        "APEKS_URL": ApeksConfig.URL,
        "APEKS_TOKEN": ApeksConfig.TOKEN,
    }
    if FlaskConfig.LDAP_AUTH:
        required_env.update(
            {
                "AD_DOMAIN": FlaskConfig.AD_DOMAIN,
                "AD_SERVER": FlaskConfig.AD_SERVER,
                "AD_SEARCH_TREE": FlaskConfig.AD_SEARCH_TREE,
            }
        )
    missing_env = []
    for key in required_env:
        if not required_env[key]:
            missing_env.append(key)
    if not missing_env:
        return True
    else:
        logging.critical(
            f'Отсутствуют необходимые переменные окружения: {", ".join(missing_env)}'
        )
        raise SystemExit(
            "Отсутствуют ключи доступа. Программа принудительно остановлена."
        )


def register_extensions(app):
    """Регистрирует расширения."""
    login_manager.init_app(app)
    create_logger(app)


def register_blueprints(app):
    """Регистрирует модули (blueprints)."""
    app.register_blueprint(login_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(staff_bp, url_prefix="/staff")
    app.register_blueprint(plans_bp, url_prefix="/plans")
    app.register_blueprint(programs_bp, url_prefix="/programs")
    app.register_blueprint(library_bp)
    app.register_blueprint(tools_bp, url_prefix="/tools")


def add_functions_to_templates():
    """Добавляет в шаблоны Jinja2 доступ к функциям."""
    return dict(has_permission=has_permission)


def check_base_roles_and_permissions_in_database():
    users_service = get_users_service()
    users_role_service = get_users_roles_service()
    permissions_service = get_users_permissions_service()
    for slug, name in PermissionsConfig.BASE_ROLES.items():
        if not users_role_service.get(slug=slug):
            users_role_service.create(slug=slug, name=name)
    if not users_service.get(username=PermissionsConfig.ROLE_ADMIN):
        role = users_role_service.get(slug=PermissionsConfig.ROLE_ADMIN)
        users_service.create_user(
            username=PermissionsConfig.ROLE_ADMIN,
            password=PermissionsConfig.ROLE_ADMIN,
            role_id=role.id,
        )
    for slug, name in PermissionsConfig.PERMISSION_DESCRIPTIONS.items():
        if not permissions_service.get(slug=slug):
            permissions_service.create(slug=slug, name=name)
            admin_role = users_role_service.get(slug=PermissionsConfig.ROLE_ADMIN)
            users_role_service.update(
                admin_role.id,
                permissions=[permission for permission in permissions_service.list()],
            )


def create_app(config_class=FlaskConfig):
    """Создает приложение Flask."""

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
                backupCount=LoggerConfig.BACKUP_COUNT,
            ),
        ],
    )

    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config.from_object(PermissionsConfig)
    app.config.from_object(MongoDBSettings)
    app.context_processor(add_functions_to_templates)
    check_tokens()
    register_extensions(app)

    with app.app_context():
        register_blueprints(app)
        db.init_app(app)
        check_base_roles_and_permissions_in_database()
        # if not os.path.exists(os.path.join(BASEDIR, 'app.db')):
        #     init_db()

    return app
