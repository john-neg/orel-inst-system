import os

from flask import render_template, request, redirect, url_for, flash
from flask.views import View
from flask_login import login_required

from app.common.forms import ChoosePlan
from app.common.func.api_get import (
    get_plan_education_specialties,
    get_education_plans,
)
from app.common.func.app_core import allowed_file
from app.plans import bp
from app.plans.func import (
    comps_file_processing,
    plan_competencies_data_delete,
    get_plan_competency_instance,
    get_plan_indicator_instance,
)
from app.plans.models import MatrixIndicatorsFile
from common.classes.PlanMatrixProcessor import (
    PlanSimpleMatrixProcessor,
    PlanIndicatorMatrixProcessor,
)
from common.reports.plans_comp_matrix import generate_plans_comp_matrix
from config import FlaskConfig
from plans.forms import (
    CompLoadForm,
    IndicatorsFileForm,
    MatrixIndicatorForm,
    MatrixSimpleForm,
)
from plans.func import (
    plan_competency_add,
    discipline_competency_add,
)


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
        file = FlaskConfig.UPLOAD_FILE_DIR + filename
        comps = comps_file_processing(file)
    if request.method == "POST":
        # Шаблон
        if request.form.get("data_template"):
            return redirect(
                url_for("main.get_temp_file", filename="comp_load_temp.xlsx")
            )
        # Полная очистка
        if request.form.get("data_delete"):
            message = await plan_competencies_data_delete(
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
        plan_name=plan.name,
        plan_comp=plan.plan_competencies,
        comps=comps,
    )


@bp.route("/matrix_simple_load/<int:plan_id>", methods=["GET", "POST"])
@login_required
async def matrix_simple_load(plan_id):
    form = MatrixSimpleForm()
    plan = await get_plan_competency_instance(plan_id)
    file, match_data, comp_not_in_file, comp_not_in_plan = (None for _ in range(4))
    filename = request.args.get("filename")
    if filename:
        file = FlaskConfig.UPLOAD_FILE_DIR + filename
        processor = PlanSimpleMatrixProcessor(plan, file)
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
            message = await plan_competencies_data_delete(
                plan_id,
                plan.plan_curriculum_disciplines,
                plan_comp=False,
                relations=True,
                work_program=True,
            )
            flash(message, category="success")
            return redirect(url_for("plans.matrix_simple_load", plan_id=plan_id))
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
    program_wrong_name = plan.wrong_name
    duplicate = plan.duplicate
    non_exist = plan.non_exist
    plan_no_control_data = plan.plan_no_control_data
    program_control_extra_levels = plan.program_control_extra_levels
    (
        file,
        match_data,
        comp_not_in_file,
        comp_not_in_plan,
        indicator_errors,
    ) = (None for _ in range(5))
    filename = request.args.get("filename")
    if filename:
        file = FlaskConfig.UPLOAD_FILE_DIR + filename
        processor = PlanIndicatorMatrixProcessor(plan, file)
        match_data = processor.matrix_match_data
        comp_not_in_file = processor.comp_not_in_file()
        comp_not_in_plan = processor.comp_not_in_plan()
        indicator_errors = processor.indicator_errors
        (
            program_comp_level_add,
            program_comp_level_edit,
            program_competency_add,
        ) = processor.program_load_data()
        program_comp_level_delete = plan.program_comp_level_delete
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
            message = await plan_competencies_data_delete(
                plan_id,
                plan.plan_curriculum_disciplines,
                plan_comp=False,
                relations=True,
                work_program=True,
            )
            flash(message, category="success")
            return redirect(url_for("plans.matrix_indicator_load", plan_id=plan_id))
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
        if request.form.get("file_load"):
            # Загрузка связей
            # for disc in match_data:
            #     if match_data[disc].get("comps"):
            #         for comp in match_data[disc].get("comps"):
            #             await discipline_competency_add(
            #                 match_data[disc].get("id"), match_data[disc]["comps"][comp]
            #             )
            # os.remove(file)
            flash("Данные успешно загружены", category="success")

            # program_comp_level_delete,
            # program_comp_level_add,
            # program_comp_level_edit,
            # program_competency_add

            # if request.form.get("switch_relations") and request.form.get(
            #         "switch_programs"
            # ):
            #     for disc_id in plan.disciplines.keys():
            #         disc_comp_upload(disc_id)
            #         work_program_load(disc_id)
            #     flash("Связи и программы обновлены", category="success")
            # elif request.form.get("switch_relations"):
            #     for disc_id in plan.disciplines.keys():
            #         disc_comp_upload(disc_id)
            #     flash("Связи обновлены", category="success")
            # elif request.form.get("switch_programs"):
            #     for disc_id in plan.disciplines.keys():
            #         work_program_load(disc_id)
            #     flash("Программы обновлены", category="success")
            # else:
            #     flash(
            #         "Ничего не загружено, т.к. все опции были выключены",
            #         category="warning",
            #     )
            # os.remove(file)
            return redirect(url_for("plans.matrix_indicator_load", plan_id=plan_id))
        # return render_template(
        #     "plans/matrix_indicator_load.html",
        #     active="plans",
        #     form=form,
        #     filename=filename,
        #     plan_name=plan.name,
        #     plan_relations=plan.disciplines_comp_dict(),
        #     report=report,
        #     file_errors=matrix.file_errors(),
        #     no_comp_list=no_comp_list,
        # )
    return render_template(
        "plans/matrix_indicator_load.html",
        active="plans",
        form=form,
        plan_name=plan.name,
        plan_relations=plan.named_disc_comp_relations(),
        program_non_exist=plan.non_exist,
        program_duplicate=plan.duplicate,
        program_wrong_name=plan.wrong_name,
        plan_no_control_data=plan_no_control_data,
        program_control_extra_levels=program_control_extra_levels,
        match_data=match_data,
        indicator_errors=indicator_errors,
        comp_not_in_file=comp_not_in_file,
        comp_not_in_plan=comp_not_in_plan,
    )


