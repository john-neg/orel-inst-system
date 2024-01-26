from flask_sqlalchemy.session import Session
from sqlalchemy.orm import scoped_session

from ..db.auth_models import UsersRoles
from ..db.database import get_db_session
from ..repository.sqlalchemy_repository import DbRepository


class UsersRolesCRUDService(DbRepository[UsersRoles]):
    """Класс для CRUD операций модели StaffStableBusyTypes"""

    pass


def get_users_roles_service(
        model: type[UsersRoles] = UsersRoles,
        db_session: scoped_session[Session] = get_db_session()
) -> UsersRolesCRUDService:
    return UsersRolesCRUDService(
        model=model,
        db_session=db_session
    )
