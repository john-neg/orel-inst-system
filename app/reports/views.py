import logging
from dataclasses import dataclass
from datetime import date

from flask import render_template, request, url_for, flash
from flask.views import View
from flask_login import login_required
from werkzeug.utils import redirect

from config import ApeksConfig, PermissionsConfig
from . import bp
from .forms import LoadReportForm, HolidaysReportForm, ProductionCalendarForm
from ..auth.func import permission_required
from ..core.classes.EducationStaff import EducationStaff
from ..core.classes.LoadReportProcessor import LoadReportProcessor
from ..core.db.database import db
from ..core.db.reports_models import (
    ProductionCalendarHolidays,
    ProductionCalendarWorkingDays,
)
from ..core.forms import ObjectDeleteForm
from ..core.func.api_get import check_api_db_response, api_get_db_table, get_lessons
from ..core.func.organization import get_departments
from ..core.func.staff import get_state_staff
from ..core.reports.holidays_report import generate_holidays_report
from ..core.reports.load_report import generate_load_report
from ..core.repository.sqlalchemy_repository import DbRepository
from ..core.services.db_production_calendar_services import (
    get_productions_calendar_holidays_service,
    get_productions_calendar_working_days_service,
)


@bp.route("/load_report", methods=["GET", "POST"])
@login_required
async def load_report():
    departments = await get_departments(department_filter="kafedra")
    year = date.today().year
    month = date.today().month
    form = LoadReportForm()
    form.department.choices = [(k, v.get("full")) for k, v in departments.items()]
    form.year.choices = [year - 1, year, year + 1]
    form.year.data = year
    form.month.data = f"{month}-{month}"
    if request.method == "POST" and form.validate_on_submit():
        year = request.form.get("year")
        month = request.form.get("month").split("-")
        month_start = int(month[0])
        month_end = int(month[1])
        department = request.form.get("department")
        logging.info(
            f"view функция reports.load_report передала "
            f"year={year}, month_start={month_start}, "
            f"month_end={month_end}, department={department}"
        )
        return redirect(
            url_for(
                "reports.load_report_export",
                year=year,
                month_start=month_start,
                month_end=month_end,
                department_id=department,
            )
        )
    return render_template("reports/load_report.html", active="reports", form=form)


@bp.route(
    "/load_report/<int:year>/<int:month_start>/<int:month_end>/<int:department_id>",
    methods=["GET", "POST"],
)
@login_required
async def load_report_export(year, month_start, month_end, department_id):
    staff = EducationStaff(
        year,
        month_start,
        month_end,
        state_staff=await get_state_staff(),
        state_staff_history=await check_api_db_response(
            await api_get_db_table(
                ApeksConfig.TABLES.get("state_staff_history"),
                department_id=department_id,
            )
        ),
        state_staff_positions=await check_api_db_response(
            await api_get_db_table(ApeksConfig.TABLES.get("state_staff_positions"))
        ),
        departments=await get_departments(department_filter="kafedra"),
    )
    department_staff = staff.department_staff(department_id)
    load = LoadReportProcessor(
        year=year,
        month_start=month_start,
        month_end=month_end,
        department_id=department_id,
        departments=staff.departments,
        department_staff=department_staff,
        schedule_lessons=await check_api_db_response(
            await get_lessons(year, month_start, month_end)
        ),
        schedule_lessons_staff=await check_api_db_response(
            await api_get_db_table(
                ApeksConfig.TABLES.get("schedule_day_schedule_lessons_staff"),
                staff_id=[*department_staff],
            )
        ),
        load_groups=await check_api_db_response(
            await api_get_db_table(ApeksConfig.TABLES.get("load_groups"))
        ),
        load_subgroups=await check_api_db_response(
            await api_get_db_table(ApeksConfig.TABLES.get("load_subgroups"))
        ),
        plan_education_plans=await check_api_db_response(
            await api_get_db_table(ApeksConfig.TABLES.get("plan_education_plans"))
        ),
        plan_education_plans_education_forms=await check_api_db_response(
            await api_get_db_table(
                ApeksConfig.TABLES.get("plan_education_plans_education_forms"),
            )
        ),
        staff_history_data=staff.staff_history(),
    )
    filename = generate_load_report(load)
    return redirect(url_for("main.get_file", filename=filename))


