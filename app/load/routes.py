from flask import render_template, request, url_for
from werkzeug.utils import redirect

from app.load import bp
from app.load.forms import LoadReportForm
from app.load.models import LoadReport
from app.main.func import get_departments


@bp.route("/load", methods=["GET", "POST"])
def load_report():
    form = LoadReportForm()
    form.department.choices = [(d[0], d[1][0]) for d in get_departments().items()]
    if request.method == "POST" and form.validate_on_submit():
        year = request.form.get('year')
        month = request.form.get('month')
        department = request.form.get('department')
        return redirect(
            url_for(
                "load.load_report_export",
                year=year,
                month=month,
                department=department
            )
        )
    return render_template("load/load_report.html", active="load", form=form)


@bp.route(
    "/load_report/<int:year>/<string:month>/<int:department>",
    methods=["GET", "POST"]
)
def load_report_export(year, month, department):
    report = LoadReport(year, month, department)
    report.generate_report()
    return redirect(url_for("main.get_file", filename=report.filename))
