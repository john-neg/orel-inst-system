import logging
import datetime as dt

from flask import render_template, request, url_for, flash
from flask_login import login_required, current_user
from pymongo.errors import PyMongoError
from werkzeug.utils import redirect

from config import ApeksConfig as Apeks, MongoDBSettings, FlaskConfig
from . import bp
from .forms import StableStaffForm, create_staff_edit_form
from ..core.func.api_get import (
    check_api_db_response,
    get_state_staff_history,
    api_get_db_table,
)
from ..core.func.app_core import data_processor
from ..core.func.organization import get_departments
from ..core.func.staff import get_state_staff
from ..core.reports.stable_staff_report import generate_stable_staff_report
from ..core.db.auth_models import Users
from ..core.services.staff_document_service import get_staff_stable_crud_service, \
    DocumentStatusType
from ..core.services.staff_service import get_staff_stable_busy_types_service


@bp.route("/staff_stable", methods=["GET", "POST"])
@login_required
async def staff_stable():
    form = StableStaffForm()
    working_date = (
        dt.date.fromisoformat(request.args.get("date"))
        if request.args.get("date")
        else dt.date.today()
    )
    staff_stable_service = get_staff_stable_crud_service()
    busy_types_service = get_staff_stable_busy_types_service()

    current_db_data = staff_stable_service.get(
        query_filter={"date": working_date.isoformat()}
    )
    if not current_db_data:
        result_info = staff_stable_service.make_blank_document(working_date)
        logging.info(
            f"Создан документ - строевая записка постоянного состава "
            f"за {working_date.isoformat()}. {result_info}"
        )
        current_db_data = staff_stable_service.get(
            query_filter={"date": working_date.isoformat()}
        )
    if request.method == "POST" and form.validate_on_submit():
        if request.form.get("finish_edit"):
            result = staff_stable_service.change_status(
                _id=current_db_data.get("_id"),
                status=DocumentStatusType.COMPLETED.value
            )
            logging.error(f"Изменен статус документа : {result}")
            return redirect(url_for("staff.staff_stable"))
        elif request.form.get("enable_edit"):
            staff_stable_service.change_status(
                _id=current_db_data.get("_id"),
                status=DocumentStatusType.IN_PROGRESS.value
            )
            return redirect(url_for("staff.staff_stable"))
        elif request.form.get("make_report"):
            busy_types = {item.slug: item.name for item in busy_types_service.list()}
            filename = generate_stable_staff_report(
                current_db_data, busy_types
            )
            return redirect(url_for("main.get_file", filename=filename))

    departments = await get_departments()
    staff_history = await check_api_db_response(
        await get_state_staff_history(working_date)
    )
    for staff in staff_history:
        dept_id = int(staff.get("department_id"))
        dept_data = departments[dept_id]
        if staff.get("vacancy_id") and staff.get("value") == "1":
            dept_data["staff_total"] = dept_data.get("staff_total", 0) + 1
    staff_data = {key: {} for key in Apeks.DEPT_TYPES.values()}

    for dept in sorted(departments, key=lambda d: departments[d].get("short")):
        dept_data = departments[dept]
        dept_type = dept_data.get("type")
        dept_cur_data = current_db_data["departments"].get(str(dept))
        dept_total = dept_data.get("staff_total", 0)
        dept_abscence = (
            sum(len(val) for val in dept_cur_data["absence"].values())
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
                "name": dept_data.get("short"),
                "staff_total": dept_total,
                "staff_absence": dept_abscence,
                "staff_stock": dept_stock,
            }

    return render_template(
        "staff/staff_stable.html",
        active="staff",
        form=form,
        date=working_date,
        staff_data=staff_data,
        doc_status=current_db_data.get("status"),
    )


