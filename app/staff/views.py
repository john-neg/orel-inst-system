import logging
import datetime as dt

from flask import render_template, request, url_for
from flask_login import login_required
from werkzeug.utils import redirect

from config import ApeksConfig as Apeks, MongoDBSettings, FlaskConfig
from . import bp
from .forms import StableStaffForm
from ..common.func.api_get import check_api_db_response, get_state_staff_history
from ..common.func.organization import get_departments
from ..db.database import db
from ..db.mongodb import get_mongo_db
from ..services.base_db_service import BaseDBService


@bp.route("/stable_staff", methods=["GET", "POST"])
async def stable_staff():
    form = StableStaffForm()

    today_date = dt.date.today()
    mongo_db = get_mongo_db()
    db_collection = mongo_db[MongoDBSettings.STAFF_STABLE_COLLECTION]

    current_data = db_collection.find_one({"date": today_date.isoformat()})
    if not current_data:
        current_data = {
            'date': today_date.isoformat(),
            'departments': {},
            'status': FlaskConfig.STAFF_IN_PROGRESS_STATUS
        }
        db_collection.insert_one(current_data)

    if request.method == "POST" and form.validate_on_submit():
        if request.form.get('finish_edit'):
            db_collection.find_one_and_update(
                {"_id": current_data.get("_id")},
                {"$set": {'status': FlaskConfig.STAFF_COMPLETED_STATUS}}
            )
            return redirect(url_for('staff.stable_staff'))
        elif request.form.get('enable_edit'):
            db_collection.find_one_and_update(
                {"_id": current_data.get("_id")},
                {"$set": {'status': FlaskConfig.STAFF_IN_PROGRESS_STATUS}}
            )
            return redirect(url_for('staff.stable_staff'))

    departments = await get_departments()
    staff_history = await check_api_db_response(
        await get_state_staff_history(today_date)
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
        dept_cur_data= current_data['departments'].get(str(dept))
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
        date=today_date,
        staff_data=staff_data,
        doc_status=current_data['status']
    )


@bp.route("/stable_staff_edit/<int:department_id>", methods=["GET", "POST"])
async def stable_staff_edit(department_id):
    # department_id = int(request.args.get("department_id"))
    return department_id
