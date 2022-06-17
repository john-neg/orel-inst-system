import os

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.common.forms import ChoosePlan, FileForm
from app.common.func.api_get import get_plan_education_specialties, \
    get_education_plans
from app.common.func.app_core import allowed_file
from app.plans import bp
from app.plans.func import comps_file_processing, disciplines_comp_load
from app.plans.models import CompPlan, MatrixIndicatorsFile
from app.plans.models import WorkProgramProcessing
from config import FlaskConfig


@bp.route("/comp_choose_plan", endpoint="comp_choose_plan", methods=["GET", "POST"])
@login_required
async def comp_choose_plan():
    title = "Загрузка компетенций в учебный план"
    form = ChoosePlan()
    specialities = await get_plan_education_specialties()
    form.edu_spec.choices = list(specialities.items())
    if request.method == "POST":
        edu_spec = request.form.get("edu_spec")
        plans = await get_education_plans(edu_spec)
        form.edu_plan.choices = list(plans.items())
        if request.form.get("edu_plan") and form.validate_on_submit():
            edu_plan = request.form.get("edu_plan")
            return redirect(url_for("plans.comp_load", plan_id=edu_plan))
        return render_template(
            "plans/plans_choose_plan.html",
            active="plans",
            form=form,
            title=title,
            edu_spec=edu_spec,
        )
    return render_template(
        "plans/plans_choose_plan.html",
        active="plans",
        form=form,
        title=title,
    )


@bp.route("/matrix_simple_choose_plan", methods=["GET", "POST"])
@login_required
async def matrix_simple_choose_plan():
    title = "Матрица компетенций (простая)"
    form = ChoosePlan()
    specialities = await get_plan_education_specialties()
    form.edu_spec.choices = list(specialities.items())
    if request.method == "POST":
        edu_spec = request.form.get("edu_spec")
        plans = await get_education_plans(edu_spec)
        form.edu_plan.choices = list(plans.items())
        if request.form.get("edu_plan") and form.validate_on_submit():
            edu_plan = request.form.get("edu_plan")
            return redirect(url_for("plans.matrix_simple_load", plan_id=edu_plan))
        return render_template(
            "plans/plans_choose_plan.html",
            active="plans",
            form=form,
            title=title,
            edu_spec=edu_spec,
        )
    return render_template(
        "plans/plans_choose_plan.html",
        active="plans",
        form=form,
        title=title,
    )


@bp.route("/matrix_indicator_choose_plan", methods=["GET", "POST"])
@login_required
async def matrix_indicator_choose_plan():
    title = "Матрица компетенций (с индикаторами)"
    form = ChoosePlan()
    specialities = await get_plan_education_specialties()
    form.edu_spec.choices = list(specialities.items())
    if request.method == "POST":
        edu_spec = request.form.get("edu_spec")
        plans = await get_education_plans(edu_spec)
        form.edu_plan.choices = list(plans.items())
        if request.form.get("edu_plan") and form.validate_on_submit():
            edu_plan = request.form.get("edu_plan")
            return redirect(url_for("plans.matrix_indicator_load", plan_id=edu_plan))
        return render_template(
            "plans/plans_choose_plan.html",
            active="plans",
            form=form,
            title=title,
            edu_spec=edu_spec,
        )
    return render_template(
        "plans/plans_choose_plan.html",
        active="plans",
        form=form,
        title=title,
    )


