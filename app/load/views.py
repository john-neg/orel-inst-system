from flask import render_template, request, url_for
from werkzeug.utils import redirect

from app.load import bp
from app.load.forms import LoadReportForm
from app.load.func import (
    lessons_staff,
    load_subgroups,
    load_groups,
    plan_education_plans_education_forms,
    plan_education_plans,
)
from app.load.models import LoadReport, LoadData
from app.common.func import get_departments


@bp.route("/load", methods=["GET", "POST"])
async def load_report():
    form = LoadReportForm()
    departments = await get_departments()
    form.department.choices = [(k, v.get("full")) for k, v in departments.items()]
    if request.method == "POST" and form.validate_on_submit():
        year = request.form.get("year")
        #TODO новая маркировка для месяцев в форме должна правильно отрабатываться
        month = request.form.get("month")
        department = request.form.get("department")
        return redirect(
            url_for(
                "load.load_report_export", year=year, month=month, department=department
            )
        )
    return render_template("load/load_report.html", active="load", form=form)


@bp.route(
    "/load_report/<int:year>/<string:month>/<int:department>", methods=["GET", "POST"]
)
async def load_report_export(year, month, department):
    load = LoadData(
        year,
        month,
        lesson_staff=await lessons_staff(),
        load_subgroup=await load_subgroups(),
        load_group=await load_groups(),
        plan_education_plans_education_form=await plan_education_plans_education_forms(),
        plan_education_plan=await plan_education_plans(),
    )
    report = LoadReport(year, month, department, load)

    report.generate_report()
    return redirect(url_for("main.get_file", filename=report.filename))
