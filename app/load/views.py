import logging
from datetime import date

from flask import render_template, request, url_for
from werkzeug.utils import redirect

from app.common.classes.EducationStaff import EducationStaff
from app.common.classes.LoadReportProcessor import LoadReportProcessor
from app.common.func.api_get import (
    check_api_db_response,
    api_get_db_table,
    get_lessons,
)
from app.common.func.organization import get_departments
from app.common.func.staff import get_state_staff
from app.common.reports.load_report import generate_load_report
from config import ApeksConfig as Apeks
from . import bp
from .forms import LoadReportForm


@bp.route("/load", methods=["GET", "POST"])
async def load_report():
    departments = await get_departments(
        department_filter="kafedra"
    )
    year = date.today().year
    month = date.today().month
    form = LoadReportForm()
    form.department.choices = [(k, v.get("full")) for k, v in departments.items()]
    form.year.choices = [year - 1, year, year + 1]
    form.year.data = year
    form.month.data = f'{month}-{month}'
    if request.method == "POST" and form.validate_on_submit():
        year = request.form.get("year")
        month = request.form.get("month").split("-")
        month_start = int(month[0])
        month_end = int(month[1])
        department = request.form.get("department")
        logging.info(
            f"view функция load.load_report передала "
            f"year={year}, month_start={month_start}, "
            f"month_end={month_end}, department={department}"
        )
        return redirect(
            url_for(
                "load.load_report_export",
                year=year,
                month_start=month_start,
                month_end=month_end,
                department_id=department,
            )
        )
    return render_template("load/load_report.html", active="load", form=form)


@bp.route(
    "/load_report/<int:year>/<int:month_start>"
    + "/<int:month_end>/<int:department_id>",
    methods=["GET", "POST"],
)
async def load_report_export(year, month_start, month_end, department_id):
    staff = EducationStaff(
        year,
        month_start,
        month_end,
        state_staff=await get_state_staff(),
        state_staff_history=await check_api_db_response(
            await api_get_db_table(
                Apeks.TABLES.get("state_staff_history"),
                department_id=department_id,
            )
        ),
        state_staff_positions=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("state_staff_positions"))
        ),
        departments=await get_departments(
            department_filter="kafedra"
        ),
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
                Apeks.TABLES.get("schedule_day_schedule_lessons_staff"),
                staff_id=[*department_staff],
            )
        ),
        load_groups=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("load_groups"))
        ),
        load_subgroups=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("load_subgroups"))
        ),
        plan_education_plans=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("plan_education_plans"))
        ),
        plan_education_plans_education_forms=await check_api_db_response(
            await api_get_db_table(
                Apeks.TABLES.get("plan_education_plans_education_forms"),
            )
        ),
        staff_history_data=staff.staff_history(),
    )
    filename = generate_load_report(load)
    return redirect(url_for("main.get_file", filename=filename))
