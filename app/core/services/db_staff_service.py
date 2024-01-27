from flask_sqlalchemy.session import Session
from sqlalchemy.orm import scoped_session

from ..db.database import get_db_session
from ..db.staff_models import StaffStableBusyTypes
from ..repository.sqlalchemy_repository import DbRepository


class StaffStableBusyTypesCRUDService(DbRepository[StaffStableBusyTypes]):
    """Класс для CRUD операций модели StaffStableBusyTypes"""

    pass


def get_staff_stable_busy_types_service(
        model: type[StaffStableBusyTypes] = StaffStableBusyTypes,
        db_session: scoped_session[Session] = get_db_session()
) -> StaffStableBusyTypesCRUDService:
    return StaffStableBusyTypesCRUDService(model, db_session)
