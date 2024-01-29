import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append('.')

from app.core.repository.sqlalchemy_repository import DbRepository
from app.tools.payment.func import make_slug
from app.core.func.app_core import read_json_file
from app.core.db.payment_models import (
    PaymentRates,
    PaymentRatesValues,
    PaymentAddons,
    PaymentAddonsValues,
    PaymentMatchRateAddon,
    PaymentSingleAddons,
    PaymentMatchRateSingle,
    PaymentIncrease,
    PaymentMatchRateIncrease,
    PaymentPensionDutyCoefficient,
    PaymentGlobalCoefficient, PaymentDocuments,
)
from config import FlaskConfig, BASEDIR


engine = create_engine(FlaskConfig.SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

FILE_DIR = os.path.join(BASEDIR, "tools", "data_payment")


# Заполняем данные о нормативных документах
doc_service = DbRepository(PaymentDocuments, db_session=session)

documents_data = read_json_file(os.path.join(FILE_DIR, "documents_data.json"))
for data in documents_data:
    doc_service.create(name=documents_data[data].get("name"))


# Заполняем данные об окладах
rate_service = DbRepository(PaymentRates, db_session=session)
rate_val_service = DbRepository(PaymentRatesValues, db_session=session)

rate_data = read_json_file(os.path.join(FILE_DIR, "rate_data.json"))
for rate in rate_data:
    current_rate = rate_service.create(
        slug=make_slug(rate_data[rate].get("name"), prefix="rate_"),
        name=rate_data[rate].get("name"),
        payment_name=rate_data[rate].get("payment_name"),
        salary=rate_data[rate].get("salary"),
        pension=rate_data[rate].get("pension"),
    )
    for record in rate_data[rate].get("data"):
        for name, value in rate_data[rate]["data"][record].get("values").items():
            rate_val_service.create(
                name=name,
                value=value,
                rate_id=current_rate.id,
                description=rate_data[rate]["data"][record].get("description"),
                document_id=rate_data[rate]["data"][record].get('document_id'),
            )


# Заполняем данные о надбавках
addon_service = DbRepository(PaymentAddons, db_session=session)
addon_values_service = DbRepository(PaymentAddonsValues, db_session=session)

addons_data = read_json_file(os.path.join(FILE_DIR, "addons_data.json"))
for data in addons_data:
    addon = addon_service.create(
        slug=make_slug(addons_data[data].get("name"), prefix="addon_"),
        name=addons_data[data].get("name"),
        payment_name=addons_data[data].get("payment_name"),
        salary=addons_data[data].get("salary"),
        pension=addons_data[data].get("pension"),
    )
    for name, value in addons_data[data].get("data").items():
        addon_values_service.create(
            name=name,
            value=value,
            description=addons_data[data].get("description"),
            addon_id=addon.id,
            document_id=addons_data[data].get("document_id"),
        )
    for rate_name in addons_data[data].get("apply_to"):
        rate = rate_service.get(name=rate_name)
        session.add(
            PaymentMatchRateAddon(
                rate_id=rate.id,
                addon_id=addon.id,
            )
        )
        session.commit()


# Заполняем данные о фиксированных надбавках
single_add_service = DbRepository(PaymentSingleAddons, db_session=session)

single_addons_data = read_json_file(os.path.join(FILE_DIR, "single_addons_data.json"))
for data in single_addons_data:
    single_add = single_add_service.create(
        slug=make_slug(single_addons_data[data].get("name"), prefix="single_"),
        name=single_addons_data[data].get("name"),
        payment_name=single_addons_data[data].get("payment_name"),
        value=single_addons_data[data].get("value"),
        description=single_addons_data[data].get("description"),
        document_id=single_addons_data[data].get("document_id"),
        salary=single_addons_data[data].get("salary"),
        pension=single_addons_data[data].get("pension"),
        default_state=single_addons_data[data].get("default_state"),
    )
    for rate_name in single_addons_data[data].get("apply_to"):
        rate = rate_service.get(name=rate_name)
        session.add(
            PaymentMatchRateSingle(
                rate_id=rate.id,
                single_addon_id=single_add.id,
            )
        )
        session.commit()


# Заполняем данные об индексациях
increase_service = DbRepository(PaymentIncrease, db_session=session)

increase_data = read_json_file(os.path.join(FILE_DIR, "increase_data.json"))
for data in increase_data:
    increase = increase_service.create(
        name=increase_data[data].get("name"),
        value=increase_data[data].get("value"),
        document_id=increase_data[data].get("document_id"),
    )
    for rate_name in increase_data[data].get("apply_to"):
        rate = rate_service.get(name=rate_name)
        session.add(
            PaymentMatchRateIncrease(
                rate_id=rate.id,
                increase_id=increase.id,
            )
        )
    session.commit()


# Заполняем данные о коэффициенте выслуги для расчета пенсии
pension_duty_service = DbRepository(PaymentPensionDutyCoefficient, db_session=session)

pension_duty_data = read_json_file(os.path.join(FILE_DIR, "pension_duty_data.json"))
for data in pension_duty_data:
    pension_duty_service.create(
        name=pension_duty_data[data].get("name"),
        value=pension_duty_data[data].get("value"),
        document_id=pension_duty_data[data].get("document_id"),
    )


# Заполняем данные о глобальных коэффициентах, изменяющих общую выплату
global_service = DbRepository(PaymentGlobalCoefficient, db_session=session)

global_coefficient_data = read_json_file(
    os.path.join(FILE_DIR, "global_coefficient_data.json")
)
for data in global_coefficient_data:
    global_service.create(
        slug=make_slug(global_coefficient_data[data].get("name"), prefix="coeff_"),
        name=global_coefficient_data[data].get("name"),
        value=global_coefficient_data[data].get("value"),
        payment_name=global_coefficient_data[data].get("payment_name"),
        description=global_coefficient_data[data].get("description"),
        document_id=global_coefficient_data[data].get("document_id"),
        salary=global_coefficient_data[data].get("salary"),
        pension=global_coefficient_data[data].get("pension"),
    )
