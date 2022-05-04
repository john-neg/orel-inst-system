import xlsxwriter
from flask import render_template, request, redirect, url_for
from app.schedule import bp
from app.schedule.forms import CalendarForm
from app.schedule.models import ApeksStaffData, ApeksLessons
from config import FlaskConfig


@bp.route("/schedule", methods=["GET", "POST"])
def schedule():
    apeks = ApeksStaffData()

    def lessons_ical_exp(department_id, staff_id, month, year):
        """Формирование данных для экспорта iCAl."""
        lessons = ApeksLessons(staff_id, month, year)

        if not lessons.data:
            return "no data"
        else:
            lines = [
                "BEGIN:VCALENDAR",
                "VERSION:2.0",
                "CALSCALE:GREGORIAN",
                "METHOD:PUBLISH",
                "X-WR-TIMEZONE:Europe/Moscow",
                "BEGIN:VTIMEZONE",
                "TZID:Europe/Moscow",
                "X-LIC-LOCATION:Europe/Moscow",
                "BEGIN:STANDARD",
                "TZOFFSETFROM:+0300",
                "TZOFFSETTO:+0300",
                "TZNAME:MSK",
                "DTSTART:19700101T000000",
                "END:STANDARD",
                "END:VTIMEZONE",
                "BEGIN:VTIMEZONE",
                "TZID:Europe/Minsk",
                "X-LIC-LOCATION:Europe/Minsk",
                "BEGIN:STANDARD",
                "TZOFFSETFROM:+0300",
                "TZOFFSETTO:+0300",
                "TZNAME:+03",
                "DTSTART:19700101T000000",
                "END:STANDARD",
                "END:VTIMEZONE",
            ]

            with open(
                f"{FlaskConfig.EXPORT_FILE_DIR}{apeks.staff_name(staff_id, department_id)}"
                f" {month}-{year}.ics",
                "w",
            ) as f:
                for line in lines:
                    f.write(line)
                    f.write("\n")
                f.write("\n")
                for lesson in range(len(lessons.data)):
                    f.write("BEGIN:VEVENT" + "\n")
                    f.write("DTSTART:" + lessons.time_ical('start', lesson) + "\n")
                    f.write("DTEND:" + lessons.time_ical('end', lesson) + "\n")
                    f.write(
                        "DESCRIPTION:"
                        + lessons.topic_code(lesson)
                        + lessons.topic_name(lesson)
                        + "\n"
                    )
                    f.write("LOCATION:" + lessons.data[lesson]["classroom"] + "\n")
                    f.write("SEQUENCE:0" + "\n")
                    f.write("STATUS:CONFIRMED" + "\n")
                    f.write("SUMMARY:" + lessons.calendar_name(lesson) + "\n")
                    f.write("TRANSP:OPAQUE" + "\n")
                    f.write("BEGIN:VALARM" + "\n")
                    f.write("ACTION:DISPLAY" + "\n")
                    f.write("DESCRIPTION:This is an event reminder" + "\n")
                    f.write("TRIGGER:-P0DT0H30M0S" + "\n")
                    f.write("END:VALARM" + "\n")
                    f.write("END:VEVENT" + "\n")
                    f.write("\n")
                f.write("END:VCALENDAR")
            f.close()
        return f"{apeks.staff_name(staff_id, department_id)} {month}-{year}.ics"

    def lessons_xlsx_exp(department_id, staff_id, month, year):
        """Выгрузка занятий в формате xlsx."""
        lessons = ApeksLessons(staff_id, month, year)

        if not lessons.data:
            return "no data"
        else:
            workbook = xlsxwriter.Workbook(
                f"{FlaskConfig.EXPORT_FILE_DIR}{apeks.staff_name(staff_id, department_id)}"
                f" {month}-{year}.xlsx"
            )
            worksheet = workbook.add_worksheet(
                apeks.staff_name(staff_id, department_id)
            )

            bold = workbook.add_format({"bold": True})
            worksheet.write(
                "A1", "Расписание на месяц " + str(month) + "-" + str(year), bold
            )
            worksheet.write("B1", apeks.staff_name(staff_id, department_id), bold)

            a = str(3)  # отступ сверху

            # Write some data headers.
            worksheet.write("A" + a, "Дата/время", bold)
            worksheet.write("B" + a, "Занятие", bold)
            worksheet.write("C" + a, "Место", bold)
            worksheet.write("D" + a, "Тема", bold)

            # Worksheet set columns width
            worksheet.set_column(0, 0, 15)
            worksheet.set_column(1, 1, 60)
            worksheet.set_column(2, 2, 15)
            worksheet.set_column(3, 4, 50)

            # Some data we want to write to the worksheet.
            lesson_export = ()
            for lesson in range(len(lessons.data)):
                export = (
                    [
                        lessons.time_start_xlsx(lesson),
                        lessons.calendar_name(lesson),
                        lessons.data[lesson]["classroom"],
                        lessons.topic_name(lesson),
                    ],
                )
                lesson_export += export

            # Start from the first cell below the headers.
            row = 3
            col = 0

            # Iterate over the data and write it out row by row.
            for lesson in lesson_export:
                for a in range(len(lesson)):
                    worksheet.write(row, col + a, lesson[a])
                row += 1

            workbook.close()
            return f"{apeks.staff_name(staff_id, department_id)} {month}-{year}.xlsx"

    form = CalendarForm()
    form.department.choices = list(apeks.departments.items())

    if request.method == "POST":
        if request.form.get("ical_exp") or request.form.get("xlsx_exp"):
            department = request.form.get("department")
            month = request.form.get("month")
            year = request.form.get("year")
            prepod = request.form.get("prepod")
            filename = (
                lessons_ical_exp(department, prepod, month, year)
                if request.form.get("ical_exp")
                else lessons_xlsx_exp(department, prepod, month, year)
            )
            if filename == "no data":
                form.prepod.choices = list(apeks.get_staff(department).items())
                error = f"{apeks.staff_name(prepod, department)}" \
                        f" - нет занятий в указанный период"
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
            form.prepod.choices = list(apeks.get_staff(department).items())
            return render_template(
                "schedule/schedule.html",
                active="schedule",
                form=form,
                department=department,
            )
    return render_template("schedule/schedule.html", active="schedule", form=form)
