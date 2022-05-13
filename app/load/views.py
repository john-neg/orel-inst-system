import logging

from flask import render_template, request, url_for
from werkzeug.utils import redirect

from app.common.classes.EducationStaff import EducationStaff
from app.common.classes.LoadReportProcessor import LoadReportProcessor
from app.common.func import (
    get_departments,
    get_state_staff,
    check_api_db_response,
    api_get_db_table,
    get_lessons,
)
from app.load import bp
from app.load.forms import LoadReportForm
from config import ApeksConfig as Apeks


@bp.route("/load", methods=["GET", "POST"])
async def load_report():
    form = LoadReportForm()
    departments = await get_departments()
    form.department.choices = [(k, v.get("full")) for k, v in departments.items()]
    if request.method == "POST" and form.validate_on_submit():
        year = request.form.get("year")
        month = request.form.get("month").split('-')
        month_start = int(month[0])
        month_end = int(month[1])
        department = request.form.get("department")
        logging.info(f'view функция load.load_report передала year={year}, month_start={month_start}, '
                     f'month_end={month_end}, department={department}')
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
            await api_get_db_table(Apeks.TABLES.get("state_staff_history"))
        ),
        state_staff_positions=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("state_staff_positions"))
        ),
        departments=await get_departments(),
    )

    load = LoadReportProcessor(
        year=year,
        month_start=month_start,
        month_end=month_end,
        department_id=department_id,
        departments=staff.departments,
        department_staff=staff.department_staff(department_id),
        schedule_lessons=await check_api_db_response(
            await get_lessons(year, month_start, month_end)
            ),
        schedule_lessons_staff=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("schedule_day_schedule_lessons_staff"))
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
                Apeks.TABLES.get("plan_education_plans_education_forms")
            )
        ),
        staff_history_data=staff.staff_history(),
    )

    load.generate_report()
    return redirect(url_for("main.get_file", filename=load.filename))