@bp.route("/comp_load/<int:plan_id>", methods=["GET", "POST"])
@login_required
def comp_load(plan_id):
    plan = CompPlan(plan_id)
    form = FileForm()
    if request.method == "POST":
        if request.form.get("comp_load_temp"):
            # Шаблон
            return redirect(
                url_for("main.get_temp_file", filename="comp_load_temp.xlsx")
            )
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
                    return redirect(
                        url_for("plans.comp_check", plan_id=plan_id, filename=filename)
                    )
                if request.form.get("comp_load"):
                    # Загрузка компетенций
                    return redirect(
                        url_for("plans.comp_update", plan_id=plan_id, filename=filename)
                    )
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
            flash("Все связи удалены")
            return redirect(url_for("plans.matrix_simple_load", plan_id=plan_id))
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("mtrx_sim_check"):
                    # Проверка файла
                    return redirect(
                        url_for(
                            "plans.matrix_simple_check",
                            plan_id=plan_id,
                            filename=filename,
                        )
                    )
                if request.form.get("mtrx_sim_load"):
                    # Загрузка связей
                    return redirect(
                        url_for(
                            "plans.matrix_simple_update",
                            plan_id=plan_id,
                            filename=filename,
                        )
                    )
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
            return redirect(
                url_for("main.get_temp_file", filename="matrix_ind_temp.xlsx")
            )
        if request.form.get("mtrx_download"):
            # Текущая матрица
            return redirect(url_for("main.get_file", filename=plan.matrix_generate()))
        if request.form.get("mtrx_delete"):
            # Удаление связей
            plan.matrix_delete()
            flash("Все связи удалены")
            return redirect(url_for("plans.matrix_indicator_load", plan_id=plan_id))
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("mtrx_ind_check"):
                    # Проверка файла
                    return redirect(
                        url_for(
                            "plans.matrix_indicator_check",
                            plan_id=plan_id,
                            filename=filename,
                        )
                    )
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
                    return redirect(
                        url_for("plans.comp_check", plan_id=plan_id, filename=filename)
                    )
        if request.form.get("comp_load_temp"):
            # Шаблон
            return redirect(
                url_for("main.get_temp_file", filename="comp_load_temp.xlsx")
            )
        if request.form.get("comp_delete"):
            # Полная очистка
            plan.disciplines_all_comp_del()
            return redirect(
                url_for("plans.comp_check", plan_id=plan_id, filename=filename)
            )
        if request.form.get("comp_load"):
            # Загрузка компетенций
            return redirect(
                url_for("plans.comp_update", plan_id=plan_id, filename=filename)
            )
    return render_template(
        "plans/comp_load.html",
        active="plans",
        form=form,
        plan_name=plan.name,
        plan_comp=plan.competencies,
        comps=comps,
    )


@bp.route(
    "/matrix_simple_check/<int:plan_id>/<string:filename>", methods=["GET", "POST"]
)
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
                    return redirect(
                        url_for(
                            "plans.matrix_simple_check",
                            plan_id=plan_id,
                            filename=filename,
                        )
                    )
        if request.form.get("mtrx_download"):
            # Текущая матрица
            return redirect(url_for("main.get_file", filename=plan.matrix_generate()))
        if request.form.get("mtrx_delete"):
            # Удаление связей
            plan.matrix_delete()
            flash("Все связи удалены")
            return redirect(
                url_for("plans.matrix_simple_check", plan_id=plan_id, filename=filename)
            )
        if request.form.get("mtrx_sim_load"):
            # Загрузка связей
            return redirect(
                url_for(
                    "plans.matrix_simple_update", plan_id=plan_id, filename=filename
                )
            )
    return render_template(
        "plans/matrix_simple_load.html",
        active="plans",
        form=form,
        plan_name=plan.name,
        plan_relations=plan.disciplines_comp_dict(),
        report=report,
        comp_code_errors=comp_code_errors,
    )