@bp.route("/staff_stable_edit/<int:department_id>", methods=["GET", "POST"])
@login_required
async def staff_stable_edit(department_id):
    # mongo_db = get_mongo_db()
    # staff_db = mongo_db[MongoDBSettings.STAFF_STABLE_COLLECTION]
    # logs_db = mongo_db[MongoDBSettings.STAFF_LOGS_COLLECTION]
    busy_types_service = get_staff_stable_busy_types_service()

    working_date = (
        dt.date.fromisoformat(request.args.get("date"))
        if request.args.get("date")
        else dt.date.today()
    )

    staff_history = await check_api_db_response(
        await get_state_staff_history(working_date, department_id=department_id)
    )
    staff_ids = {
        item.get("staff_id"): item
        for item in staff_history
        if item.get("vacancy_id") and item.get("value") == "1"
    }

    departments = await get_departments()
    department_data = departments.get(int(department_id))
    department_name = department_data.get("short")
    department_type = department_data.get("type")

    state_staff = await get_state_staff(id=staff_ids.keys())

    state_staff_positions = data_processor(
        await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("state_staff_positions"))
        )
    )

    final_staff_data = []
    for staff_id, staff_hist in staff_ids.items():
        staff_id = staff_id
        position_id = int(staff_hist.get("position_id"))
        position = state_staff_positions.get(position_id)
        staff_data = state_staff.get(int(staff_id))

        final_staff_data.append(
            {
                "staff_id": staff_id,
                "name": staff_data.get("short"),
                "position": position.get("name"),
                "sort": position.get("sort"),
            }
        )

    final_staff_data.sort(key=lambda x: int(x["sort"]), reverse=True)

    busy_types = busy_types_service.list(is_active=1)

    form = create_staff_edit_form(staff_data=final_staff_data, busy_types=busy_types)

    current_db_data = staff_db.find_one({"date": working_date.isoformat()})

    if request.method == "POST" and form.validate_on_submit():
        if current_db_data.get("status") == FlaskConfig.STAFF_IN_PROGRESS_STATUS:
            load_data = {
                "id": department_id,
                "name": department_name,
                "type": department_type,
                "total": len(staff_ids),
                "absence": {item.slug: {} for item in busy_types},
                "user": current_user.username
                if isinstance(current_user, Users)
                else "anonymous",
                "updated": dt.datetime.now().isoformat(),
            }
            for _id in staff_ids:
                staff_absence = request.form.get(f"staff_id_{_id}")
                if staff_absence != "0" and staff_absence in load_data["absence"]:
                    load_data["absence"][staff_absence][_id] = state_staff[
                        int(_id)
                    ].get("short")
                elif staff_absence != "0" and staff_absence not in load_data["absence"]:
                    message = (
                        f"Форма вернула неизвестное местонахождение: {staff_absence}"
                    )
                    flash(message, category="danger")
                    logging.error(message)

            try:
                staff_db.update_one(
                    {"date": working_date.isoformat()},
                    {"$set": {f"departments.{department_id}": load_data}},
                    upsert=True,
                )
                current_db_data = staff_db.find_one({"date": working_date.isoformat()})
                load_data["edit_document_id"] = current_db_data.get('_id', None)
                logs_db.insert_one(load_data)
                message = (
                    f"Данные подразделения {department_name} за "
                    f"{working_date.isoformat()} успешно переданы"
                )
                flash(message, category="success")
                logging.info(message)
            except PyMongoError as error:
                message = f"Произошла ошибка записи данных: {error}"
                flash(message, category="danger")
                logging.error(message)
        else:
            message = f"Данные за {working_date.isoformat()} закрыты для редактирования"
            flash(message, category="danger")

    current_dept_data = current_db_data["departments"].get(str(department_id))
    if current_dept_data:
        for absence, items in current_dept_data["absence"].items():
            if items:
                for _id in items:
                    attr = getattr(form, f"staff_id_{_id}")
                    attr.data = absence

    return render_template(
        "staff/staff_stable_edit.html",
        active="staff",
        form=form,
        date=working_date,
        department=department_name,
        staff_data=final_staff_data,
        status=current_db_data.get("status"),
    )
