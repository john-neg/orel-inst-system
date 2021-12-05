import requests
from flask import render_template, request
from flask_login import login_required
from app.plans import bp
from app.plans.forms import ChoosePlan
from app.main.func import education_specialty, education_plans, db_filter_req
from config import ApeksAPI


def comp_delete(education_plan_id):
    data = db_filter_req("plan_competencies", "education_plan_id", education_plan_id)
    # data['data'][0]['id']
    report = []
    for i in range(len(data)):
        payload = {"table": "plan_competencies", "filter[id]": data[i]["id"]}
        remove = requests.delete(
            ApeksAPI.URL + "/api/call/system-database/delete?token=" + ApeksAPI.TOKEN,
            params=payload,
        )
        if remove.json()["status"] == 0:
            report.append(f"{data[i]['code']} - {remove.json()['message']}")
            return report


@bp.route("/competencies_load", methods=["GET", "POST"])
@login_required
def competencies_load():
    form = ChoosePlan()
    form.edu_spec.choices = list(education_specialty().items())
    if request.method == "POST":
        if request.form.get("plan_choose") and request.form.get("edu_spec"):
            edu_spec = request.form.get("edu_spec")
            edu_plan = request.form.get("edu_plan")
            form.edu_plan.choices = list(education_plans(edu_spec).items())
            return render_template(
                "plans/competencies_load.html",
                active="plans",
                form=form,
                edu_plan=edu_plan,
                edu_spec=edu_spec,
            )
        elif request.form.get("edu_spec"):
            edu_spec = request.form.get("edu_spec")
            form.edu_plan.choices = list(education_plans(edu_spec).items())
            return render_template(
                "plans/competencies_load.html", active="plans", form=form, edu_spec=edu_spec
            )
    return render_template("plans/competencies_load.html", active="plans", form=form)
