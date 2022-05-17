from datetime import date

from flask import render_template, request, redirect, url_for, flash
from flask.views import View
from flask_login import login_required

from app.common.classes.EducationPlanExtended import EducationPlanExtended
from app.common.func import get_departments, check_api_db_response, api_get_db_table, \
    get_plan_curriculum_disciplines, get_organization_name, get_organization_chief_info, \
    get_rank_name
from app.main.func import education_specialty, education_plans, db_filter_req
from app.main.models import EducationPlan
from app.plans.func import create_wp
from app.programs import bp
from app.programs.forms import (
    WorkProgramDatesUpdate,
    FieldsForm,
    ChoosePlan,
    DepartmentWPCheck,
    WorkProgramFieldUpdate,
    TitlePagesGenerator,
)
from app.programs.func import wp_update_list, wp_dates_update
from app.programs.models import WorkProgramBunchData, WorkProgram
from config import ApeksConfig as Apeks


class ProgramsChoosePlanView(View):
    methods = ["GET", "POST"]

    def __init__(self, wp_type, title):
        self.template_name = "programs/programs_choose_plan.html"
        self.wp_type = wp_type
        self.title = title

    @login_required
    def dispatch_request(self):
        form = ChoosePlan()
        form.edu_spec.choices = list(education_specialty().items())
        if request.method == "POST":
            edu_spec = request.form.get("edu_spec")
            form.edu_plan.choices = list(education_plans(edu_spec).items())
            if request.form.get("edu_plan") and form.validate_on_submit():
                edu_plan = request.form.get("edu_plan")
                return redirect(
                    url_for(
                        f"programs.{self.wp_type}",
                        plan_id=edu_plan,
                    )
                )
            return render_template(
                self.template_name,
                active="programs",
                title=self.title,
                form=form,
                edu_spec=edu_spec,
            )
        return render_template(
            self.template_name,
            active="programs",
            title=self.title,
            form=form,
        )


bp.add_url_rule(
    "/wp_fields_choose_plan",
    view_func=ProgramsChoosePlanView.as_view(
        "wp_fields_choose_plan",
        wp_type="wp_fields",
        title="Сводная информация по полям рабочих программ плана",
    ),
)

bp.add_url_rule(
    "/wp_data_choose_plan",
    view_func=ProgramsChoosePlanView.as_view(
        "wp_data_choose_plan",
        wp_type="wp_data",
        title="Информация по рабочим программам учебного плана",
    ),
)

bp.add_url_rule(
    "/wp_title_choose_plan",
    view_func=ProgramsChoosePlanView.as_view(
        "wp_title_choose_plan",
        wp_type="wp_title",
        title="Формирование титульных листов рабочих программ",
    ),
)


@bp.route("/dept_check", methods=["GET", "POST"])
async def dept_check():
    form = DepartmentWPCheck()
    departments = await get_departments()
    form.department.choices = [(k, v.get('full')) for k, v in departments.items()]
    form.edu_spec.choices = list(education_specialty().items())
    if request.method == "POST":
        wp_data = {}
        edu_spec = request.form.get("edu_spec")
        department = request.form.get("department")
        year = request.form.get("year")
        wp_field = request.form.get("wp_fields")
        plan_list = education_plans(edu_spec, year)
        if plan_list:
            for plan_id in plan_list:
                plan_wp_data = WorkProgramBunchData(plan_id, wp_field)
                wp_data[plan_list[plan_id]] = plan_wp_data.department(department)
        else:
            wp_data = {"Нет планов": {"Нет дисциплин": "Информация отсутствует"}}
        return render_template(
            "programs/dept_check.html",
            active="programs",
            form=form,
            edu_spec=edu_spec,
            department=department,
            year=year,
            wp_field=wp_field,
            wp_data=wp_data,
        )
    return render_template("programs/dept_check.html", active="programs", form=form)


@bp.route("/dates_update", methods=["GET", "POST"])
@login_required
def dates_update():
    form = WorkProgramDatesUpdate()
    form.edu_spec.choices = list(education_specialty().items())
    if request.method == "POST":
        edu_spec = request.form.get("edu_spec")
        form.edu_plan.choices = list(education_plans(edu_spec).items())
        if request.form.get("wp_dates_update") and form.validate_on_submit():
            edu_plan = request.form.get("edu_plan")
            date_methodical = (
                request.form.get("date_methodical")
                if request.form.get("date_methodical")
                else ""
            )
            document_methodical = (
                request.form.get("document_methodical")
                if request.form.get("document_methodical")
                else ""
            )
            date_academic = (
                request.form.get("date_academic")
                if request.form.get("date_academic")
                else ""
            )
            document_academic = (
                request.form.get("document_academic")
                if request.form.get("document_academic")
                else ""
            )
            date_approval = (
                request.form.get("date_approval")
                if request.form.get("date_approval")
                else ""
            )
            disciplines, non_exist = wp_update_list(edu_plan)
            results = []
            for disc in disciplines:
                load_info = wp_dates_update(
                    disc,
                    date_methodical,
                    document_methodical,
                    date_academic,
                    document_academic,
                    date_approval,
                )
                if load_info == 1:
                    results.append(disciplines[disc])
            return render_template(
                "programs/dates_update.html",
                active="programs",
                form=form,
                edu_plan=edu_plan,
                edu_spec=edu_spec,
                results=results,
                non_exist=non_exist,
            )
        else:
            return render_template(
                "programs/dates_update.html",
                active="programs",
                form=form,
                edu_spec=edu_spec,
            )
    return render_template("programs/dates_update.html", active="programs", form=form)