@bp.route(
    "/matrix_indicator_check/<int:plan_id>/<string:filename>", methods=["GET", "POST"]
)
@login_required
def matrix_indicator_check(plan_id, filename):
    file = FlaskConfig.UPLOAD_FILE_DIR + filename
    plan = CompPlan(plan_id)
    matrix = MatrixIndicatorsFile(file)
    form = FileForm()

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
    # Comp check
    no_comp_list = []
    matrix_comp_list = matrix.comp_list()
    plan_comp_list = plan.get_comp_list()
    for comp in matrix_comp_list:
        if comp not in plan_comp_list:
            no_comp_list.append(comp)

    def disc_load_ids(curriculum_discipline_id):
        """Получение ID компетенций плана для дисциплины для загрузки."""
        disc_comp_load = []
        disc_name = plan.discipline_name(curriculum_discipline_id)
        compet_data = matrix.disc_comp(disc_name)
        for compet in compet_data:
            for v in range(len(plan.competencies)):
                if compet == plan.competencies[v]["code"]:
                    disc_comp_load.append(plan.competencies[v]["id"])
        return disc_comp_load

    def disc_comp_upload(curriculum_discipline_id):
        """Загрузка связей дисциплин и компетенций из файла в план."""
        for compet in disc_load_ids(curriculum_discipline_id):
            disciplines_comp_load(curriculum_discipline_id, compet)

    def work_program_load(curriculum_discipline_id):
        """Загрузка индикаторов в программу"""
        wp = WorkProgramProcessing(curriculum_discipline_id)
        wp.comp_data_del()
        disc_name = plan.discipline_name(curriculum_discipline_id)
        compet_data = matrix.disc_comp(disc_name)
        fields = {1: "knowledge", 2: "abilities", 3: "ownerships"}
        knowledge, abilities, ownerships = [], [], []

        for compet in compet_data.keys():
            for v in range(len(plan.competencies)):
                if compet == plan.competencies[v]["code"]:
                    competency_id = plan.competencies[v]["id"]
                    for f in fields:
                        value = ";\n".join(compet_data[compet][fields[f]])
                        if value:
                            wp.comp_data_add(competency_id, f, value)

            knowledge += compet_data[compet]["knowledge"]
            abilities += compet_data[compet]["abilities"]
            ownerships += compet_data[compet]["ownerships"]

        wp.comp_level_edit(
            ";\n".join(knowledge), ";\n".join(abilities), ";\n".join(ownerships)
        )

    if request.method == "POST":
        if request.form.get("mtrx_ind_temp"):
            # Шаблон
            return redirect(
                url_for("main.get_temp_file", filename="matrix_ind_temp.xlsx")
            )
        if request.form.get("mtrx_download"):
            # Текущая матрица
            return redirect(url_for("main.get_file", filename=plan.matrix_generate()))
        if request.form.get("mtrx_delete"):
            # Удаление связей
            plan.matrix_delete()
            flash("Все связи удалены")
            return redirect(url_for("plans.matrix_indicator_load", plan_id=plan_id))
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("mtrx_ind_check"):
                    # Проверка файла
                    return redirect(
                        url_for(
                            "plans.matrix_indicator_check",
                            plan_id=plan_id,
                            filename=filename,
                        )
                    )
        if request.form.get("mtrx_ind_load"):
            if request.form.get("switch_relations") and request.form.get(
                "switch_programs"
            ):
                for disc_id in plan.disciplines.keys():
                    disc_comp_upload(disc_id)
                    work_program_load(disc_id)
                flash("Связи и программы обновлены")
            elif request.form.get("switch_relations"):
                for disc_id in plan.disciplines.keys():
                    disc_comp_upload(disc_id)
                flash("Связи обновлены")
            elif request.form.get("switch_programs"):
                for disc_id in plan.disciplines.keys():
                    work_program_load(disc_id)
                flash("Программы обновлены")
            else:
                flash("Ничего не загружено, т.к. все опции были выключены")
            os.remove(file)
            return redirect(url_for("plans.matrix_indicator_load", plan_id=plan_id))
    return render_template(
        "plans/matrix_indicator_load.html",
        active="plans",
        form=form,
        filename=filename,
        plan_name=plan.name,
        plan_relations=plan.disciplines_comp_dict(),
        report=report,
        file_errors=matrix.file_errors(),
        no_comp_list=no_comp_list,
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
                    return redirect(
                        url_for("plans.matrix_indicator_file_check", filename=filename)
                    )
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
                    return redirect(
                        url_for("plans.matrix_indicator_file_check", filename=filename)
                    )
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
