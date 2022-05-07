from datetime import date

from flask import render_template, request, redirect, url_for

from app.common.EducationStaff import EducationStaff
from app.common.func import get_departments
from app.schedule import bp
from app.schedule.forms import CalendarForm
from app.schedule.func import lessons_ical_exp, lessons_xlsx_exp


@bp.route("/schedule", methods=["GET", "POST"])
def schedule():
    form = CalendarForm()
    form.department.choices = [(k, v[0]) for k, v in get_departments().items()]
    if request.method == "POST":
        staff = EducationStaff(date.today().month, date.today().year)
        if request.form.get("ical_exp") or request.form.get("xlsx_exp"):
            department = request.form.get("department")
            month = request.form.get("month")
            year = request.form.get("year")
            staff_id = request.form.get("prepod")
            staff_name = staff.state_staff.get(staff_id)
            filename = (
                lessons_ical_exp(staff_id, staff_name, month, year)
                if request.form.get("ical_exp")
                else lessons_xlsx_exp(staff_id, staff_name, month, year)
            )
            if filename == "no data":
                form.prepod.choices = list(staff.department_staff(department).items())
                error = f"{staff_name} - нет занятий в указанный период"
                return render_template(
                    "schedule/schedule.html",
                    active="schedule",
                    form=form,
                    department=department,
                    error=error,
                )
            else:
                return redirect(url_for("main.get_file", filename=filename))
        elif request.form["dept_choose"]:
            department = request.form.get("department")
            form.prepod.choices = list(staff.department_staff(department).items())
            return render_template(
                "schedule/schedule.html",
                active="schedule",
                form=form,
                department=department,
            )
    return render_template("schedule/schedule.html", active="schedule", form=form)
