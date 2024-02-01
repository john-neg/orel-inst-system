import datetime
import datetime as dt
import logging

from flask import render_template, request, url_for, flash
from flask_login import login_required, current_user
from pymongo.errors import PyMongoError
from werkzeug.utils import redirect

from config import FlaskConfig, ApeksConfig
from . import bp
from .forms import StableStaffForm, create_staff_edit_form, StaffForm, \
    StableStaffReportForm
from .func import (
    process_apeks_stable_staff_data,
    process_full_staff_data,
    process_document_stable_staff_data, process_documents_range_by_busy_type,
    process_documents_range_by_staff_id,
)
from .stable_staff_report import generate_stable_staff_report
from ..core.db.auth_models import Users
from ..core.services.apeks_state_departments_service import (
    get_apeks_state_departments_service,
)
from ..core.services.apeks_state_staff_history_service import (
    get_apeks_state_staff_history_service,
)
from ..core.services.apeks_state_staff_positions_service import (
    get_apeks_state_staff_positions_service,
)
from ..core.services.apeks_state_staff_service import (
    get_apeks_state_staff_service,
    process_state_staff_data,
)
from ..core.services.base_apeks_api_service import data_processor
from ..core.services.db_staff_service import get_staff_stable_busy_types_service
from ..core.services.staff_logs_document_service import get_staff_logs_crud_service
from ..core.services.staff_stable_document_service import (
    get_staff_stable_crud_service,
    DocumentStatusType,
)


@bp.route("/staff_stable_info", methods=["GET", "POST"])
@login_required
async def staff_stable_info():
    form = StaffForm()
    current_date = request.form.get("document_date") or dt.date.today().isoformat()
    staff_stable_service = get_staff_stable_crud_service()
    staff_stable_document = staff_stable_service.get(
        query_filter={"date": current_date}
    )
    busy_types_service = get_staff_stable_busy_types_service()
    busy_types = {item.slug: item.name for item in busy_types_service.list()}
    document_status = (
        FlaskConfig.STAFF_COLLECTION_STATUSES.get(staff_stable_document.get("status"))
        if staff_stable_document
        else None
    )
    staff_stable_data = process_document_stable_staff_data(staff_stable_document)
    if request.method == "POST" and form.validate_on_submit():
        if request.form.get("make_report"):
            filename = generate_stable_staff_report(staff_stable_document, busy_types)
            return redirect(url_for("main.get_file", filename=filename))
    return render_template(
        "staff/staff_stable_info.html",
        active="staff",
        form=form,
        date=current_date,
        busy_types=busy_types,
        department_types=ApeksConfig.DEPT_TYPES.values(),
        staff_stable_data=staff_stable_data,
        document_status=document_status,
    )


@bp.route("/staff_stable_report", methods=["GET", "POST"])
@login_required
async def staff_stable_report():
    form = StableStaffReportForm()
    busy_data, staff_data = None, None
    # form.document_start_date.data = request.form.get("document_start_date")
    # form.document_end_date.data = datetime.date.today()

    if request.method == "POST" and form.validate_on_submit():
        start_date = request.form.get("document_start_date")
        end_date = request.form.get("document_end_date")
        staff_stable_service = get_staff_stable_crud_service()
        staff_stable_documents = list(
            staff_stable_service.list(
                {
                    "date": {'$gte': start_date, "$lte": end_date},
                    "status": FlaskConfig.STAFF_COMPLETED_STATUS
                }
            )
        )
        busy_data = process_documents_range_by_busy_type(staff_stable_documents)
        staff_data = process_documents_range_by_staff_id(staff_stable_documents)

    busy_types_service = get_staff_stable_busy_types_service()
    busy_types = {item.slug: item.name for item in busy_types_service.list()}

    busy_type = request.args.get("busy_type")
    staff_id = request.args.get("staff_id")

    return render_template(
        "staff/staff_stable_report.html",
        active="staff",
        form=form,
        busy_data=busy_data,
        staff_data=staff_data,
        busy_types=busy_types,
        busy_type=busy_type,
        staff_id=staff_id,
    )
    # return render_template(
    #     "staff/staff_stable_report.html",
    #     active="staff",
    #     form=form,
    # )


