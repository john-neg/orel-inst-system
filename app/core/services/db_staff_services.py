from flask_sqlalchemy.session import Session
from sqlalchemy.orm import scoped_session

from ..db.database import get_db_session
from ..db.staff_models import (
    StaffAllowedFaculty,
    StaffStableBusyTypes,
    StaffVariousBusyTypes,
    StaffVariousIllnessTypes,
)
from ..repository.sqlalchemy_repository import DbRepository


class StaffStableBusyTypesCRUDService(DbRepository[StaffStableBusyTypes]):
    """Класс для CRUD операций модели StaffStableBusyTypes"""


def get_staff_stable_busy_types_service(
    model: type[StaffStableBusyTypes] = StaffStableBusyTypes,
    db_session: scoped_session[Session] = get_db_session(),
) -> StaffStableBusyTypesCRUDService:
    return StaffStableBusyTypesCRUDService(model, db_session)


class StaffVariousBusyTypesCRUDService(DbRepository[StaffVariousBusyTypes]):
    """Класс для CRUD операций модели StaffVariousBusyTypes"""


def get_staff_various_busy_types_service(
    model: type[StaffVariousBusyTypes] = StaffVariousBusyTypes,
    db_session: scoped_session[Session] = get_db_session(),
) -> StaffVariousBusyTypesCRUDService:
    return StaffVariousBusyTypesCRUDService(model, db_session)


class StaffVariousIllnessTypesCRUDService(DbRepository[StaffVariousIllnessTypes]):
    """Класс для CRUD операций модели StaffVariousIllnessTypesCRUDService."""


def get_staff_various_illness_types_service(
    model: type[StaffVariousIllnessTypes] = StaffVariousIllnessTypes,
    db_session: scoped_session[Session] = get_db_session(),
) -> StaffVariousIllnessTypesCRUDService:
    return StaffVariousIllnessTypesCRUDService(model, db_session)


class StaffAllowedFacultyCRUDService(DbRepository[StaffAllowedFaculty]):
    """Класс для CRUD операций модели StaffStableBusyTypes"""


def get_staff_allowed_faculty_service(
    model: type[StaffAllowedFaculty] = StaffAllowedFaculty,
    db_session: scoped_session[Session] = get_db_session(),
) -> StaffAllowedFacultyCRUDService:
    return StaffAllowedFacultyCRUDService(model, db_session)
