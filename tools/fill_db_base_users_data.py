import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append('.')

from app.db.auth_models import UsersRoles, Users
from app.services.auth_service import UsersCRUDService, UsersRolesCRUDService
from config import FlaskConfig


engine = create_engine(FlaskConfig.SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

users_service = UsersCRUDService(Users, db_session=session)
users_role_service = UsersRolesCRUDService(UsersRoles, db_session=session)

roles = {
    FlaskConfig.ROLE_ADMIN: 'Администратор',
    FlaskConfig.ROLE_METOD: 'Методист',
    FlaskConfig.ROLE_BIBL: 'Библиотека',
    FlaskConfig.ROLE_USER: 'Пользователь',
    FlaskConfig.ROLE_STAFF: 'Строевая записка',
}

for slug, name in roles.items():
    if not users_role_service.get(slug=slug):
        role = users_role_service.create(slug=slug, name=name)
        users_service.create_user(username=slug, password=slug, role_id=role.id)
