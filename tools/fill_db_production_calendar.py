import os
import sys
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append('.')

from app.core.repository.sqlalchemy_repository import DbRepository
from app.core.func.app_core import read_json_file
from app.core.db.reports_models import (
    ProductionCalendarHolidays,
    ProductionCalendarWorkingDays,
)
from config import FlaskConfig, BASEDIR


engine = create_engine(FlaskConfig.SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

FILE_DIR = os.path.join(BASEDIR, "tools", "production_calendar")

holidays_service = DbRepository(
    ProductionCalendarHolidays, db_session=session
)
working_service = DbRepository(
    ProductionCalendarWorkingDays, db_session=session
)

holidays_data = read_json_file(os.path.join(FILE_DIR, "calendars.json"))

for year in holidays_data:
    for holiday in holidays_data[year].get("holidays"):
        holidays_service.create(date=datetime.fromisoformat(holiday))
    for working in holidays_data[year].get("working"):
        working_service.create(date=datetime.fromisoformat(working))