@bp.route("/wp_fields/<int:plan_id>", methods=["GET", "POST"])
@login_required
def wp_fields(plan_id):
    form = FieldsForm()
    plan_name = db_filter_req("plan_education_plans", "id", plan_id)[0]["name"]
    if request.method == "POST":
        wp_field = request.form.get("wp_fields")
        wp_plan_data = WorkProgramBunchData(plan_id, wp_field)
        wp_data = wp_plan_data.all()
        return render_template(
            "programs/wp_fields.html",
            active="programs",
            form=form,
            plan_name=plan_name,
            wp_field=wp_field,
            wp_data=wp_data,
        )
    return render_template(
        "programs/wp_fields.html", active="programs", form=form, plan_name=plan_name
    )


@bp.route("/wp_field_edit", methods=["GET", "POST"])
@login_required
def wp_field_edit():
    form = WorkProgramFieldUpdate()
    disc_id = request.args.get("disc_id")
    parameter = request.args.get("parameter")
    wp = WorkProgram(disc_id)
    if request.method == "POST":
        parameter = request.form.get("wp_fields")

        if request.form.get("field_update") and form.validate_on_submit():
            load_data = request.form.get("wp_field_edit")
            wp.edit(parameter, load_data)
            flash("Данные обновлены")
    form.wp_fields.data = parameter
    try:
        wp_field_data = wp.get(parameter)
    except IndexError:
        wp_field_data = ""
    form.wp_field_edit.data = wp_field_data

    return render_template(
        "programs/wp_field_edit.html",
        active="programs",
        form=form,
        wp_name=wp.get("name"),
    )


@bp.route("/wp_data/<int:plan_id>", methods=["GET", "POST"])
@login_required
def wp_data(plan_id):
    plan = EducationPlan(plan_id)
    button = ""
    plan_name = plan.name
    wp_list = {}
    no_program = {}
    for disc in plan.disciplines:
        try:
            wp = WorkProgram(disc)
            if request.method == "POST" and request.form.get("wp_status_0"):
                button = "wp_status_0"
                wp.edit("status", 0)
            elif request.method == "POST" and request.form.get("wp_status_1"):
                wp.edit("status", 1)
                button = "wp_status_1"
            wp_list[disc] = [
                wp.name, wp.get_signs(), wp.get("status"), wp.work_program_id
            ]
        except IndexError:
            if request.method == "POST" and request.form.get("create_wp"):
                button = "create_wp"
                create_wp(disc)
                wp = WorkProgram(disc)
                wp_list[disc] = [
                    wp.name, wp.get_signs(), wp.get("status"), wp.work_program_id
                ]
            else:
                no_program[disc] = plan.discipline_name(disc)
    return render_template(
        "programs/wp_data.html",
        active="programs",
        wp_list=wp_list,
        no_program=no_program,
        plan_name=plan_name,
        button=button,
    )


@bp.route("/wp_title/<int:plan_id>", methods=["GET", "POST"])
@login_required
async def wp_title(plan_id):
    plan = EducationPlanExtended(
        education_plan_id=plan_id,
        plan_education_plans=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("plan_education_plans"),
                                   id=plan_id)),
        plan_curriculum_disciplines=await get_plan_curriculum_disciplines(plan_id),
        plan_education_levels=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("plan_education_levels"))),
        plan_education_specialties=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("plan_education_specialties"))),
        plan_education_groups=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("plan_education_groups"))),
        plan_education_specializations=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("plan_education_specializations"))),
        plan_education_plans_education_forms=await check_api_db_response(
            await api_get_db_table(
                Apeks.TABLES.get("plan_education_plans_education_forms"))),
        plan_education_forms=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("plan_education_forms"))),
        plan_qualifications=await check_api_db_response(
            await api_get_db_table(Apeks.TABLES.get("plan_qualifications"))),
        plan_education_specializations_narrow=await check_api_db_response(
            await api_get_db_table(
                Apeks.TABLES.get("plan_education_specializations_narrow"))),
    )
    plan_name = plan.name
    form = TitlePagesGenerator()
    organization_name = await get_organization_name()
    chief_info = await get_organization_chief_info()
    chief_rank = await get_rank_name(chief_info.get('specialRank'))
    approval_date = date.fromisoformat(plan.approval_date)
    full_spec_code = (f"{plan.education_group_code}."
                      f"{plan.education_level_code}."
                      f"{plan.specialty_code}")
    form.organization_name.data = organization_name.upper()
    form.chief_rank.data = chief_rank[0]
    form.chief_name.data = chief_info.get('name_short')
    form.wp_approval_day.data = approval_date.day
    form.wp_approval_month.data = str(approval_date.month)
    form.wp_approval_year.data = approval_date.year
    form.wp_speciality_type.data = "bak" if plan.specialty_code == '02' else "spec"
    form.wp_speciality.data = f"{full_spec_code} {plan.specialty}"
    form.wp_specialization_type.data = "bak" if plan.specialty_code == '02' else "spec"
    form.wp_specialization.data = plan.specialization
    form.wp_education_form.data = plan.education_form
    form.wp_year.data = approval_date.year
    form.wp_qualification.data = plan.qualification
    form.wp_narrow_specialization.data = plan.specialization_narrow
    if request.method == "POST":
        data = dict(request.form)
        del data['csrf_token']
        del data['fields_data']
        print(data)
    return render_template(
        "programs/wp_title.html",
        active="programs",
        plan_name=plan_name,
        form=form,
    )
