import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



sys.path.append('.')

from app.core.db.staff_models import (
    StaffStableBusyTypes,
    StaffVariousBusyTypes,
    StaffVariousIllnessTypes
)
from app.core.func.app_core import read_json_file
from app.core.services.db_staff_service import StaffStableBusyTypesCRUDService
from config import FlaskConfig, BASEDIR


engine = create_engine(FlaskConfig.SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

FILE_DIR = os.path.join(BASEDIR, "tools", "data_staff")


# Заполняем данные о причинах отсутствия постоянного состава
staff_stable_service = StaffStableBusyTypesCRUDService(StaffStableBusyTypes, db_session=session)

documents_data = read_json_file(os.path.join(FILE_DIR, "staff_stable_busy_types.json"))
for data in documents_data:
    staff_stable_service.create(
        slug=data,
        name=documents_data[data],
        is_active=True
    )
