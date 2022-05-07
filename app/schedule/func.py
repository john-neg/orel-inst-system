from __future__ import annotations

import logging
from datetime import datetime, timedelta

import pytz
import xlsxwriter
from icalendar import Calendar, Timezone, TimezoneStandard, Event, Alarm

from app.common.ScheduleLessonsStaff import ScheduleLessonsStaff
from config import FlaskConfig, ApeksConfig as Apeks


def lessons_ical_exp(
    staff_id: int | str, staff_name: str, month: int | str, year: int | str
) -> str:
    """Формирование файла для экспорта занятий преподавателя в формате iCal."""
    lessons = ScheduleLessonsStaff(staff_id, month, year)

    # TODO make exception here
    if not lessons.data:
        return "no data"

    cal = Calendar()
    cal.add("calscale", "GREGORIAN")
    cal.add("version", "2.0")
    cal.add("prodid", "APEKS-VUZ-EXTENSION")
    timezone = Timezone()
    timezone.add("TZID", Apeks.TIMEZONE)
    tz_standard = TimezoneStandard()
    tz_standard.add("TZNAME", datetime.now(tz=Apeks.TIMEZONE).strftime("%Z"))
    tz_standard.add("TZOFFSETFROM", timedelta(hours=Apeks.TIMEZONE_OFFSET))
    tz_standard.add("TZOFFSETTO", timedelta(hours=Apeks.TIMEZONE_OFFSET))
    timezone.add_component(tz_standard)
    cal.add_component(timezone)

    for l_index in range(len(lessons.data)):
        event = Event()
        event.add("dtstart", lessons.time_start(l_index).astimezone(pytz.utc))
        event.add("dtend", lessons.time_end(l_index).astimezone(pytz.utc))
        event.add("dtstamp", datetime.now().astimezone(pytz.utc))
        event.add(
            "description",
            f"т.{lessons.data[l_index].get('topic_code')} "
            f"{lessons.data[l_index].get('topic_name')}\n\n"
            f"Данные актуальны на: {datetime.now()}",
        )
        event.add("location", lessons.data[l_index].get("classroom"))
        event.add("status", "CONFIRMED")
        event.add("summary", lessons.calendar_name(l_index))
        event.add(
            "uid",
            f'apeks-id-{lessons.data[l_index].get("id")}'
            f'journal-lesson-id-{lessons.data[l_index].get("journal_lesson_id")}',
        )
        alarm = Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add("description", "Напоминание")
        alarm.add("trigger", timedelta(minutes=-30))
        event.add_component(alarm)
        cal.add_component(event)

    filename = f"{staff_name} {month}-{year}.ics"

    with open(
        f"{FlaskConfig.EXPORT_FILE_DIR}{filename}",
        "wb",
    ) as f:
        f.write(cal.to_ical())
        f.close()
        logging.debug(f'Файл "{filename}" успешно сформирован')
    return filename


def lessons_xlsx_exp(
    staff_id: int | str, staff_name: str, month: int | str, year: int | str
) -> str:
    """Формирование файла для экспорта занятий преподавателя в формате xlsx."""
    lessons = ScheduleLessonsStaff(staff_id, month, year)

    if not lessons.data:
        return "no data"
    else:
        filename = f"{staff_name} {month}-{year}.xlsx"
        workbook = xlsxwriter.Workbook(f"{FlaskConfig.EXPORT_FILE_DIR}{filename}")
        worksheet = workbook.add_worksheet(staff_name)
        bold = workbook.add_format({"bold": True})
        worksheet.write("A1", staff_name, bold)
        worksheet.write("B1", f"Расписание на месяц {str(month)}-{str(year)}", bold)

        # Отступ сверху
        a = str(3)

        # Заголовки.
        worksheet.write("A" + a, "Дата/время", bold)
        worksheet.write("B" + a, "Занятие", bold)
        worksheet.write("C" + a, "Место", bold)
        worksheet.write("D" + a, "Тема", bold)

        # Ширина столбцов
        worksheet.set_column(0, 0, 15)
        worksheet.set_column(1, 1, 60)
        worksheet.set_column(2, 2, 15)
        worksheet.set_column(3, 3, 70)

        lesson_export = ()
        for l_index in range(len(lessons.data)):
            export = (
                [
                    lessons.time_start(l_index).strftime("%d.%m.%Y %H:%M"),
                    lessons.calendar_name(l_index),
                    lessons.data[l_index]["classroom"],
                    lessons.data[l_index]["topic_name"],
                ],
            )
            lesson_export += export

        # Устанавливаем начальные ячейки для записи (начало с 0).
        row = 3
        col = 0

        # Итерация и запись данных построчно
        for lesson in lesson_export:
            for a in range(len(lesson)):
                worksheet.write(row, col + a, lesson[a])
            row += 1

        workbook.close()
        logging.debug(f'Файл "{filename}" успешно сформирован')
        return filename
