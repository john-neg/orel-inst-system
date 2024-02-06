import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(".")

from app.core.db.auth_models import UsersRoles, Users, UsersPermissions
from app.core.services.db_users_service import (
    UsersCRUDService,
    UsersRolesCRUDService,
    UsersPermissionsCRUDService,
)
from config import FlaskConfig, PermissionsConfig

engine = create_engine(FlaskConfig.SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

users_service = UsersCRUDService(Users, db_session=session)
users_role_service = UsersRolesCRUDService(UsersRoles, db_session=session)
users_permission_service = UsersPermissionsCRUDService(
    UsersPermissions, db_session=session
)

roles = {
    PermissionsConfig.ROLE_ADMIN: "Администратор",
}

for slug, name in roles.items():
    if not users_role_service.get(slug=slug):
        role = users_role_service.create(slug=slug, name=name)
        users_service.create_user(username=slug, password=slug, role_id=role.id)

for slug, name in PermissionsConfig.PERMISSION_DESCRIPTIONS.items():
    if not users_permission_service.get(slug=slug):
        permission = users_permission_service.create(slug=slug, name=name)
        admin_role = users_role_service.get(slug=PermissionsConfig.ROLE_ADMIN)
        users_role_service.update(
            admin_role.id,
            permissions=[permission for permission in users_permission_service.list()],
        )
