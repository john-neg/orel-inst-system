import os
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.plans import bp
from app.main.forms import ChoosePlan, FileForm
from app.main.func import education_specialty, education_plans, allowed_file
from app.plans.func import comps_file_processing
from app.plans.models import CompPlan, MatrixIndicatorsFile
from config import FlaskConfig


@bp.route("/comp_choose_plan", endpoint="comp_choose_plan", methods=["GET", "POST"])
@login_required
def comp_choose_plan():
    title = "Загрузка компетенций в учебный план"
    form = ChoosePlan()
    form.edu_spec.choices = list(education_specialty().items())
    if request.method == "POST":
        edu_spec = request.form.get("edu_spec")
        form.edu_plan.choices = list(education_plans(edu_spec).items())
        if request.form.get("edu_plan") and form.validate_on_submit():
            edu_plan = request.form.get("edu_plan")
            return redirect(url_for("plans.comp_load", plan_id=edu_plan))
        return render_template(
            "plans/plan_choose_plan.html", active="plans", form=form, title=title, edu_spec=edu_spec
        )
    return render_template("plans/plan_choose_plan.html", active="plans", form=form, title=title)


@bp.route("/matrix_simple_choose_plan", methods=["GET", "POST"])
@login_required
def matrix_simple_choose_plan():
    title = "Матрица компетенций (простая)"
    form = ChoosePlan()
    form.edu_spec.choices = list(education_specialty().items())
    if request.method == "POST":
        edu_spec = request.form.get("edu_spec")
        form.edu_plan.choices = list(education_plans(edu_spec).items())
        if request.form.get("edu_plan") and form.validate_on_submit():
            edu_plan = request.form.get("edu_plan")
            return redirect(url_for("plans.matrix_simple_load", plan_id=edu_plan))
        return render_template(
            "plans/plan_choose_plan.html", active="plans", form=form, title=title, edu_spec=edu_spec
        )
    return render_template("plans/plan_choose_plan.html", active="plans", form=form, title=title)


@bp.route("/matrix_indicator_choose_plan", methods=["GET", "POST"])
@login_required
def matrix_indicator_choose_plan():
    title = "Матрица компетенций (с индикаторами)"
    form = ChoosePlan()
    form.edu_spec.choices = list(education_specialty().items())
    if request.method == "POST":
        edu_spec = request.form.get("edu_spec")
        form.edu_plan.choices = list(education_plans(edu_spec).items())
        if request.form.get("edu_plan") and form.validate_on_submit():
            edu_plan = request.form.get("edu_plan")
            return redirect(url_for("plans.matrix_indicator_load", plan_id=edu_plan))
        return render_template(
            "plans/plan_choose_plan.html", active="plans", form=form, title=title, edu_spec=edu_spec
        )
    return render_template("plans/plan_choose_plan.html", active="plans", form=form, title=title)


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


@bp.route("/matrix_simple_load/<int:plan_id>", methods=["GET", "POST"])
@login_required
def matrix_simple_load(plan_id):
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
            return redirect(url_for("plans.matrix_simple_load", plan_id=plan_id))
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("mtrx_sim_check"):
                    # Проверка файла
                    return redirect(url_for("plans.matrix_simple_check", plan_id=plan_id, filename=filename))
                if request.form.get("mtrx_sim_load"):
                    # Загрузка связей
                    return redirect(url_for("plans.matrix_simple_update", plan_id=plan_id, filename=filename))
    return render_template(
        "plans/matrix_simple_load.html",
        active="plans",
        form=form,
        plan_name=plan.name,
        plan_relations=plan.disciplines_comp_dict(),
    )


