from flask_sqlalchemy.session import Session
from sqlalchemy.orm import scoped_session
from werkzeug.security import check_password_hash, generate_password_hash

from ..db.auth_models import Users, UsersPermissions, UsersRoles
from ..db.database import get_db_session
from ..repository.sqlalchemy_repository import DbRepository, ModelType


class UsersCRUDService(DbRepository[Users]):
    """Класс для CRUD операций модели Users"""

    @staticmethod
    def get_password_hash(password) -> str:
        return generate_password_hash(password)

    @staticmethod
    def check_password(password_hash, password) -> bool:
        return check_password_hash(password_hash, password)

    def create_user(self, username, password, role_id) -> ModelType:
        new_user = self.create(
            username=username,
            password_hash=self.get_password_hash(password),
            role_id=role_id,
        )
        return new_user

    def update_user(
            self,
            user_id: int,
            username: str | None = None,
            password: str | None = None,
            role_id: int | None = None,
    ) -> ModelType:
        update_dict = {}
        if username:
            update_dict["username"] = username
        if password:
            update_dict["password_hash"] = self.get_password_hash(password)
        if role_id:
            update_dict["role_id"] = role_id
        return self.update(user_id, **update_dict)


def get_users_service(
        model: type[Users] = Users,
        db_session: scoped_session[Session] = get_db_session()
) -> UsersCRUDService:
    return UsersCRUDService(
        model=model,
        db_session=db_session
    )


class UsersRolesCRUDService(DbRepository[UsersRoles]):
    """Класс для CRUD операций модели UsersRoles."""


def get_users_roles_service(
        model: type[UsersRoles] = UsersRoles,
        db_session: scoped_session[Session] = get_db_session()
) -> UsersRolesCRUDService:
    return UsersRolesCRUDService(
        model=model,
        db_session=db_session
    )


class UsersPermissionsCRUDService(DbRepository[UsersPermissions]):
    """Класс для CRUD операций модели UsersPermissions."""


def get_users_permissions_service(
        model: type[UsersPermissions] = UsersPermissions,
        db_session: scoped_session[Session] = get_db_session()
) -> UsersPermissionsCRUDService:
    return UsersPermissionsCRUDService(
        model=model,
        db_session=db_session
    )
