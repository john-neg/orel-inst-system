from datetime import date
import logging

from flask import flash, redirect, render_template, request, url_for

from config import ApeksConfig as Apeks
from . import bp
from .forms import CalendarForm
from ..core.classes.EducationStaff import EducationStaff
from ..core.classes.ScheduleLessonsStaff import ScheduleLessonsStaff
from ..core.func.api_get import (
    api_get_db_table,
    api_get_staff_lessons,
    check_api_db_response,
    check_api_staff_lessons_response,
)
from ..core.func.app_core import data_processor
from ..core.func.education_plan import get_plan_disciplines
from ..core.func.organization import get_departments
from ..core.func.staff import get_state_staff
from ..core.reports.schedule_ical import generate_schedule_ical
from ..core.reports.schedule_xlsx import generate_schedule_xlsx


@bp.route("/schedule", methods=["GET", "POST"])
async def schedule():
    departments = await get_departments(department_filter="kafedra")
    year = date.today().year
    month = date.today().month
    form = CalendarForm()
    form.department.choices = [(k, v.get("full")) for k, v in departments.items()]
    form.year.choices = [year - 1, year, year + 1]
    form.year.data = year
    form.month.data = month
    if request.method == "POST":
        department = request.form.get("department")
        state_staff = await get_state_staff()
        staff = EducationStaff(
            year=date.today().year,
            month_start=month - 6 if month - 6 >= 1 else 1,
            month_end=month + 3 if month + 3 <= 12 else 12,
            state_staff=state_staff,
            state_staff_history=await check_api_db_response(
                await api_get_db_table(
                    Apeks.TABLES.get("state_staff_history"),
                    department_id=department,
                )
            ),
            state_staff_positions=await check_api_db_response(
                await api_get_db_table(Apeks.TABLES.get("state_staff_positions"))
            ),
            departments=departments,
        )

        form.staff.choices = list(staff.department_staff(department).items())
        if (
            request.form.get("ical_exp") or request.form.get("xlsx_exp")
        ) and form.validate_on_submit():
            month = request.form.get("month")
            year = request.form.get("year")
            staff_id = request.form.get("staff")
            try:
                staff_name = staff.state_staff.get(int(staff_id)).get("short")
            except AttributeError:
                logging.error("Не найдено имя преподавателя по staff_id")
                staff_name = "Имя преподавателя отсутствует"
            staff_lessons = ScheduleLessonsStaff(
                staff_id,
                month,
                year,
                lessons_data=await check_api_staff_lessons_response(
                    await api_get_staff_lessons(staff_id, month, year)
                ),
                disciplines=await get_plan_disciplines(),
                load_subgroups_data=data_processor(
                    await check_api_db_response(
                        await api_get_db_table(Apeks.TABLES.get("load_subgroups"))
                    )
                ),
            )
            filename = (
                generate_schedule_ical(staff_lessons, staff_name)
                if request.form.get("ical_exp")
                else generate_schedule_xlsx(staff_lessons, staff_name)
            )
            if filename == "no data":
                flash(
                    f"{staff_name} - нет занятий в указанный период", category="warning"
                )
                return render_template(
                    "schedule/schedule.html",
                    active="schedule",
                    form=form,
                    department=department,
                )
            else:
                return redirect(url_for("main.get_file", filename=filename))
        return render_template(
            "schedule/schedule.html",
            active="schedule",
            form=form,
            department=department,
        )
    return render_template("schedule/schedule.html", active="schedule", form=form)