# @bp.route(
#     "/matrix_indicator_check/<int:plan_id>/<string:filename>", methods=["GET", "POST"]
# )
# @login_required
# def matrix_indicator_check(plan_id, filename):
#     file = FlaskConfig.UPLOAD_FILE_DIR + filename
#     plan = CompPlan(plan_id)
#     matrix = MatrixIndicatorsFile(file)
#     form = MatrixIndicatorForm()
#
#     # File check
#     report = {}
#     for disc_id in plan.disciplines:
#         discipline_name = plan.discipline_name(disc_id)
#         if matrix.find_discipline(discipline_name):
#             comp_data = matrix.disc_comp(discipline_name)
#             if comp_data:
#                 report[discipline_name] = list(comp_data.keys())
#             else:
#                 report[discipline_name] = ["None"]
#         else:
#             report[discipline_name] = []
#     # Comp check
#     no_comp_list = []
#     matrix_comp_list = matrix.comp_list()
#     plan_comp_list = plan.get_comp_list()
#     for comp in matrix_comp_list:
#         if comp not in plan_comp_list:
#             no_comp_list.append(comp)
#
#     def disc_load_ids(curriculum_discipline_id):
#         """Получение ID компетенций плана для дисциплины для загрузки."""
#         disc_comp_load = []
#         disc_name = plan.discipline_name(curriculum_discipline_id)
#         compet_data = matrix.disc_comp(disc_name)
#         for compet in compet_data:
#             for v in range(len(plan.competencies)):
#                 if compet == plan.competencies[v]["code"]:
#                     disc_comp_load.append(plan.competencies[v]["id"])
#         return disc_comp_load
#
#     def disc_comp_upload(curriculum_discipline_id):
#         """Загрузка связей дисциплин и компетенций из файла в план."""
#         for compet in disc_load_ids(curriculum_discipline_id):
#             disciplines_comp_load(curriculum_discipline_id, compet)
#
#     def work_program_load(curriculum_discipline_id):
#         """Загрузка индикаторов в программу"""
#         wp = WorkProgramProcessing(curriculum_discipline_id)
#         wp.comp_data_del()
#         disc_name = plan.discipline_name(curriculum_discipline_id)
#         compet_data = matrix.disc_comp(disc_name)
#         fields = {1: "knowledge", 2: "abilities", 3: "ownerships"}
#         knowledge, abilities, ownerships = [], [], []
#
#         for compet in compet_data.keys():
#             for v in range(len(plan.competencies)):
#                 if compet == plan.competencies[v]["code"]:
#                     competency_id = plan.competencies[v]["id"]
#                     for f in fields:
#                         value = ";\n".join(compet_data[compet][fields[f]])
#                         if value:
#                             wp.comp_data_add(competency_id, f, value)
#
#             knowledge += compet_data[compet]["knowledge"]
#             abilities += compet_data[compet]["abilities"]
#             ownerships += compet_data[compet]["ownerships"]
#
#         wp.comp_level_edit(
#             ";\n".join(knowledge), ";\n".join(abilities), ";\n".join(ownerships)
#         )
#
#     if request.method == "POST":
#         # Шаблон
#         if request.form.get("data_template"):
#             return redirect(
#                 url_for("main.get_temp_file", filename="matrix_ind_temp.xlsx")
#             )
#         # Текущая матрица
#         if request.form.get("make_matrix"):
#             return redirect(url_for("main.get_file", filename=plan.matrix_generate()))
#         # Удаление связей
#         if request.form.get("data_delete"):
#             plan.matrix_delete()
#             flash("Все связи удалены", category="success")
#             return redirect(url_for("plans.matrix_indicator_load", plan_id=plan_id))
#         if request.files["file"]:
#             file = request.files["file"]
#             if file and allowed_file(file.filename):
#                 filename = file.filename
#                 file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
#                 # Проверка файла
#                 if request.form.get("file_check"):
#                     return redirect(
#                         url_for(
#                             "plans.matrix_indicator_check",
#                             plan_id=plan_id,
#                             filename=filename,
#                         )
#                     )
#         if request.form.get("file_load"):
#             if request.form.get("switch_relations") and request.form.get(
#                 "switch_programs"
#             ):
#                 for disc_id in plan.disciplines.keys():
#                     disc_comp_upload(disc_id)
#                     work_program_load(disc_id)
#                 flash("Связи и программы обновлены", category="success")
#             elif request.form.get("switch_relations"):
#                 for disc_id in plan.disciplines.keys():
#                     disc_comp_upload(disc_id)
#                 flash("Связи обновлены", category="success")
#             elif request.form.get("switch_programs"):
#                 for disc_id in plan.disciplines.keys():
#                     work_program_load(disc_id)
#                 flash("Программы обновлены", category="success")
#             else:
#                 flash(
#                     "Ничего не загружено, т.к. все опции были выключены",
#                     category="warning",
#                 )
#             os.remove(file)
#             return redirect(url_for("plans.matrix_indicator_load", plan_id=plan_id))
#     return render_template(
#         "plans/matrix_indicator_load.html",
#         active="plans",
#         form=form,
#         filename=filename,
#         plan_name=plan.name,
#         plan_relations=plan.disciplines_comp_dict(),
#         report=report,
#         file_errors=matrix.file_errors(),
#         no_comp_list=no_comp_list,
#     )


