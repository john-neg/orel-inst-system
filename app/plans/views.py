import os

from flask import render_template, request, redirect, url_for, flash
from flask.views import View
from flask_login import login_required

from app.common.classes.PlanMatrixProcessor import (
    MatrixSimpleProcessor,
    MatrixIndicatorProcessor,
    MatrixFileProcessor,
)
from app.common.forms import ChoosePlan
from app.common.func.app_core import allowed_file
from app.common.func.education_plan import (
    get_plan_education_specialties,
    get_education_plans,
    plan_competency_add,
    discipline_competency_add,
)
from app.common.func.work_program import (
    work_programs_competencies_level_del,
    work_program_competency_data_add,
    work_program_competency_level_add,
    work_program_competency_level_edit,
)
from app.common.reports.plans_comp_matrix import generate_plans_comp_matrix
from app.common.reports.plans_indicators_file import generate_indicators_file
from app.plans import bp
from app.plans.forms import (
    CompLoadForm,
    IndicatorsFileForm,
    MatrixIndicatorForm,
    MatrixSimpleForm,
)
from app.plans.func import (
    comps_file_processing,
    get_plan_competency_instance,
    get_plan_indicator_instance,
)
from app.plans.func import plan_competencies_data_cleanup
from config import FlaskConfig, ApeksConfig as Apeks


class PlanChoosePlanView(View):
    methods = ["GET", "POST"]

    def __init__(self, title, plan_type):
        self.title = title
        self.plan_type = plan_type

    async def dispatch_request(self):
        form = ChoosePlan()
        specialities = await get_plan_education_specialties()
        form.edu_spec.choices = list(specialities.items())
        if request.method == "POST":
            edu_spec = request.form.get("edu_spec")
            plans = await get_education_plans(edu_spec)
            form.edu_plan.choices = list(plans.items())
            if request.form.get("edu_plan") and form.validate_on_submit():
                edu_plan = request.form.get("edu_plan")
                return redirect(
                    url_for(f"plans.{self.plan_type}_load", plan_id=edu_plan)
                )
            return render_template(
                "plans/choose_plan.html",
                active="plans",
                form=form,
                title=self.title,
                edu_spec=edu_spec,
            )
        return render_template(
            "plans/choose_plan.html",
            active="plans",
            form=form,
            title=self.title,
        )


bp.add_url_rule(
    "/competencies_choose_plan",
    view_func=PlanChoosePlanView.as_view(
        "competencies_choose_plan",
        title="Загрузка компетенций в учебный план",
        plan_type="competencies",
    ),
)

bp.add_url_rule(
    "/matrix_simple_choose_plan",
    view_func=PlanChoosePlanView.as_view(
        "matrix_simple_choose_plan",
        title="Матрица компетенций (простая)",
        plan_type="matrix_simple",
    ),
)

bp.add_url_rule(
    "/matrix_indicator_choose_plan",
    view_func=PlanChoosePlanView.as_view(
        "matrix_indicator_choose_plan",
        title="Матрица компетенций (с индикаторами)",
        plan_type="matrix_indicator",
    ),
)


@bp.route("/competencies_load/<int:plan_id>", methods=["GET", "POST"])
@login_required
async def competencies_load(plan_id):
    form = CompLoadForm()
    plan = await get_plan_competency_instance(plan_id)
    file, comps = None, None
    filename = request.args.get("filename")
    if filename:
        file = os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename)
        comps = comps_file_processing(file)
    if request.method == "POST":
        # Шаблон
        if request.form.get("data_template"):
            return redirect(
                url_for("main.get_temp_file", filename="comp_load_temp.xlsx")
            )
        # Полная очистка
        if request.form.get("data_delete"):
            message = await plan_competencies_data_cleanup(
                plan_id,
                plan.plan_curriculum_disciplines,
                plan_comp=True,
                relations=True,
                work_program=True,
            )
            flash(message, category="success")
            return redirect(
                url_for("plans.competencies_load", plan_id=plan_id, filename=filename)
            )
        # Загрузка файла
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
            # Проверка файла
            if request.form.get("file_check"):
                return redirect(
                    url_for(
                        "plans.competencies_load", plan_id=plan_id, filename=filename
                    )
                )
        # Загрузка компетенций
        if request.form.get("file_load"):
            left_node, right_node = 1, 2
            for comp in comps:
                code = comp[0]
                description = comp[1]
                await plan_competency_add(
                    plan_id, code, description, left_node, right_node
                )
                left_node += 2
                right_node += 2
            os.remove(file)
            flash("Данные успешно загружены", category="success")
            return redirect(url_for("plans.competencies_load", plan_id=plan_id))
    return render_template(
        "plans/competencies_load.html",
        active="plans",
        form=form,
        url=Apeks.URL,
        plan_id=plan_id,
        plan_name=plan.name,
        plan_comp=plan.plan_competencies,
        comps=comps,
    )