@bp.route("/holidays_report", methods=["GET", "POST"])
@permission_required(PermissionsConfig.REPORT_HOLIDAYS_PERMISSION)
@login_required
async def holidays_report():
    year = date.today().year
    month_start = 1
    month_end = 12
    form = HolidaysReportForm()
    form.year.choices = [year - 1, year, year + 1]
    form.year.data = year
    form.month_start.data = month_start
    form.month_end.data = month_end

    if request.method == "POST" and form.validate_on_submit():
        year = request.form.get("year")
        month_start = request.form.get("month_start")
        month_end = request.form.get("month_end")
        form.year.data = year
        form.month_start.data = int(month_start)
        form.month_end.data = int(month_end)
        logging.info(
            f"view функция reports.holidays_report передала "
            f"year={year}, month_start={month_start}, "
            f"month_end={month_end}"
        )
        return redirect(
            url_for(
                "reports.holiday_report_export",
                year=year,
                month_start=month_start,
                month_end=month_end,
            )
        )
    return render_template("reports/holidays_report.html", active="reports", form=form)


@bp.route(
    "/holiday_report/<int:year>/<int:month_start>/<int:month_end>",
    methods=["GET", "POST"],
)
@permission_required(PermissionsConfig.REPORT_HOLIDAYS_PERMISSION)
@login_required
async def holiday_report_export(year, month_start, month_end):
    non_working = [
        d.date
        for d in DbRepository(ProductionCalendarHolidays, db_session=db.session).list()
    ]
    working_sat = [
        d.date
        for d in DbRepository(
            ProductionCalendarWorkingDays, db_session=db.session
        ).list()
    ]
    filename = await generate_holidays_report(
        year, month_start, month_end, working_sat, non_working
    )
    return redirect(url_for("main.get_file", filename=filename))


@dataclass
class ProductionCalendarGetView(View):
    """View класс для просмотра записей производственного календаря."""

    template_name: str
    title: str
    service: DbRepository
    methods = ["GET", "POST"]
    base_view_slug: str

    @permission_required(PermissionsConfig.REPORT_HOLIDAYS_PERMISSION)
    @login_required
    async def dispatch_request(self):
        paginated_data = self.service.paginated(reverse=True)
        return render_template(
            self.template_name,
            title=self.title,
            paginated_data=paginated_data,
            base_view_slug=self.base_view_slug,
        )


bp.add_url_rule(
    "/production_calendar_holidays",
    view_func=ProductionCalendarGetView.as_view(
        "production_calendar_holidays",
        title="Производственный календарь - выходные дни",
        template_name="reports/production_calendar_view.html",
        service=get_productions_calendar_holidays_service(),
        base_view_slug="production_calendar_holidays",
    ),
)

bp.add_url_rule(
    "/production_calendar_working_days",
    view_func=ProductionCalendarGetView.as_view(
        "production_calendar_working_days",
        title="Производственный календарь - рабочие выходные",
        template_name="reports/production_calendar_view.html",
        service=get_productions_calendar_working_days_service(),
        base_view_slug="production_calendar_working_days",
    ),
)


@dataclass
class ProductionCalendarAddView(View):
    """View класс для добавления записей производственного календаря."""

    template_name: str
    title: str
    service: DbRepository
    methods = ["GET", "POST"]
    base_view_slug: str

    @permission_required(PermissionsConfig.PRODUCTION_CALENDAR_EDIT_PERMISSION)
    @login_required
    async def dispatch_request(self, **kwargs):
        form = ProductionCalendarForm()
        if request.method == "POST" and form.validate_on_submit():
            self.service.create(
                date=date.fromisoformat(request.form.get("date")),
            )
            flash(
                f"Запись {request.form.get('date')} успешно добавлена",
                category="success",
            )
            return redirect(url_for(f".{self.base_view_slug}"))
        return render_template(
            self.template_name,
            title=f'Добавить запись в "{self.title.lower()}"',
            form=form,
            back_link=url_for(f".{self.base_view_slug}", **kwargs),
        )