@bp.route("/matrix_indicator_file", methods=["GET", "POST"])
@login_required
def matrix_indicator_file():
    form = IndicatorsFileForm()
    if request.method == "POST":
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                if request.form.get("file_check"):
                    return redirect(
                        url_for("plans.matrix_indicator_file_check", filename=filename)
                    )
    return render_template(
        "plans/indicator_file.html",
        active="plans",
        form=form,
    )


@bp.route("/matrix_indicator_file_check/<string:filename>", methods=["GET", "POST"])
@login_required
def matrix_indicator_file_check(filename):
    form = IndicatorsFileForm()
    file = FlaskConfig.UPLOAD_FILE_DIR + filename
    matrix = MatrixIndicatorsFile(file)
    if request.method == "POST":
        if request.files["file"]:
            file = request.files["file"]
            if file and allowed_file(file.filename):
                filename = file.filename
                file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
                file_path = FlaskConfig.UPLOAD_FILE_DIR + filename
                if request.form.get("file_check"):
                    return redirect(
                        url_for("plans.matrix_indicator_file_check", filename=filename)
                    )
                if request.form.get("generate_report"):
                    matrix = MatrixIndicatorsFile(file_path)
                    filename = matrix.list_to_word()
                    os.remove(file_path)
                    return redirect(url_for("main.get_file", filename=filename))
    if request.form.get("generate_report"):
        filename = matrix.list_to_word()
        os.remove(file)
        flash("Файл отправлен", category="success")
        return redirect(url_for("main.get_file", filename=filename))
    return render_template(
        "plans/indicator_file.html",
        active="plans",
        file_errors=matrix.file_errors(),
        message="Ошибки не обнаружены",
        form=form,
        filename=filename,
    )
