from config import FlaskConfig
from .database import db
from .models import User


def init_db():
    """Создает начальную базу данных пользователей."""

    db.create_all()

    u = User(username='admin', role=FlaskConfig.ROLE_ADMIN)
    u.set_password('admin')
    db.session.add(u)

    u = User(username='user', role=FlaskConfig.ROLE_USER)
    u.set_password('user')
    db.session.add(u)

    u = User(username='metod', role=FlaskConfig.ROLE_METOD)
    u.set_password('metod')
    db.session.add(u)

    u = User(username='bibl', role=FlaskConfig.ROLE_BIBL)
    u.set_password('bibl')
    db.session.add(u)

    db.session.commit()
