from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import FlaskConfig

engine = create_engine(FlaskConfig.SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """Создание структуры БД. Должны быть импортированы все модели."""

    from .models import User

    Base.metadata.create_all(bind=engine)

    user = User(username='admin', role=FlaskConfig.ROLE_ADMIN)
    user.set_password('admin')
    db_session.add(user)

    user = User(username='user', role=FlaskConfig.ROLE_USER)
    user.set_password('user')
    db_session.add(user)

    user = User(username='metod', role=FlaskConfig.ROLE_METOD)
    user.set_password('metod')
    db_session.add(user)

    user = User(username='bibl', role=FlaskConfig.ROLE_BIBL)
    user.set_password('bibl')
    db_session.add(user)
    db_session.commit()
