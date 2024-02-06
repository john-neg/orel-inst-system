import datetime
import datetime as dt
import logging
from dataclasses import dataclass

from flask import render_template, request, url_for, flash
from flask.views import View
from flask_login import login_required, current_user
from pymongo.errors import PyMongoError
from werkzeug.utils import redirect

from config import ApeksConfig, MongoDBSettings, PermissionsConfig
from . import bp
from .forms import (
    StableStaffForm,
    create_staff_edit_form,
    StaffForm,
    StaffReportForm,
    StaffStableBusyTypesForm,
)
from .func import (
    process_apeks_stable_staff_data,
    process_full_staff_data,
    process_document_stable_staff_data,
    process_documents_range_by_busy_type,
    process_documents_range_by_staff_id,
)
from .stable_staff_report import generate_stable_staff_report
from ..auth.func import permission_required
from ..core.db.auth_models import Users
from ..core.repository.sqlalchemy_repository import DbRepository
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
    get_staff_stable_document_service,
    DocumentStatusType,
)


@bp.route("/staff_stable_info", methods=["GET", "POST"])
@login_required
async def staff_stable_info():
    form = StaffForm()
    current_date = request.form.get("document_date") or dt.date.today().isoformat()
    staff_stable_service = get_staff_stable_document_service()
    staff_stable_document = staff_stable_service.get(
        query_filter={"date": current_date}
    )
    busy_types_service = get_staff_stable_busy_types_service()
    busy_types = {item.slug: item.name for item in busy_types_service.list()}
    document_status = (
        MongoDBSettings.STAFF_COLLECTION_STATUSES.get(staff_stable_document.get("status"))
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


@bp.route("/staff_stable_report", methods=["GET"])
@permission_required(PermissionsConfig.STAFF_REPORT_PERMISSION)
@login_required
async def staff_stable_report():
    form = StaffReportForm()
    busy_data, staff_data, total_docs = None, None, None
    document_start_date = request.args.get("document_start_date")
    document_end_date = request.args.get("document_end_date")
    if document_start_date and document_end_date:
        staff_stable_service = get_staff_stable_document_service()
        staff_stable_documents = list(
            staff_stable_service.list(
                {
                    "date": {"$gte": document_start_date, "$lte": document_end_date},
                    "status": MongoDBSettings.STAFF_COMPLETED_STATUS,
                }
            )
        )
        total_docs = len(staff_stable_documents)
        busy_data = process_documents_range_by_busy_type(staff_stable_documents)
        staff_data = process_documents_range_by_staff_id(staff_stable_documents)
        form.document_start_date.data = datetime.date.fromisoformat(document_start_date)
        form.document_end_date.data = datetime.date.fromisoformat(document_end_date)

    busy_types_service = get_staff_stable_busy_types_service()
    busy_types = {item.slug: item.name for item in busy_types_service.list()}

    busy_type = request.args.get("busy_type")
    staff_id = request.args.get("staff_id")

    return render_template(
        "staff/staff_stable_report.html",
        active="staff",
        form=form,
        document_start_date=document_start_date,
        document_end_date=document_end_date,
        busy_data=busy_data,
        busy_types=busy_types,
        busy_type=busy_type,
        staff_data=staff_data,
        staff_id=staff_id,
        total_docs=total_docs,
    )


@bp.route("/staff_stable_load", methods=["GET", "POST"])
@login_required
async def staff_stable_load():
    form = StableStaffForm()
    working_date = (
        dt.date.fromisoformat(request.args.get("date"))
        if request.args.get("date")
        else dt.date.today()
    )
    staff_stable_service = get_staff_stable_document_service()
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
    staff_stable_service = get_staff_stable_document_service()
    current_data = staff_stable_service.get({"date": working_date.isoformat()})
    if request.method == "POST" and form.validate_on_submit():
        if current_data.get("status") == MongoDBSettings.STAFF_IN_PROGRESS_STATUS:
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


@bp.route("/staff_data_edit", methods=["GET"])
@permission_required(PermissionsConfig.STAFF_BUSY_TYPES_EDIT_PERMISSION)
@login_required
def staff_data_edit():
    data = {
        "Причины отсутствия постоянного состава": url_for(".staff_stable_busy_types"),
    }
    return render_template(
        "staff/staff_data_edit.html",
        title="Редактировать информацию",
        data=data,
    )


@dataclass
class StaffDataGetView(View):
    """View класс для просмотра списка записей."""

    template_name: str
    title: str
    service: DbRepository
    methods = ["GET", "POST"]
    base_view_slug: str

    @permission_required(PermissionsConfig.STAFF_BUSY_TYPES_EDIT_PERMISSION)
    @login_required
    async def dispatch_request(self):
        paginated_data = self.service.paginated()
        return render_template(
            self.template_name,
            title=self.title,
            paginated_data=paginated_data,
            base_view_slug=self.base_view_slug,
        )


bp.add_url_rule(
    "/staff_stable_busy_types",
    view_func=StaffDataGetView.as_view(
        "staff_stable_busy_types",
        title="Причины отсутствия постоянного состава",
        template_name="staff/staff_busy_types.html",
        service=get_staff_stable_busy_types_service(),
        base_view_slug="staff_stable_busy_types",
    ),
)


@dataclass
class StaffDataAddView(View):
    """View класс для добавления записей."""

    template_name: str
    title: str
    service: DbRepository
    methods = ["GET", "POST"]
    base_view_slug: str

    @permission_required(PermissionsConfig.STAFF_BUSY_TYPES_EDIT_PERMISSION)
    @login_required
    async def dispatch_request(self):
        form = StaffStableBusyTypesForm()
        if request.method == "POST" and form.validate_on_submit():
            self.service.create(
                slug=request.form.get("slug"),
                name=request.form.get("name"),
                is_active=True if request.form.get("is_active") else False,
            )
            flash("Запись успешно добавлена", category="success")
            return redirect(url_for(f".{self.base_view_slug}"))
        return render_template(
            "staff/staff_busy_types_edit.html",
            title=f'Добавить запись в "{self.title}"',
            base_view_slug=self.base_view_slug,
            slug_edit_disable=False,
            form=form,
        )


bp.add_url_rule(
    "/staff_stable_busy_types_add",
    view_func=StaffDataAddView.as_view(
        "staff_stable_busy_types_add",
        title="Причины отсутствия постоянного состава",
        template_name="staff/staff_busy_types_edit.html",
        service=get_staff_stable_busy_types_service(),
        base_view_slug="staff_stable_busy_types",
    ),
)


@dataclass
class StaffDataEditView(View):
    """View класс для изменения записей."""

    template_name: str
    title: str
    service: DbRepository
    methods = ["GET", "POST"]
    base_view_slug: str

    @permission_required(PermissionsConfig.STAFF_BUSY_TYPES_EDIT_PERMISSION)
    @login_required
    async def dispatch_request(self, id_: int):
        obj = self.service.get(id=id_)
        form = StaffStableBusyTypesForm(obj=obj)
        if request.method == "POST" and form.validate_on_submit():
            name = request.form.get("name")
            self.service.update(
                id_,
                name=name,
                is_active=True if request.form.get("is_active") else False,
            )
            flash(f"Данные {name} обновлены", category="success")
            return redirect(url_for(f".{self.base_view_slug}"))

        return render_template(
            "staff/staff_busy_types_edit.html",
            title=f"Изменить - {obj.name.lower()}",
            base_view_slug=self.base_view_slug,
            slug_edit_disable=True,
            form=form,
        )


bp.add_url_rule(
    "/staff_stable_busy_types/<int:id_>",
    view_func=StaffDataEditView.as_view(
        "staff_stable_busy_types_edit",
        title="Причина отсутствия постоянного состава",
        template_name="staff/staff_busy_types_edit.html",
        service=get_staff_stable_busy_types_service(),
        base_view_slug="staff_stable_busy_types",
    ),
)
