import logging
from datetime import date

from flask import render_template, request, redirect, url_for

from app.common.classes.EducationStaff import EducationStaff
from app.common.classes.ScheduleLessonsStaff import ScheduleLessonsStaff
from app.common.func import (
    get_departments,
    get_state_staff,
    check_api_db_response,
    api_get_db_table,
    check_api_staff_lessons_response,
    api_get_staff_lessons,
    get_disciplines,
    data_processor,
)
from app.common.reports.schedule_ical import generate_schedule_ical
from app.common.reports.schedule_xlsx import generate_schedule_xlsx
from app.schedule import bp
from app.schedule.forms import CalendarForm
from config import ApeksConfig as Apeks


@bp.route("/schedule", methods=["GET", "POST"])
async def schedule():
    form = CalendarForm()
    departments = await get_departments()
    form.department.choices = [(k, v.get("full")) for k, v in departments.items()]
    if request.method == "POST":
        department = request.form.get("department")
        state_staff = await get_state_staff()
        staff = EducationStaff(
            year=date.today().year,
            month_start=date.today().month - 1,
            month_end=date.today().month,
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
                disciplines=await get_disciplines(),
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
        return render_template(
            "schedule/schedule.html",
            active="schedule",
            form=form,
            department=department,
        )
    return render_template("schedule/schedule.html", active="schedule", form=form)
