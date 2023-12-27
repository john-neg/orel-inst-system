import logging
import datetime as dt

from flask import render_template, request, url_for, flash
from flask_login import login_required, current_user
from pymongo.errors import PyMongoError
from werkzeug.utils import redirect

from config import ApeksConfig as Apeks, MongoDBSettings, FlaskConfig
from . import bp
from .forms import StableStaffForm, create_staff_edit_form
from ..common.func.api_get import check_api_db_response, get_state_staff_history, \
    api_get_db_table
from ..common.func.app_core import data_processor
from ..common.func.organization import get_departments
from ..common.func.staff import get_state_staff
from ..db.auth_models import Users
from ..db.database import db
from ..db.mongodb import get_mongo_db
from ..db.staff_models import StaffStableBusyTypes
from ..services.base_db_service import BaseDBService


@bp.route("/stable_staff", methods=["GET", "POST"])
async def stable_staff():
    form = StableStaffForm()

    working_date = dt.date.today()
    mongo_db = get_mongo_db()
    staff_db = mongo_db[MongoDBSettings.STAFF_STABLE_COLLECTION]

    current_data = staff_db.find_one({"date": working_date.isoformat()})
    if not current_data:
        current_data = {
            'date': working_date.isoformat(),
            'departments': {},
            'status': FlaskConfig.STAFF_IN_PROGRESS_STATUS
        }
        staff_db.insert_one(current_data)

    if request.method == "POST" and form.validate_on_submit():
        if request.form.get('finish_edit'):
            staff_db.find_one_and_update(
                {"_id": current_data.get("_id")},
                {"$set": {'status': FlaskConfig.STAFF_COMPLETED_STATUS}}
            )
            return redirect(url_for('staff.stable_staff'))
        elif request.form.get('enable_edit'):
            staff_db.find_one_and_update(
                {"_id": current_data.get("_id")},
                {"$set": {'status': FlaskConfig.STAFF_IN_PROGRESS_STATUS}}
            )
            return redirect(url_for('staff.stable_staff'))

    departments = await get_departments()
    staff_history = await check_api_db_response(
        await get_state_staff_history(working_date)
    )
    for staff in staff_history:
        dept_id = int(staff.get('department_id'))
        dept_data = departments[dept_id]
        if staff.get('vacancy_id') and staff.get('value') == '1':
            dept_data['staff_total'] = dept_data.get('staff_total', 0) + 1
    staff_data = {key: {} for key in Apeks.DEPT_TYPES.values()}

    for dept in sorted(departments, key=lambda d: departments[d].get('short')):
        dept_data = departments[dept]
        dept_type = dept_data.get('type')
        dept_cur_data = current_data['departments'].get(str(dept))
        dept_total = dept_data.get('staff_total', 0)
        dept_abscence = (
            sum(len(val) for val in dept_cur_data['absence'].values())
            if dept_cur_data
            else "нет данных"
        )
        dept_stock = (
            dept_total - dept_abscence
            if isinstance(dept_abscence, int)
            else "нет данных"
        )

        if dept_type in staff_data:
            type_data = staff_data[dept_type]
            type_data[dept] = {
                'name': dept_data.get('short'),
                'staff_total': dept_total,
                'staff_absence': dept_abscence,
                'staff_stock': dept_stock,
            }

    return render_template(
        "staff/stable_staff.html",
        active="staff",
        form=form,
        date=working_date,
        staff_data=staff_data,
        doc_status=current_data['status']
    )


@bp.route("/stable_staff_edit/<int:department_id>", methods=["GET", "POST"])
async def stable_staff_edit(department_id):

    mongo_db = get_mongo_db()
    staff_db = mongo_db[MongoDBSettings.STAFF_STABLE_COLLECTION]
    logs_db = mongo_db[MongoDBSettings.STAFF_LOGS_COLLECTION]
    staff_stable_service = BaseDBService(StaffStableBusyTypes, db_session=db.session)
    working_date = (
        dt.date.fromisoformat(request.args.get("date"))
        if request.args.get("date")
        else dt.date.today()
    )

    staff_history = await check_api_db_response(
        await get_state_staff_history(
            working_date, department_id=department_id
        )
    )
    staff_ids = {
        item.get('staff_id'): item for item in staff_history
        if item.get('vacancy_id') and item.get('value') == '1'
    }

    department_data = list(
        await check_api_db_response(
            await api_get_db_table(
                Apeks.TABLES.get("state_departments"), id=department_id
            )
        )
    )
    department_name = department_data[0].get('name_short')

    state_staff = await get_state_staff(id=staff_ids.keys())

    state_staff_positions = data_processor(
        await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("state_staff_positions"))
        )
    )

    final_staff_data = []
    for staff_id, staff_hist in staff_ids.items():
        staff_id = staff_id
        position_id = int(staff_hist.get('position_id'))
        position = state_staff_positions.get(position_id)
        staff_data = state_staff.get(int(staff_id))

        final_staff_data.append(
            {
                'staff_id': staff_id,
                'name': staff_data.get('short'),
                'position': position.get('name'),
                'sort': position.get('sort')
            }
        )

    final_staff_data.sort(key=lambda x: int(x['sort']), reverse=True)

    busy_types = staff_stable_service.list(is_active=1)

    form = create_staff_edit_form(
        staff_data=final_staff_data,
        busy_types=busy_types
    )

    current_db_data = staff_db.find_one({"date": working_date.isoformat()})

    if request.method == 'POST' and form.validate_on_submit():
        if current_db_data.get('status') == FlaskConfig.STAFF_IN_PROGRESS_STATUS:
            load_data = {
                'id': department_id,
                'name': department_name,
                'total': len(staff_ids),
                'absence': {item.slug: {} for item in busy_types},
                'user': current_user.username if isinstance(current_user, Users) else 'anonymous',
                'updated': dt.datetime.now().isoformat()
            }
            for _id in staff_ids:
                staff_absence = request.form.get(f"staff_id_{_id}")
                if staff_absence != '0' and staff_absence in load_data['absence']:
                    load_data['absence'][staff_absence][_id] = state_staff[int(_id)].get('short')
                elif staff_absence != '0' and staff_absence not in load_data['absence']:
                    message = f"Форма вернула неизвестное Местонахождение: {staff_absence}"
                    flash(message, category="danger")
                    logging.info(message)

            try:
                staff_db.update_one(
                    {"date": working_date.isoformat()},
                    {
                        '$set': {f"departments.{department_id}": load_data}
                        },
                    upsert=True
                )
                logs_db.insert_one(load_data)
                current_db_data = staff_db.find_one({"date": working_date.isoformat()})
                message = (f"Данные подразделения {department_name} за "
                           f"{working_date.isoformat()} успешно переданы")
                flash(message, category="success")
                logging.info(message)
            except PyMongoError as error:
                message = f"Произошла ошибка записи данных: {error}"
                flash(message, category="danger")
                logging.info(message)
        else:
            message = f"Данные за {working_date.isoformat()} закрыты для редактирования"
            flash(message, category="danger")

    current_dept_data = current_db_data['departments'].get(str(department_id))
    if current_dept_data:
        for absence, items in current_dept_data['absence'].items():
            if items:
                for _id in items:
                    attr = getattr(form, f"staff_id_{_id}")
                    attr.data = absence

    return render_template(
        "staff/staff_edit.html",
        active="staff",
        form=form,
        date=working_date,
        department=department_name,
        staff_data=final_staff_data,
        status=current_db_data.get('status')
    )