@bp.route("/staff_stable_load", methods=["GET", "POST"])
@login_required
async def staff_stable_load():
    form = StableStaffForm()
    working_date = (
        dt.date.fromisoformat(request.args.get("date"))
        if request.args.get("date")
        else dt.date.today()
    )
    staff_stable_service = get_staff_stable_crud_service()
    busy_types_service = get_staff_stable_busy_types_service()
    current_data = staff_stable_service.get(
        query_filter={"date": working_date.isoformat()}
    )
    if not current_data:
        staff_stable_service.make_blank_document(working_date)
        current_data = staff_stable_service.get(
            query_filter={"date": working_date.isoformat()}
        )
    if request.method == "POST" and form.validate_on_submit():
        if request.form.get("finish_edit"):
            result = staff_stable_service.change_status(
                _id=current_data.get("_id"),
                status=DocumentStatusType.COMPLETED.value,
            )
            logging.info(
                f"{current_user} запретил редактирование "
                f"документа {working_date.isoformat()}: {result}"
            )
            return redirect(url_for("staff.staff_stable_load"))
        elif request.form.get("enable_edit"):
            result = staff_stable_service.change_status(
                _id=current_data.get("_id"),
                status=DocumentStatusType.IN_PROGRESS.value,
            )
            logging.info(
                f"{current_user} разрешил редактирование "
                f"документа {working_date.isoformat()}: {result}"
            )
            return redirect(url_for("staff.staff_stable_load"))
        elif request.form.get("make_report"):
            busy_types = {item.slug: item.name for item in busy_types_service.list()}
            filename = generate_stable_staff_report(current_data, busy_types)
            return redirect(url_for("main.get_file", filename=filename))
    departments_service = get_apeks_state_departments_service()
    departments = await departments_service.get_departments()
    staff_history_service = get_apeks_state_staff_history_service()
    staff_history = await staff_history_service.get_staff_for_date(working_date)
    staff_data = process_apeks_stable_staff_data(
        departments, staff_history, current_data
    )
    return render_template(
        "staff/staff_stable_load.html",
        active="staff",
        form=form,
        date=working_date,
        staff_data=staff_data,
        doc_status=current_data.get("status"),
    )


@bp.route("/staff_stable_edit/<string:department_id>", methods=["GET", "POST"])
@login_required
async def staff_stable_edit(department_id):
    working_date = (
        dt.date.fromisoformat(request.args.get("date"))
        if request.args.get("date")
        else dt.date.today()
    )
    staff_history_service = get_apeks_state_staff_history_service()
    staff_history = await staff_history_service.get_staff_for_date(
        working_date, department_id=department_id
    )
    # Отбираем тех кто стоит на должности со ставкой 1
    staff_ids = {
        item.get("staff_id"): item
        for item in staff_history
        if item.get("vacancy_id") and item.get("value") == "1"
    }
    departments_service = get_apeks_state_departments_service()
    departments = await departments_service.get_departments()
    department_data = departments.get(department_id)
    department_name = department_data.get("short")
    department_type = department_data.get("type")
    state_staff_service = get_apeks_state_staff_service()
    state_staff = process_state_staff_data(
        await state_staff_service.get(id=staff_ids.keys())
    )
    state_staff_positions_service = get_apeks_state_staff_positions_service()
    state_staff_positions = data_processor(await state_staff_positions_service.list())
    full_staff_data = process_full_staff_data(
        staff_ids, state_staff_positions, state_staff
    )
    busy_types_service = get_staff_stable_busy_types_service()
    busy_types = busy_types_service.list(is_active=1)
    form = create_staff_edit_form(staff_data=full_staff_data, busy_types=busy_types)
    staff_stable_service = get_staff_stable_crud_service()
    current_data = staff_stable_service.get({"date": working_date.isoformat()})
    if request.method == "POST" and form.validate_on_submit():
        if current_data.get("status") == FlaskConfig.STAFF_IN_PROGRESS_STATUS:
            load_data = {
                "id": department_id,
                "name": department_name,
                "type": department_type,
                "total": len(staff_ids),
                "absence": {item.slug: {} for item in busy_types},
                "user": (
                    current_user.username
                    if isinstance(current_user, Users)
                    else "anonymous"
                ),
                "updated": dt.datetime.now().isoformat(),
            }
            for _id in staff_ids:
                staff_absence = request.form.get(f"staff_id_{_id}")
                if staff_absence != "0" and staff_absence in load_data["absence"]:
                    load_data["absence"][staff_absence][_id] = state_staff[_id].get(
                        "short"
                    )
                elif staff_absence != "0" and staff_absence not in load_data["absence"]:
                    message = (
                        f"Форма вернула неизвестное местонахождение: {staff_absence}"
                    )
                    flash(message, category="danger")
                    logging.error(message)
            try:
                staff_stable_service.update(
                    {"date": working_date.isoformat()},
                    {"$set": {f"departments.{department_id}": load_data}},
                    upsert=True,
                )
                current_data = staff_stable_service.get(
                    {"date": working_date.isoformat()}
                )
                load_data["edit_document_id"] = current_data.get("_id", None)
                staff_logs_service = get_staff_logs_crud_service()
                staff_logs_service.create(load_data)
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
    current_dept_data = current_data["departments"].get(department_id)
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
        staff_data=full_staff_data,
        status=current_data.get("status"),
    )
