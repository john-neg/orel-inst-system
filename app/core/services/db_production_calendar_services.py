from flask_sqlalchemy.session import Session
from sqlalchemy.orm import scoped_session

from ..db.database import get_db_session
from ..db.reports_models import (
    ProductionCalendarHolidays,
    ProductionCalendarWorkingDays,
)
from ..repository.sqlalchemy_repository import DbRepository


class ProductionCalendarHolidaysCRUDService(DbRepository[ProductionCalendarHolidays]):
    """Класс для CRUD операций для моделей ProductionCalendarHolidays."""


def get_productions_calendar_holidays_service(
    model: type[ProductionCalendarHolidays] = ProductionCalendarHolidays,
    db_session: scoped_session[Session] = get_db_session(),
) -> ProductionCalendarHolidaysCRUDService:
    return ProductionCalendarHolidaysCRUDService(model, db_session)


class ProductionCalendarWorkingDaysCRUDService(
    DbRepository[ProductionCalendarWorkingDays]
):
    """Класс для CRUD операций для модели ProductionCalendarWorkingDays."""


def get_productions_calendar_working_days_service(
    model: type[ProductionCalendarWorkingDays] = ProductionCalendarWorkingDays,
    db_session: scoped_session[Session] = get_db_session(),
) -> ProductionCalendarWorkingDaysCRUDService:
    return ProductionCalendarWorkingDaysCRUDService(model, db_session)