@bp.route("/matrix_simple_load/<int:plan_id>", methods=["GET", "POST"])
@login_required
async def matrix_simple_load(plan_id):
    form = MatrixSimpleForm()
    plan = await get_plan_competency_instance(plan_id)
    (file, match_data, comp_not_in_file, comp_not_in_plan) = (None for _ in range(4))
    filename = request.args.get("filename")
    if filename:
        file = os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename)
        processor = MatrixSimpleProcessor(file, plan)
        match_data = processor.matrix_match_data
        comp_not_in_file = processor.comp_not_in_file()
        comp_not_in_plan = processor.comp_not_in_plan()
    if request.method == "POST":
        # Текущая матрица
        if request.form.get("make_matrix"):
            return redirect(
                url_for("main.get_file", filename=generate_plans_comp_matrix(plan))
            )
        # Удаление связей
        if request.form.get("data_delete"):
            message = await plan_competencies_data_cleanup(
                plan_id,
                plan.plan_curriculum_disciplines,
                plan_comp=False,
                relations=True,
                work_program=True,
            )
            flash(message, category="success")
            return redirect(url_for("plans.matrix_simple_load", plan_id=plan_id))
        # Загрузка файла
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                # Проверка файла
                if request.form.get("file_check"):
                    return redirect(
                        url_for(
                            "plans.matrix_simple_load",
                            plan_id=plan_id,
                            filename=filename,
                        )
                    )
        # Загрузка связей
        if request.form.get("file_load"):
            for disc in match_data:
                if match_data[disc].get("comps"):
                    for comp in match_data[disc].get("comps"):
                        await discipline_competency_add(
                            match_data[disc].get("id"), match_data[disc]["comps"][comp]
                        )
            os.remove(file)
            flash("Данные успешно загружены", category="success")
            return redirect(url_for("plans.matrix_simple_load", plan_id=plan_id))
    return render_template(
        "plans/matrix_simple_load.html",
        active="plans",
        form=form,
        url=Apeks.URL,
        plan_id=plan_id,
        plan_name=plan.name,
        plan_relations=plan.named_disc_comp_relations(),
        match_data=match_data,
        comp_not_in_file=comp_not_in_file,
        comp_not_in_plan=comp_not_in_plan,
    )


