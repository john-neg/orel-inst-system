import os
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.plans import bp
from app.main.forms import ChoosePlan, FileForm
from app.main.func import education_specialty, education_plans, allowed_file
from app.plans.func import comps_file_processing
from app.plans.models import CompPlan
from config import FlaskConfig


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


@bp.route("/mtrx_sim_choose_plan", endpoint="mtrx_sim_choose_plan", methods=["GET", "POST"])
@login_required
def mtrx_sim_choose_plan():
    title = "Матрица компетенций (с индикаторами)"
    form = ChoosePlan()
    form.edu_spec.choices = list(education_specialty().items())
    if request.method == "POST":
        edu_spec = request.form.get("edu_spec")
        form.edu_plan.choices = list(education_plans(edu_spec).items())
        if request.form.get("edu_plan") and form.validate_on_submit():
            edu_plan = request.form.get("edu_plan")
            return redirect(url_for("plans.mtrx_sim_load", plan_id=edu_plan))
        return render_template(
            "plans/mtrx_sim_choose_plan.html", active="plans", form=form, edu_spec=edu_spec
        )
    return render_template("plans/mtrx_sim_choose_plan.html", active="plans", form=form)


@bp.route("/mtrx_ind_choose_plan", endpoint="mtrx_ind_choose_plan", methods=["GET", "POST"])
@login_required
def mtrx_ind_choose_plan():
    form = ChoosePlan()
    form.edu_spec.choices = list(education_specialty().items())
    if request.method == "POST":
        edu_spec = request.form.get("edu_spec")
        form.edu_plan.choices = list(education_plans(edu_spec).items())
        if request.form.get("edu_plan") and form.validate_on_submit():
            edu_plan = request.form.get("edu_plan")
            return redirect(url_for("plans.mtrx_ind_load", plan_id=edu_plan))
        return render_template(
            "plans/mtrx_ind_choose_plan.html", active="plans", form=form, edu_spec=edu_spec
        )
    return render_template("plans/mtrx_ind_choose_plan.html", active="plans", form=form)


@bp.route("/comp_load/<int:plan_id>", methods=["GET", "POST"])
@login_required
def comp_load(plan_id):
    plan = CompPlan(plan_id)
    form = FileForm()
    if request.method == "POST":
        if request.form.get("comp_load_temp"):
            # Шаблон
            return redirect(url_for("main.get_temp_file", filename="comp_load_temp.xlsx"))
        if request.form.get("comp_delete"):
            # Полная очистка
            plan.disciplines_all_comp_del()
            return redirect(url_for("plans.comp_load", plan_id=plan_id))
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("comp_check"):
                    # Проверка файла
                    return redirect(url_for("plans.comp_check", plan_id=plan_id, filename=filename))
                if request.form.get("comp_load"):
                    # Загрузка компетенций
                    return redirect(url_for("plans.comp_update", plan_id=plan_id, filename=filename))
    return render_template(
        "plans/comp_load.html",
        active="plans",
        form=form,
        plan_name=plan.name,
        plan_comp=plan.competencies,
    )


@bp.route("/comp_check/<int:plan_id>/<string:filename>", methods=["GET", "POST"])
@login_required
def comp_check(plan_id, filename):
    file = FlaskConfig.UPLOAD_FILE_DIR + filename
    plan = CompPlan(plan_id)
    form = FileForm()
    comps = comps_file_processing(file)
    if request.method == "POST":
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("comp_check"):
                    # Проверка файла
                    return redirect(url_for("plans.comp_check", plan_id=plan_id, filename=filename))
        if request.form.get("comp_load_temp"):
            # Шаблон
            return redirect(url_for("main.get_temp_file", filename="comp_load_temp.xlsx"))
        if request.form.get("comp_delete"):
            # Полная очистка
            plan.disciplines_all_comp_del()
            return redirect(url_for("plans.comp_check", plan_id=plan_id, filename=filename))
        if request.form.get("comp_load"):
            # Загрузка компетенций
            return redirect(url_for("plans.comp_update", plan_id=plan_id, filename=filename))
    return render_template(
        "plans/comp_load.html",
        active="plans",
        form=form,
        plan_name=plan.name,
        plan_comp=plan.competencies,
        comps=comps,
    )


