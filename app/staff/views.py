import copy
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
    StaffAllowedFacultyAddForm,
    StaffAllowedFacultyEditForm,
    StaffLoadForm,
    create_staff_stable_edit_form,
    StaffForm,
    StaffReportForm,
    StaffStableBusyTypesForm,
    create_staff_various_edit_form,
)
from .func import (
    make_short_name,
    process_apeks_stable_staff_data,
    process_apeks_various_group_data,
    process_document_various_staff_data,
    process_stable_staff_data,
    process_document_stable_staff_data,
    process_documents_range_by_busy_type,
    process_documents_range_by_staff_id,
    staff_various_groups_data_filter,
)
from .stable_staff_report import generate_stable_staff_report
from .various_staff_report import generate_various_staff_report, get_various_report_data
from ..auth.func import permission_required
from ..core.db.auth_models import Users
from ..core.forms import ObjectDeleteForm
from ..core.repository.sqlalchemy_repository import DbRepository
from ..core.services.apeks_db_load_groups_service import get_apeks_load_groups_service
from ..core.services.apeks_db_state_departments_service import (
    get_db_apeks_state_departments_service,
)
from ..core.services.apeks_db_state_staff_history_service import (
    get_db_apeks_state_staff_history_service,
)
from ..core.services.apeks_db_state_staff_positions_service import (
    get_apeks_db_state_staff_positions_service,
)
from ..core.services.apeks_db_state_staff_service import (
    get_apeks_db_state_staff_service,
    process_state_staff_data,
)
from ..core.services.apeks_db_state_vacancies_service import (
    get_apeks_db_state_vacancies_service,
)
from ..core.services.apeks_db_student_student_history_service import (
    get_apeks_student_student_history_service,
)
from ..core.services.apeks_db_student_students_groups_service import (
    get_apeks_student_students_groups_service,
)
from ..core.services.apeks_db_student_students_service import (
    get_apeks_student_students_service,
)
from ..core.services.apeks_schedule_schedule_student_service import (
    get_apeks_schedule_schedule_student_service,
)
from ..core.services.base_apeks_api_service import data_processor
from ..core.services.base_mongo_db_crud_service import VariousStaffDaytimeType
from ..core.services.db_staff_services import (
    get_staff_allowed_faculty_service,
    get_staff_stable_busy_types_service,
    get_staff_various_busy_types_service,
    get_staff_various_illness_types_service,
)
from ..core.services.staff_logs_document_service import get_staff_logs_crud_service
from ..core.services.staff_stable_document_service import (
    StaffStableDepartmentDocStructure,
    get_staff_stable_document_service,
    DocumentStatusType,
)
from ..core.services.staff_various_document_service import (
    StaffVariousGroupDocStructure,
    get_staff_various_document_service,
)


@bp.route("/staff_data_edit", methods=["GET"])
@permission_required(PermissionsConfig.STAFF_BUSY_TYPES_EDIT_PERMISSION)
@login_required
def staff_data_edit():
    data = {
        "Причины отсутствия постоянного состава": url_for(".staff_stable_busy_types"),
        "Факультеты для данных переменного состава": url_for(".staff_allowed_faculty"),
        "Причины отсутствия переменного состава": url_for(".staff_various_busy_types"),
        "Причины отсутствия переменного состава по болезни": url_for(
            ".staff_various_illness_types"
        ),
    }
    return render_template(
        "staff/staff_data_info.html",
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
        template_name="staff/staff_data_types.html",
        service=get_staff_stable_busy_types_service(),
        base_view_slug="staff_stable_busy_types",
    ),
)

bp.add_url_rule(
    "/staff_various_busy_types",
    view_func=StaffDataGetView.as_view(
        "staff_various_busy_types",
        title="Причины отсутствия переменного состава",
        template_name="staff/staff_data_types.html",
        service=get_staff_various_busy_types_service(),
        base_view_slug="staff_various_busy_types",
    ),
)

