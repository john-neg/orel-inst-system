from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.session import Session
from sqlalchemy.orm import DeclarativeBase, scoped_session


class DefaultBase(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=DefaultBase)


def get_db_session(database: SQLAlchemy = db) -> scoped_session[Session]:
    """Возвращает текущую сессию базы данных SQLAlchemy."""
    return database.session
