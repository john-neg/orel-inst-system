from flask import render_template, request, redirect, url_for
from flask_login import login_required
from app.plans import bp
from app.plans.forms import ChoosePlan, FileForm
from app.main.func import education_specialty, education_plans, db_filter_req
from app.plans.models import EducationPlan
from openpyxl import Workbook, load_workbook


@bp.route("/comp_choose_plan", endpoint="comp_choose_plan", methods=["GET", "POST"])
@login_required
def comp_choose_plan():
    form = ChoosePlan()
    form.edu_spec.choices = list(education_specialty().items())
    if request.method == "POST":
        edu_spec = request.form.get("edu_spec")
        form.edu_plan.choices = list(education_plans(edu_spec).items())
        if request.form.get("edu_plan") and form.validate_on_submit():
            edu_plan = request.form.get("edu_plan")
            return redirect(url_for("plans.comp_load", plan_id=edu_plan))
        return render_template(
            "plans/comp_choose_plan.html", active="plans", form=form, edu_spec=edu_spec
        )
    return render_template("plans/comp_choose_plan.html", active="plans", form=form)


@bp.route("/comp_load/<int:plan_id>", methods=["GET", "POST"])
@login_required
def comp_load(plan_id):
    plan = EducationPlan(plan_id)
    form = FileForm()
    plan_name = db_filter_req("plan_education_plans", "id", plan_id)[0]["name"]
    if request.form.get("comp_load_temp"):  # Шаблон
        return redirect(url_for("main.get_temp_file", filename="comp_load_temp.xlsx"))
    if request.form.get("comp_delete"):  # Полная очистка
        plan.disciplines_all_comp_del()
        return redirect(url_for("plans.comp_load", plan_id=plan_id))
    if request.form.get("comp_check"):  # Проверка файла
        wb = load_workbook('document.xlsx')
        return redirect(url_for("plans.comp_load", plan_id=plan_id))
    if request.form.get("comp_load"):  # Загрузка компетенций
        return redirect(url_for("plans.comp_load", plan_id=plan_id))
    return render_template(
        "plans/comp_load.html",
        active="plans",
        form=form,
        plan_name=plan_name,
        plan_comp=plan.competencies,
    )