bp.add_url_rule(
    "/staff_various_illness_types",
    view_func=StaffDataGetView.as_view(
        "staff_various_illness_types",
        title="Причины отсутствия переменного состава по болезни",
        template_name="staff/staff_data_types.html",
        service=get_staff_various_illness_types_service(),
        base_view_slug="staff_various_illness_types",
    ),
)

bp.add_url_rule(
    "/staff_allowed_faculty",
    view_func=StaffDataGetView.as_view(
        "staff_allowed_faculty",
        title="Факультеты для подачи строевой записки",
        template_name="staff/staff_allowed_faculty.html",
        service=get_staff_allowed_faculty_service(),
        base_view_slug="staff_allowed_faculty",
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
            "staff/staff_data_types_edit.html",
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
        template_name="staff/staff_data_types_edit.html",
        service=get_staff_stable_busy_types_service(),
        base_view_slug="staff_stable_busy_types",
    ),
)

bp.add_url_rule(
    "/staff_various_busy_types_add",
    view_func=StaffDataAddView.as_view(
        "staff_various_busy_types_add",
        title="Причины отсутствия переменного состава",
        template_name="staff/staff_data_types_edit.html",
        service=get_staff_various_busy_types_service(),
        base_view_slug="staff_various_busy_types",
    ),
)

bp.add_url_rule(
    "/staff_various_illness_types_add",
    view_func=StaffDataAddView.as_view(
        "staff_various_illness_types_add",
        title="Причины отсутствия переменного состава по болезни",
        template_name="staff/staff_data_types_edit.html",
        service=get_staff_various_illness_types_service(),
        base_view_slug="staff_various_illness_types",
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
            "staff/staff_data_types_edit.html",
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
        template_name="staff/staff_data_types_edit.html",
        service=get_staff_stable_busy_types_service(),
        base_view_slug="staff_stable_busy_types",
    ),
)

bp.add_url_rule(
    "/staff_various_busy_types/<int:id_>",
    view_func=StaffDataEditView.as_view(
        "staff_various_busy_types_edit",
        title="Причина отсутствия переменного состава",
        template_name="staff/staff_data_types_edit.html",
        service=get_staff_various_busy_types_service(),
        base_view_slug="staff_various_busy_types",
    ),
)

bp.add_url_rule(
    "/staff_various_illness_types/<int:id_>",
    view_func=StaffDataEditView.as_view(
        "staff_various_illness_types_edit",
        title="Причина отсутствия переменного состава по болезни",
        template_name="staff/staff_data_types_edit.html",
        service=get_staff_various_illness_types_service(),
        base_view_slug="staff_various_illness_types",
    ),
)


@bp.route("/staff_allowed_faculty_add", methods=["GET", "POST"])
@permission_required(PermissionsConfig.STAFF_BUSY_TYPES_EDIT_PERMISSION)
@login_required
async def staff_allowed_faculty_add():
    student_service = get_apeks_schedule_schedule_student_service()
    apeks_groups_data = await student_service.get()
    form = StaffAllowedFacultyAddForm()
    form.apeks_id.choices = [
        (faculty.get("id"), faculty.get("name"))
        for faculty in apeks_groups_data["groups"].values()
    ]
    if request.method == "POST" and form.validate_on_submit():
        faculty_service = get_staff_allowed_faculty_service()
        faculty_dict = dict(form.apeks_id.choices)
        apeks_id = int(request.form.get("apeks_id"))
        name = faculty_dict.get(apeks_id)
        faculty_service.create(
            apeks_id=apeks_id,
            name=name,
            short_name=request.form.get("short_name"),
            sort=request.form.get("sort"),
        )
        flash(
            f"Запись {name} успешно добавлена",
            category="success",
        )
        return redirect(url_for(".staff_allowed_faculty"))
    return render_template(
        "staff/staff_allowed_faculty_add.html",
        active="staff",
        form=form,
    )