bp.add_url_rule(
    "/production_calendar_holidays_add",
    view_func=ProductionCalendarAddView.as_view(
        "production_calendar_holidays_add",
        title="Производственный календарь - выходные дни",
        template_name="reports/production_calendar_edit.html",
        service=get_productions_calendar_holidays_service(),
        base_view_slug="production_calendar_holidays",
    ),
)

bp.add_url_rule(
    "/production_calendar_working_days_add",
    view_func=ProductionCalendarAddView.as_view(
        "production_calendar_working_days_add",
        title="Производственный календарь - рабочие выходные",
        template_name="reports/production_calendar_edit.html",
        service=get_productions_calendar_working_days_service(),
        base_view_slug="production_calendar_working_days",
    ),
)


@dataclass
class ProductionCalendarEditView(View):
    """View класс для редактирования записей производственного календаря."""

    template_name: str
    title: str
    service: DbRepository
    methods = ["GET", "POST"]
    base_view_slug: str

    @permission_required(PermissionsConfig.PRODUCTION_CALENDAR_EDIT_PERMISSION)
    @login_required
    async def dispatch_request(self, id_: int, **kwargs):
        obj = self.service.get(id=id_)
        form = ProductionCalendarForm(obj=obj)
        if request.method == "POST" and form.validate_on_submit():
            self.service.update(
                id_,
                date=date.fromisoformat(request.form.get("date")),
            )
            flash(
                f"Запись {request.form.get('date')} успешно обновлена",
                category="success",
            )
            return redirect(url_for(f".{self.base_view_slug}"))
        return render_template(
            self.template_name,
            title=f'Изменить запись в "{self.title.lower()}"',
            form=form,
            back_link=url_for(f".{self.base_view_slug}", **kwargs),
        )


bp.add_url_rule(
    "/production_calendar_holidays/<int:id_>",
    view_func=ProductionCalendarEditView.as_view(
        "production_calendar_holidays_edit",
        title="Производственный календарь - выходные дни",
        template_name="reports/production_calendar_edit.html",
        service=get_productions_calendar_holidays_service(),
        base_view_slug="production_calendar_holidays",
    ),
)

bp.add_url_rule(
    "/production_calendar_working_days/<int:id_>",
    view_func=ProductionCalendarEditView.as_view(
        "production_calendar_working_days_edit",
        title="Производственный календарь - рабочие выходные",
        template_name="reports/production_calendar_edit.html",
        service=get_productions_calendar_working_days_service(),
        base_view_slug="production_calendar_working_days",
    ),
)


@dataclass
class ProductionCalendarDeleteView(View):
    """View класс для удаления записей производственного календаря."""

    template_name: str
    title: str
    service: DbRepository
    methods = ["GET", "POST"]
    base_view_slug: str

    @permission_required(PermissionsConfig.PRODUCTION_CALENDAR_EDIT_PERMISSION)
    @login_required
    async def dispatch_request(self, id_: int, **kwargs):
        obj = self.service.get(id=id_)
        form = ObjectDeleteForm(obj=obj)
        current_date = str(obj.date)
        if request.method == "POST" and form.validate_on_submit():
            self.service.delete(obj.id)
            flash(
                f"Запись {current_date} успешно удалена",
                category="success",
            )
            return redirect(url_for(f".{self.base_view_slug}"))
        return render_template(
            self.template_name,
            title=f'Удалить запись в "{self.title.lower()}"',
            obj_data=obj,
            form=form,
            back_link=url_for(f".{self.base_view_slug}", **kwargs),
        )


bp.add_url_rule(
    "/production_calendar_holidays/delete/<int:id_>",
    view_func=ProductionCalendarDeleteView.as_view(
        "production_calendar_holidays_delete",
        title="Производственный календарь - выходные дни",
        template_name="reports/production_calendar_delete.html",
        service=get_productions_calendar_holidays_service(),
        base_view_slug="production_calendar_holidays",
    ),
)

bp.add_url_rule(
    "/production_calendar_working_days/delete/<int:id_>",
    view_func=ProductionCalendarDeleteView.as_view(
        "production_calendar_working_days_delete",
        title="Производственный календарь - рабочие выходные",
        template_name="reports/production_calendar_delete.html",
        service=get_productions_calendar_working_days_service(),
        base_view_slug="production_calendar_working_days",
    ),
)
