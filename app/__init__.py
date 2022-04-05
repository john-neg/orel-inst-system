from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from config import FlaskConfig

db = SQLAlchemy()
login = LoginManager()
login.login_view = "auth.login"

def create_app(config_class=FlaskConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)

    from app.auth import bp as login_bp
    app.register_blueprint(login_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.schedule import bp as schedule_bp
    app.register_blueprint(schedule_bp)

    from app.load import bp as load_bp
    app.register_blueprint(load_bp)

    from app.plans import bp as plans_bp
    app.register_blueprint(plans_bp, url_prefix='/plans')

    from app.programs import bp as programs_bp
    app.register_blueprint(programs_bp, url_prefix='/programs')

    from app.library import bp as library_bp
    app.register_blueprint(library_bp)

    return app


from app.main import routes