@bp.route("/staff_allowed_faculty_edit/<int:id_>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.STAFF_BUSY_TYPES_EDIT_PERMISSION)
@login_required
async def staff_allowed_faculty_edit(id_):
    faculty_service = get_staff_allowed_faculty_service()
    obj = faculty_service.get(id=id_)
    form = StaffAllowedFacultyEditForm(obj=obj)
    if request.method == "POST" and form.validate_on_submit():
        faculty_service.update(
            id_,
            apeks_id=obj.apeks_id,
            name=request.form.get("name"),
            short_name=request.form.get("short_name"),
            sort=request.form.get("sort"),
        )
        flash(
            f"Запись {obj.name} успешно обновлена",
            category="success",
        )
        return redirect(url_for(".staff_allowed_faculty"))
    return render_template(
        "staff/staff_allowed_faculty_edit.html",
        active="staff",
        form=form,
    )


@bp.route("/staff_allowed_faculty_delete/<int:id_>", methods=["GET", "POST"])
@permission_required(PermissionsConfig.STAFF_BUSY_TYPES_EDIT_PERMISSION)
@login_required
async def staff_allowed_faculty_delete(id_):
    faculty_service = get_staff_allowed_faculty_service()
    obj = faculty_service.get(id=id_)
    form = ObjectDeleteForm()
    if request.method == "POST" and form.validate_on_submit():
        faculty_service.delete(obj.id)
        flash(
            f"Запись {obj.name} успешно удалена",
            category="success",
        )
        return redirect(url_for(".staff_allowed_faculty"))
    return render_template(
        "staff/staff_allowed_faculty_delete.html",
        active="staff",
        obj_data=obj,
        form=form,
    )


@bp.route("/staff_info", methods=["GET", "POST"])
@login_required
async def staff_info():
    form = StaffForm()
    current_date = request.form.get("document_date") or dt.date.today().isoformat()
    staff_stable_service = get_staff_stable_document_service()
    staff_stable_document = staff_stable_service.get(
        query_filter={"date": current_date}
    )
    stable_busy_types_service = get_staff_stable_busy_types_service()
    stable_busy_types = {
        item.slug: item.name for item in stable_busy_types_service.list()
    }
    document_stable_status = (
        MongoDBSettings.STAFF_COLLECTION_STATUSES.get(
            staff_stable_document.get("status")
        )
        if staff_stable_document
        else None
    )
    staff_stable_data = process_document_stable_staff_data(staff_stable_document)
    if current_date == dt.date.today().isoformat() and staff_stable_document:
        departments_service = get_db_apeks_state_departments_service()
        departments = await departments_service.get_departments()
        staff_history_service = get_db_apeks_state_staff_history_service()
        staff_history = data_processor(
            await staff_history_service.get_staff_for_date(dt.date.today()),
            key="staff_id",
        )
        state_vacancies_service = get_apeks_db_state_vacancies_service()
        state_vacancies = data_processor(await state_vacancies_service.list())
        stable_data = process_apeks_stable_staff_data(
            departments,
            staff_history,
            staff_stable_document,
            state_vacancies,
        )
        military_data = {
            "staff_military_total": 0,
            "staff_military_absence": 0,
            "staff_military_stock": 0,
        }
        for dept_type in stable_data:
            for dept in stable_data[dept_type]:
                if all(
                    isinstance(stable_data[dept_type][dept].get(item_name), int)
                    for item_name in military_data
                ):
                    for item_name in military_data:
                        military_data[item_name] += stable_data[dept_type][dept].get(
                            item_name
                        )
    else:
        military_data = None
    staff_various_service = get_staff_various_document_service()
    various_documents = {
        daytime.value: process_document_various_staff_data(
            staff_various_service.get(
                query_filter={"date": current_date, "daytime": daytime}
            )
        )
        for daytime in VariousStaffDaytimeType
    }
    return render_template(
        "staff/staff_info.html",
        active="staff",
        form=form,
        date=current_date,
        stable_busy_types=stable_busy_types,
        department_types=ApeksConfig.DEPT_TYPES.values(),
        staff_stable_data=staff_stable_data,
        document_stable_status=document_stable_status,
        various_documents=various_documents,
        military_data=military_data,
    )


@bp.route("/staff_stable_file_report/<string:date>", methods=["GET"])
@login_required
async def staff_stable_file_report(date):
    staff_stable_service = get_staff_stable_document_service()
    document_data = staff_stable_service.get(
        query_filter={"date": date}
    )
    stable_busy_types_service = get_staff_stable_busy_types_service()
    busy_types = {item.slug: item.name for item in stable_busy_types_service.list()}
    filename = generate_stable_staff_report(document_data, busy_types)
    return redirect(url_for("main.get_file", filename=filename))


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
    form = StaffLoadForm()
    working_date = (
        dt.date.fromisoformat(request.args.get("date"))
        if request.args.get("date")
        else dt.date.today()
    )
    staff_stable_service = get_staff_stable_document_service()
    document_data = staff_stable_service.get(
        query_filter={"date": working_date.isoformat()}
    )
    if not document_data:
        staff_stable_service.make_blank_document(working_date)
        document_data = staff_stable_service.get(
            query_filter={"date": working_date.isoformat()}
        )
    if request.method == "POST" and form.validate_on_submit():
        if request.form.get("finish_edit"):
            result = staff_stable_service.change_status(
                _id=document_data.get("_id"),
                status=DocumentStatusType.COMPLETED.value,
            )
            logging.info(
                f"{current_user} запретил редактирование "
                f"документа {working_date.isoformat()}: {result}"
            )
            return redirect(url_for("staff.staff_stable_load"))
        elif request.form.get("enable_edit"):
            result = staff_stable_service.change_status(
                _id=document_data.get("_id"),
                status=DocumentStatusType.IN_PROGRESS.value,
            )
            logging.info(
                f"{current_user} разрешил редактирование "
                f"документа {working_date.isoformat()}: {result}"
            )
            return redirect(url_for("staff.staff_stable_load"))
    departments_service = get_db_apeks_state_departments_service()
    departments = await departments_service.get_departments()
    staff_history_service = get_db_apeks_state_staff_history_service()
    staff_history = data_processor(
        await staff_history_service.get_staff_for_date(working_date), key="staff_id"
    )
    state_vacancies_service = get_apeks_db_state_vacancies_service()
    state_vacancies = data_processor(await state_vacancies_service.list())
    staff_data = process_apeks_stable_staff_data(
        departments, staff_history, document_data, state_vacancies
    )
    return render_template(
        "staff/staff_stable_load.html",
        active="staff",
        form=form,
        date=working_date,
        staff_data=staff_data,
        doc_status=document_data.get("status"),
    )


@bp.route("/staff_stable_edit/<string:department_id>", methods=["GET", "POST"])
@login_required
async def staff_stable_edit(department_id):
    working_date = (
        dt.date.fromisoformat(request.args.get("date"))
        if request.args.get("date")
        else dt.date.today()
    )
    staff_history_service = get_db_apeks_state_staff_history_service()
    staff_history = await staff_history_service.get_staff_for_date(
        working_date, department_id=department_id
    )
    # Отбираем тех кто стоит на должности со ставкой 1
    staff_ids = {
        item.get("staff_id"): item
        for item in staff_history
        if item.get("vacancy_id") and item.get("value") == "1"
    }
    departments_service = get_db_apeks_state_departments_service()
    departments = await departments_service.get_departments()
    department_data = departments.get(department_id)
    department_name = department_data.get("short")
    department_type = department_data.get("type")
    state_staff_service = get_apeks_db_state_staff_service()
    state_staff = process_state_staff_data(
        await state_staff_service.get(id=staff_ids.keys())
    )
    state_staff_positions_service = get_apeks_db_state_staff_positions_service()
    state_staff_positions = data_processor(await state_staff_positions_service.list())
    full_staff_data = process_stable_staff_data(
        staff_ids, state_staff_positions, state_staff
    )
    busy_types_service = get_staff_stable_busy_types_service()
    busy_types = busy_types_service.list(is_active=1)
    form = create_staff_stable_edit_form(
        staff_data=full_staff_data, busy_types=busy_types
    )
    staff_stable_service = get_staff_stable_document_service()
    document_data = staff_stable_service.get({"date": working_date.isoformat()})
    if request.method == "POST" and form.validate_on_submit():
        if document_data.get("status") == MongoDBSettings.STAFF_IN_PROGRESS_STATUS:
            dept_document = StaffStableDepartmentDocStructure(
                id=department_id,
                name=department_name,
                type=department_type,
                total=len(staff_ids),
                absence={item.slug: {} for item in busy_types},
                user=(
                    current_user.username
                    if isinstance(current_user, Users)
                    else "anonymous"
                ),
                updated=dt.datetime.now().isoformat(),
            )
            for _id in staff_ids:
                staff_absence = request.form.get(f"staff_id_{_id}")
                if staff_absence != "0" and staff_absence in dept_document.absence:
                    dept_document.absence[staff_absence][_id] = state_staff[_id].get(
                        "short"
                    )
                elif (
                    staff_absence != "0" and staff_absence not in dept_document.absence
                ):
                    message = (
                        f"Форма вернула неизвестное местонахождение: {staff_absence}"
                    )
                    flash(message, category="danger")
                    logging.error(message)
            try:
                staff_stable_service.update(
                    {"date": working_date.isoformat()},
                    {"$set": {f"departments.{department_id}": dept_document.__dict__}},
                    upsert=True,
                )
                document_data = staff_stable_service.get(
                    {"date": working_date.isoformat()}
                )
                dept_document.edit_document_id = document_data.get("_id", None)
                staff_logs_service = get_staff_logs_crud_service()
                staff_logs_service.create(dept_document.__dict__)
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

    # Заполняем форму имеющимися данными
    current_dept_data = document_data["departments"].get(department_id)
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
        status=document_data.get("status"),
    )