@bp.route("/matrix_indicator_load/<int:plan_id>", methods=["GET", "POST"])
@login_required
async def matrix_indicator_load(plan_id):
    form = MatrixIndicatorForm()
    plan = await get_plan_indicator_instance(plan_id)
    program_control_extra_levels = plan.program_control_extra_levels
    (
        file,
        match_data,
        comp_not_in_file,
        comp_not_in_plan,
        indicator_errors,
        program_comp_level_add,
        program_comp_level_edit,
        program_competency_add,
    ) = (None for _ in range(8))
    filename = request.args.get("filename")
    if filename:
        file = os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename)
        processor = MatrixIndicatorProcessor(file, plan)
        match_data = processor.matrix_match_data
        comp_not_in_file = processor.comp_not_in_file()
        comp_not_in_plan = processor.comp_not_in_plan()
        indicator_errors = processor.indicator_errors
        (
            program_comp_level_add,
            program_comp_level_edit,
            program_competency_add,
        ) = processor.program_load_data()
    if request.method == "POST":
        # Шаблон
        if request.form.get("data_template"):
            return redirect(
                url_for("main.get_temp_file", filename="matrix_ind_temp.xlsx")
            )
        # Текущая матрица
        if request.form.get("make_matrix"):
            return redirect(
                url_for("main.get_file", filename=generate_plans_comp_matrix(plan))
            )
        # Удаление связей
        if request.form.get("data_delete"):
            message = await plan_competencies_data_cleanup(
                plan_id,
                plan.plan_curriculum_disciplines,
                plan_comp=False,
                relations=True,
                work_program=True,
            )
            flash(message, category="success")
            return redirect(url_for("plans.matrix_indicator_load", plan_id=plan_id))
        # Загрузка файла
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                # Проверка файла
                if request.form.get("file_check"):
                    return redirect(
                        url_for(
                            "plans.matrix_indicator_load",
                            plan_id=plan_id,
                            filename=filename,
                        )
                    )
        # Загрузка данных
        if request.form.get("file_load"):
            # Загрузка связей
            if request.form.get("switch_relations"):
                comp_relations_counter = 0
                for disc in match_data:
                    if match_data[disc].get("comps"):
                        for comp in match_data[disc].get("comps"):
                            resp = await discipline_competency_add(
                                match_data[disc].get("id"),
                                match_data[disc]["comps"][comp].get("id"),
                            )
                            if resp.get("data"):
                                comp_relations_counter += int(resp.get("data"))
                flash(
                    "Добавлены связи дисциплин и "
                    f"компетенций - {comp_relations_counter}",
                    category="success",
                )
            # Загрузка данных в рабочие программы
            if request.form.get("switch_programs"):
                resp = await work_programs_competencies_level_del(
                    level_id=plan.program_comp_level_delete
                )
                level_delete_counter = resp.get("data")
                flash(
                    "Удалены лишние уровни формирования "
                    f"компетенций - {level_delete_counter}",
                    category="success",
                )

                comp_add_counter = 0
                # Очищаем ранее загруженные в программу данные
                await plan_competencies_data_cleanup(
                    plan_id,
                    plan.plan_curriculum_disciplines,
                    plan_comp=False,
                    relations=False,
                    work_program=True,
                )
                for comp_data in program_competency_add:
                    resp = await work_program_competency_data_add(comp_data)
                    if resp.get("data"):
                        comp_add_counter += int(resp.get("data"))
                flash(
                    "Добавлена информация об индикаторах компетенций "
                    f"в рабочие программы - {comp_add_counter}",
                    category="success",
                )

                level_add_counter = 0
                for level_add in program_comp_level_add:

                    resp = await work_program_competency_level_add(level_add)
                    if resp.get("data"):
                        level_add_counter += int(resp.get("data"))
                flash(
                    "Добавлены отсутствовавшие уровни формирования "
                    f"компетенций - {level_add_counter}",
                    category="success",
                )

                level_edit_counter = 0
                for wp in program_comp_level_edit:
                    resp = await work_program_competency_level_edit(
                        work_program_id=wp, fields=program_comp_level_edit[wp]
                    )
                    if resp.get("data"):
                        level_edit_counter += int(resp.get("data"))
                flash(
                    "Отредактированы уровни формирования "
                    f"компетенций - {level_edit_counter}",
                    category="success",
                )

            if not request.form.get("switch_relations") and not request.form.get(
                "switch_programs"
            ):
                flash(
                    "Ничего не загружено, т.к. все опции были выключены",
                    category="warning",
                )
            os.remove(file)
            return redirect(url_for("plans.matrix_indicator_load", plan_id=plan_id))
    return render_template(
        "plans/matrix_indicator_load.html",
        active="plans",
        form=form,
        url=Apeks.URL,
        plan_id=plan_id,
        plan_name=plan.name,
        plan_relations=plan.named_disc_comp_relations(),
        program_non_exist=plan.non_exist,
        program_duplicate=plan.duplicate,
        program_wrong_name=plan.wrong_name,
        plan_no_control_data=plan.plan_no_control_data,
        program_control_extra_levels=program_control_extra_levels,
        match_data=match_data,
        indicator_errors=indicator_errors,
        comp_not_in_file=comp_not_in_file,
        comp_not_in_plan=comp_not_in_plan,
    )


@bp.route("/matrix_indicator_file", methods=["GET", "POST"])
@login_required
def matrix_indicator_file():
    form = IndicatorsFileForm()
    filename = request.args.get("filename")
    indicator_errors, report_data = None, None
    if filename:
        file = os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename)
        processor = MatrixFileProcessor(file)
        report_data, indicator_errors = processor.get_file_report_data()
    if request.method == "POST":
        if request.files["file"]:
            new_file = request.files["file"]
            if new_file and allowed_file(new_file.filename):
                filename = new_file.filename
                new_file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("file_check"):
                    return redirect(
                        url_for("plans.matrix_indicator_file", filename=filename)
                    )
        if request.form.get("generate_report"):
            report_filename = filename.rsplit(".", 1)[0]
            report = generate_indicators_file(report_filename, report_data)
            return redirect(url_for("main.get_file", filename=report))
    return render_template(
        "plans/indicator_file.html",
        active="plans",
        report_data=report_data,
        indicator_errors=indicator_errors,
        form=form,
        filename=filename,
    )