@bp.route("/matrix_indicator_load/<int:plan_id>", methods=["GET", "POST"])
@login_required
def matrix_indicator_load(plan_id):
    plan = CompPlan(plan_id)
    form = FileForm()
    if request.method == "POST":
        if request.form.get("mtrx_ind_temp"):
            # Шаблон
            return redirect(url_for("main.get_temp_file", filename="matrix_ind_temp.xlsx"))
        if request.form.get("mtrx_download"):
            # Текущая матрица
            return redirect(url_for("main.get_file", filename=plan.matrix_generate()))
        if request.form.get("mtrx_delete"):
            # Удаление связей
            plan.matrix_delete()
            flash('Все связи удалены')
            return redirect(url_for("plans.matrix_indicator_load", plan_id=plan_id))
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("mtrx_ind_check"):
                    # Проверка файла
                    return redirect(url_for("plans.matrix_indicator_check", plan_id=plan_id, filename=filename))
                if request.form.get("mtrx_ind_load"):
                    if request.form.get("switch_relations") and request.form.get("switch_programs"):
                        return "switch_relations & switch_programs"
                    elif request.form.get("switch_relations"):
                        return "switch_relations"
                    elif request.form.get("switch_programs"):
                        return "switch_programs"
                    else:
                        flash('Ничего не загружено, т.к. все опции были выключены')
                        return redirect(url_for("plans.matrix_indicator_check", plan_id=plan_id, filename=filename))
    return render_template(
        "plans/matrix_indicator_load.html",
        active="plans",
        form=form,
        plan_name=plan.name,
        plan_relations=plan.disciplines_comp_dict(),
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


@bp.route("/matrix_simple_check/<int:plan_id>/<string:filename>", methods=["GET", "POST"])
@login_required
def matrix_simple_check(plan_id, filename):
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
                    return redirect(url_for("plans.matrix_simple_check", plan_id=plan_id, filename=filename))
        if request.form.get("mtrx_download"):
            # Текущая матрица
            return redirect(url_for("main.get_file", filename=plan.matrix_generate()))
        if request.form.get("mtrx_delete"):
            # Удаление связей
            plan.matrix_delete()
            flash('Все связи удалены')
            return redirect(url_for("plans.matrix_simple_check", plan_id=plan_id, filename=filename))
        if request.form.get("mtrx_sim_load"):
            # Загрузка связей
            return redirect(url_for("plans.matrix_simple_update", plan_id=plan_id, filename=filename))
    return render_template(
        "plans/matrix_simple_load.html",
        active="plans",
        form=form,
        plan_name=plan.name,
        plan_relations=plan.disciplines_comp_dict(),
        report=report,
        comp_code_errors=comp_code_errors,
    )

@bp.route("/matrix_indicator_check/<int:plan_id>/<string:filename>", methods=["GET", "POST"])
@login_required
def matrix_indicator_check(plan_id, filename):
    file = FlaskConfig.UPLOAD_FILE_DIR + filename
    plan = CompPlan(plan_id)
    matrix = MatrixIndicatorsFile(file)
    # File check
    report = {}
    for disc_id in plan.disciplines:
        discipline_name = plan.discipline_name(disc_id)
        if matrix.find_discipline(discipline_name):
            comp_data = matrix.disc_comp(discipline_name)
            if comp_data:
                report[discipline_name] = list(comp_data.keys())
            else:
                report[discipline_name] = ["None"]
        else:
            report[discipline_name] = []
    form = FileForm()
    # report, comp_code_errors, ind_errors = plan.matrix_ind_file_check(file)
    if request.method == "POST":
        if request.form.get("mtrx_ind_temp"):
            # Шаблон
            return redirect(url_for("main.get_temp_file", filename="matrix_ind_temp.xlsx"))
        if request.form.get("mtrx_download"):
            # Текущая матрица
            return redirect(url_for("main.get_file", filename=plan.matrix_generate()))
        if request.form.get("mtrx_delete"):
            # Удаление связей
            plan.matrix_delete()
            flash('Все связи удалены')
            return redirect(url_for("plans.matrix_indicator_load", plan_id=plan_id))
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("mtrx_ind_check"):
                    # Проверка файла
                    return redirect(url_for("plans.matrix_indicator_check", plan_id=plan_id, filename=filename))
                if request.form.get("mtrx_ind_load"):
                    if request.form.get("switch_relations") and request.form.get("switch_programs"):
                        return "switch_relations & switch_programs"
                    elif request.form.get("switch_relations"):
                        return "switch_relations"
                    elif request.form.get("switch_programs"):
                        return "switch_programs"
                    else:
                        flash('Ничего не загружено, т.к. все опции были выключены')
                        return redirect(url_for("plans.matrix_indicator_check", plan_id=plan_id, filename=filename))
    return render_template(
        "plans/matrix_indicator_load.html",
        active="plans",
        form=form,
        filename=filename,
        plan_name=plan.name,
        plan_relations=plan.disciplines_comp_dict(),
        report=report,
        file_errors=matrix.file_errors(),
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


@bp.route("/matrix_simple_update/<int:plan_id>/<string:filename>", methods=["GET"])
@login_required
def matrix_simple_update(plan_id, filename):
    file = FlaskConfig.UPLOAD_FILE_DIR + filename
    plan = CompPlan(plan_id)
    plan.matrix_simple_upload(file)
    os.remove(file)
    return redirect(url_for("plans.matrix_simple_load", plan_id=plan_id))


@bp.route("/matrix_indicator_file_upload", methods=["GET", "POST"])
@login_required
def matrix_indicator_file_upload():
    form = FileForm()
    if request.method == "POST":
        if request.files["xlsx_file"]:
            file = request.files["xlsx_file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("mtrx_file_check"):
                    return redirect(url_for("plans.matrix_indicator_file_check", filename=filename))
    return render_template(
        "plans/matrix_indicator_file.html",
        active="plans",
        form=form,
    )

@bp.route("/matrix_indicator_file_check/<string:filename>", methods=["GET", "POST"])
@login_required
def matrix_indicator_file_check(filename):
    form = FileForm()
    file = FlaskConfig.UPLOAD_FILE_DIR + filename
    matrix = MatrixIndicatorsFile(file)
    if request.method == "POST":
        if request.files["xlsx_file"]:
            file = request.files["xlsx_file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                file_path = FlaskConfig.UPLOAD_FILE_DIR + filename
                if request.form.get("mtrx_file_check"):
                    return redirect(url_for("plans.matrix_indicator_file_check", filename=filename))
                if request.form.get("mtrx_indicator_export"):
                    matrix = MatrixIndicatorsFile(file_path)
                    filename = matrix.list_to_word()
                    os.remove(file_path)
                    return redirect(url_for("main.get_file", filename=filename))
    if request.form.get("mtrx_indicator_export"):
        filename = matrix.list_to_word()
        os.remove(file)
        return redirect(url_for("main.get_file", filename=filename))
    return render_template(
        "plans/matrix_indicator_file.html",
        active="plans",
        file_errors=matrix.file_errors(),
        message="Ошибки не обнаружены",
        form=form,
        filename=filename,
    )