@bp.route("/staff_various_load", methods=["GET", "POST"])
@login_required
async def staff_various_load():
    form = StaffLoadForm()
    working_date = (
        dt.date.fromisoformat(request.args.get("date"))
        if request.args.get("date")
        else dt.date.today()
    )
    daytime = request.args.get("daytime")
    if daytime:
        try:
            daytime = VariousStaffDaytimeType(request.args.get("daytime"))
        except ValueError:
            flash(f"Передан неверный параметр времени - {daytime}", category="danger")
    else:
        daytime = VariousStaffDaytimeType(MongoDBSettings.DAYTIME_MORNING)
    staff_various_service = get_staff_various_document_service()
    document_data = staff_various_service.get(
        query_filter={"date": working_date.isoformat(), "daytime": daytime}
    )
    if not document_data:
        staff_various_service.make_blank_document(working_date)
        document_data = staff_various_service.get(
            query_filter={"date": working_date.isoformat()}
        )
    allowed_faculty_service = get_staff_allowed_faculty_service()
    student_service = get_apeks_schedule_schedule_student_service()
    groups_data = staff_various_groups_data_filter(
        await student_service.get(), allowed_faculty_service.list()
    )
    groups_data = process_apeks_various_group_data(groups_data, document_data)
    if request.method == "POST" and form.validate_on_submit():
        if request.form.get("finish_edit"):
            result = staff_various_service.change_status(
                _id=document_data.get("_id"),
                status=DocumentStatusType.COMPLETED.value,
            )
            logging.info(
                f"{current_user} запретил редактирование "
                f"документа {working_date.isoformat()}: {result}"
            )
            return redirect(
                url_for(
                    "staff.staff_various_load", date=working_date, daytime=daytime.value
                )
            )
        elif request.form.get("enable_edit"):
            result = staff_various_service.change_status(
                _id=document_data.get("_id"),
                status=DocumentStatusType.IN_PROGRESS.value,
            )
            logging.info(
                f"{current_user} разрешил редактирование "
                f"документа {working_date.isoformat()}: {result}"
            )
            return redirect(
                url_for(
                    "staff.staff_various_load", date=working_date, daytime=daytime.value
                )
            )
    return render_template(
        "staff/staff_various_load.html",
        active="staff",
        form=form,
        date=working_date,
        daytime=daytime.value,
        groups_data=groups_data,
        doc_status=document_data.get("status"),
    )


