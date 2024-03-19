import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(".")

from app.core.db.staff_models import (
    StaffStableBusyTypes,
    StaffVariousBusyTypes,
    StaffVariousIllnessTypes,
)
from app.core.func.app_core import read_json_file
from app.core.services.db_staff_services import (
    StaffStableBusyTypesCRUDService,
    StaffVariousBusyTypesCRUDService,
    StaffVariousIllnessTypesCRUDService,
)
from config import FlaskConfig, BASEDIR


engine = create_engine(FlaskConfig.SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

FILE_DIR = os.path.join(BASEDIR, "tools", "data_staff")


# Заполняем данные о причинах отсутствия постоянного состава
staff_stable_service = StaffStableBusyTypesCRUDService(
    StaffStableBusyTypes, db_session=session
)
documents_data = read_json_file(os.path.join(FILE_DIR, "staff_stable_busy_types.json"))
for data in documents_data:
    if not staff_stable_service.get(slug=data):
        staff_stable_service.create(
            slug=data, name=documents_data[data], is_active=True
        )

# Заполняем данные о причинах отсутствия переменного состава
staff_various_busy_service = StaffVariousBusyTypesCRUDService(
    StaffVariousBusyTypes, db_session=session
)
documents_data = read_json_file(os.path.join(FILE_DIR, "staff_various_busy_types.json"))
for data in documents_data:
    if not staff_various_busy_service.get(slug=data):
        staff_various_busy_service.create(
            slug=data, name=documents_data[data], is_active=True
        )

staff_various_illness_service = StaffVariousIllnessTypesCRUDService(
    StaffVariousIllnessTypes, db_session=session
)
documents_data = read_json_file(
    os.path.join(FILE_DIR, "staff_various_illness_types.json")
)
for data in documents_data:
    if not staff_various_illness_service.get(slug=data):
        staff_various_illness_service.create(
            slug=data, name=documents_data[data], is_active=True
        )