@bp.route("/mtrx_sim_load/<int:plan_id>", methods=["GET", "POST"])
@login_required
def mtrx_sim_load(plan_id):
    plan = CompPlan(plan_id)
    form = FileForm()
    if request.method == "POST":
        if request.form.get("mtrx_download"):
            # Текущая матрица
            return redirect(url_for("main.get_file", filename=plan.matrix_generate()))
        if request.form.get("mtrx_delete"):
            # Удаление связей
            plan.matrix_delete()
            flash('Все связи удалены')
            return redirect(url_for("plans.mtrx_sim_load", plan_id=plan_id))
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("mtrx_sim_check"):
                    # Проверка файла
                    return redirect(url_for("plans.mtrx_sim_check", plan_id=plan_id, filename=filename))
                if request.form.get("mtrx_sim_load"):
                    # Загрузка связей
                    return redirect(url_for("plans.mtrx_sim_update", plan_id=plan_id, filename=filename))
    return render_template(
        "plans/mtrx_sim_load.html",
        active="plans",
        form=form,
        plan_name=plan.name,
        plan_relations=plan.disciplines_comp_dict(),
    )


@bp.route("/mtrx_sim_check/<int:plan_id>/<string:filename>", methods=["GET", "POST"])
@login_required
def mtrx_sim_check(plan_id, filename):
    file = FlaskConfig.UPLOAD_FILE_DIR + filename
    plan = CompPlan(plan_id)
    form = FileForm()
    report, comp_code_errors = plan.matrix_simple_file_check(file)
    if request.method == "POST":
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("mtrx_sim_check"):
                    # Проверка файла
                    return redirect(url_for("plans.mtrx_sim_check", plan_id=plan_id, filename=filename))
        if request.form.get("mtrx_download"):
            # Текущая матрица
            return redirect(url_for("main.get_file", filename=plan.matrix_generate()))
        if request.form.get("mtrx_delete"):
            # Удаление связей
            plan.matrix_delete()
            flash('Все связи удалены')
            return redirect(url_for("plans.mtrx_sim_check", plan_id=plan_id, filename=filename))
        if request.form.get("mtrx_sim_load"):
            # Загрузка связей
            return redirect(url_for("plans.mtrx_sim_update", plan_id=plan_id, filename=filename))
    return render_template(
        "plans/mtrx_sim_load.html",
        active="plans",
        form=form,
        plan_name=plan.name,
        plan_relations=plan.disciplines_comp_dict(),
        report=report,
        comp_code_errors=comp_code_errors,
    )


@bp.route("/mtrx_sim_update/<int:plan_id>/<string:filename>", methods=["GET"])
@login_required
def mtrx_sim_update(plan_id, filename):
    file = FlaskConfig.UPLOAD_FILE_DIR + filename
    plan = CompPlan(plan_id)
    plan.matrix_simple_upload(file)
    os.remove(file)
    return redirect(url_for("plans.mtrx_sim_load", plan_id=plan_id))


@bp.route("/mtrx_ind_load/<int:plan_id>", methods=["GET", "POST"])
@login_required
def mtrx_ind_load(plan_id):
    plan = CompPlan(plan_id)
    form = FileForm()
    if request.method == "POST":
        if request.form.get("comp_load_temp"):
            # Шаблон
            return redirect(url_for("main.get_temp_file", filename="comp_load_temp.xlsx"))
        if request.form.get("comp_delete"):
            # Полная очистка
            plan.disciplines_all_comp_del()
            return redirect(url_for("plans.comp_load", plan_id=plan_id))
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("comp_check"):
                    # Проверка файла
                    return redirect(url_for("plans.comp_check", plan_id=plan_id, filename=filename))
                if request.form.get("comp_load"):
                    # Загрузка компетенций
                    return redirect(url_for("plans.comp_update", plan_id=plan_id, filename=filename))
    return render_template(
        "plans/comp_load.html",
        active="plans",
        form=form,
        plan_name=plan.name,
        plan_comp=plan.competencies,
    )


@bp.route("/comp_update/<int:plan_id>/<string:filename>", methods=["GET"])
@login_required
def comp_update(plan_id, filename):
    file = FlaskConfig.UPLOAD_FILE_DIR + filename
    plan = CompPlan(plan_id)
    comps = comps_file_processing(file)
    left_node, right_node = 1, 2
    for comp in comps:
        code = comp[0]
        description = comp[1]
        plan.load_comp(code, description, left_node, right_node)
        left_node += 2
        right_node += 2
    os.remove(file)
    return redirect(url_for("plans.comp_load", plan_id=plan_id))