@bp.route(
    "/staff_various_edit/<string:daytime>/<string:group_id>/<string:course>",
    methods=["GET", "POST"],
)
@login_required
async def staff_various_edit(daytime, group_id, course):
    working_date = (
        dt.date.fromisoformat(request.args.get("date"))
        if request.args.get("date")
        else dt.date.today()
    )
    try:
        daytime = VariousStaffDaytimeType(daytime)
    except ValueError:
        flash(f"Передан неверный параметр времени - {daytime}", category="danger")
        return redirect(url_for("staff.staff_various_load"))
    group_service = get_apeks_load_groups_service()
    group_data = await group_service.get(id=group_id)
    if group_data:
        group_data = group_data[-1]
    students_group_service = get_apeks_student_students_groups_service()
    group_students = data_processor(
        await students_group_service.get(group_id=group_id),
        key="student_id",
    )
    students_service = get_apeks_student_students_service()
    students_data = await students_service.get(id=group_students)
    students_data = sorted(students_data, key=lambda x: x.get("family_name"))
    student_history_service = get_apeks_student_student_history_service()
    fired_students = [
        student.get("student_id")
        for student in await student_history_service.get(
            student_id=group_students.keys(),
            type=ApeksConfig.STUDENT_HISTORY_RECORD_TYPES.keys(),
            group_id=group_id,
        )
    ]
    students_data = [
        student for student in students_data if student.get("id") not in fired_students
    ]
    for student in students_data:
        student["short_name"] = make_short_name(
            student.get("family_name"), student.get("name"), student.get("surname")
        )

    busy_types_service = get_staff_various_busy_types_service()
    busy_types = busy_types_service.list(is_active=1)
    illness_types_service = get_staff_various_illness_types_service()
    illness_types = illness_types_service.list(is_active=1)
    faculty_service = get_staff_allowed_faculty_service()
    faculty = faculty_service.get(apeks_id=group_data.get("department_id"))
    faculty_name = faculty.short_name if faculty else group_data.get("department_id")
    form = create_staff_various_edit_form(
        students_data=students_data, busy_types=busy_types, illness_types=illness_types
    )
    staff_various_service = get_staff_various_document_service()
    document_data = staff_various_service.get(
        {"date": working_date.isoformat(), "daytime": daytime}
    )

    if request.method == "POST" and form.validate_on_submit():
        if document_data.get("status") == MongoDBSettings.STAFF_IN_PROGRESS_STATUS:
            dept_document = StaffVariousGroupDocStructure(
                id=group_id,
                name=group_data.get("name"),
                type="Учебная группа",
                daytime=daytime.value,
                faculty=faculty_name,
                course=course,
                total=len(students_data),
                absence={item.slug: {} for item in busy_types},
                absence_illness={item.slug: {} for item in illness_types},
                user=(
                    current_user.username
                    if isinstance(current_user, Users)
                    else "anonymous"
                ),
                updated=dt.datetime.now().isoformat(),
            )
            for student in students_data:
                _id = student.get("id")
                student_absence = request.form.get(f"student_id_{_id}")
                if student_absence != "0":
                    if student_absence in dept_document.absence:
                        dept_document.absence[student_absence][_id] = student.get(
                            "short_name"
                        )
                    elif student_absence in dept_document.absence_illness:
                        dept_document.absence_illness[student_absence][_id] = (
                            student.get("short_name")
                        )
                    else:
                        message = f"Форма вернула неизвестное местонахождение: {student_absence}"
                        flash(message, category="danger")
                        logging.error(message)
            try:
                documents = [dept_document]
                if request.form.get("switch_copy_day"):
                    day_doc = copy.deepcopy(dept_document)
                    day_doc.daytime = VariousStaffDaytimeType(
                        MongoDBSettings.DAYTIME_DAY
                    )
                    documents.append(day_doc)
                if request.form.get("switch_copy_evening"):
                    evening_doc = copy.deepcopy(dept_document)
                    evening_doc.daytime = VariousStaffDaytimeType(
                        MongoDBSettings.DAYTIME_EVENING
                    )
                    documents.append(evening_doc)
                for document in documents[::-1]:
                    staff_various_service.update(
                        {"date": working_date.isoformat(), "daytime": document.daytime},
                        {"$set": {f"groups.{group_id}": document.__dict__}},
                        upsert=True,
                    )
                    document_data = staff_various_service.get(
                        {"date": working_date.isoformat(), "daytime": document.daytime}
                    )
                    document.edit_document_id = document_data.get("_id", None)
                    staff_logs_service = get_staff_logs_crud_service()
                    staff_logs_service.create(document.__dict__)
                    message = (
                        f"Данные группы {group_data.get('name')} за {working_date.isoformat()} "
                        f'"{MongoDBSettings.DAYTIME_NAME.get(document.daytime)}" успешно переданы'
                    )
                    flash(message, category="success")
                    logging.info(message)
            except PyMongoError as error:
                message = f"Произошла ошибка записи данных: {error}"
                flash(message, category="danger")
                logging.error(message)
        else:
            message = (
                f"Данные за {working_date.isoformat()} "
                f'"{MongoDBSettings.DAYTIME_NAME.get(daytime)}" закрыты для редактирования'
            )
            flash(message, category="danger")

    # Заполняем форму имеющимися данными
    current_group_data = document_data["groups"].get(group_id)
    if current_group_data:
        for absence, items in current_group_data["absence"].items():
            if items:
                for _id in items:
                    attr = getattr(form, f"student_id_{_id}")
                    attr.data = absence
        for illness, items in current_group_data["absence_illness"].items():
            if items:
                for _id in items:
                    attr = getattr(form, f"student_id_{_id}")
                    attr.data = illness

    return render_template(
        "staff/staff_various_edit.html",
        active="staff",
        form=form,
        date=working_date,
        daytime=daytime.value,
        group=group_data.get("name"),
        students_data=enumerate(students_data, start=1),
        status=document_data.get("status"),
    )


@bp.route(
    "/staff_various_file_report/<string:date>/<string:daytime>",
    methods=["GET"],
)
@login_required
async def staff_various_file_report(date, daytime):
    staff_various_service = get_staff_various_document_service()
    document_data = staff_various_service.get(
        query_filter={"date": date, "daytime": daytime}
    )
    allowed_faculty_service = get_staff_allowed_faculty_service()
    busy_types_service = get_staff_various_busy_types_service()
    busy_types = {item.slug: item.name for item in busy_types_service.list()}
    illness_types_service = get_staff_various_illness_types_service()
    illness_types = {
        item.slug: item.name for item in illness_types_service.list()
    }
    faculty_data = {
        item.short_name: item.sort for item in allowed_faculty_service.list()
    }
    report_data = get_various_report_data(document_data, faculty_data)
    filename = generate_various_staff_report(
        report_data, busy_types, illness_types
    )
    return redirect(url_for("main.get_file", filename=filename))
