from __future__ import annotations

import logging
from datetime import datetime, timedelta, tzinfo

import pytz
from icalendar import Calendar, Timezone, TimezoneStandard, Event, Alarm

from app.common.classes.ScheduleLessonsStaff import ScheduleLessonsStaff
from config import FlaskConfig, ApeksConfig as Apeks


def generate_schedule_ical(
    schedule: ScheduleLessonsStaff, staff_name: str, timezone: tzinfo = Apeks.TIMEZONE
) -> str:
    """
    Формирует файл для экспорта занятий преподавателя в формате iCal.

    Parameters
    ----------
        schedule
            экземпляр класса ScheduleLessonsStaff
        staff_name:str
            имя преподавателя
        timezone
            устанавливается timezone для календаря

    Returns
    -------
        string
            строка с названием файла или 'no data' если список 'lessons_data' пуст
    """

    if not schedule.lessons_data:
        return "no data"

    cal = Calendar()
    cal.add("calscale", "GREGORIAN")
    cal.add("version", "2.0")
    cal.add("prodid", "APEKS-VUZ-EXTENSION")
    cal_timezone = Timezone()
    cal_timezone.add("TZID", Apeks.TIMEZONE)
    tz_standard = TimezoneStandard()
    tz_standard.add("TZNAME", datetime.now(tz=timezone).strftime("%Z"))
    tz_standard["TZOFFSETFROM"] = datetime.now(tz=timezone).strftime("%z")
    tz_standard["TZOFFSETTO"] = datetime.now(tz=timezone).strftime("%z")
    cal_timezone.add_component(tz_standard)
    cal.add_component(cal_timezone)

    for l_index in range(len(schedule.lessons_data)):
        event = Event()
        event.add("dtstart", schedule.time_start(l_index).astimezone(pytz.utc))
        event.add("dtend", schedule.time_end(l_index).astimezone(pytz.utc))
        event.add("dtstamp", datetime.now().astimezone(pytz.utc))
        event.add(
            "description",
            f"т.{schedule.lessons_data[l_index].get('topic_code')} "
            f"{schedule.lessons_data[l_index].get('topic_name')}\n\n"
            f"Данные актуальны на: {datetime.now().strftime('%H:%M %d.%m.%Y')}",
        )
        event.add("location", schedule.lessons_data[l_index].get("classroom"))
        event.add("status", "CONFIRMED")
        event.add("summary", schedule.calendar_name(l_index))
        event.add(
            "uid",
            f'apeks-id-{schedule.lessons_data[l_index].get("id")}'
            f'journal-lesson-id-{schedule.lessons_data[l_index].get("journal_lesson_id")}',
        )
        group_id = schedule.lessons_data[l_index].get("group_id")
        subgroup_id = schedule.lessons_data[l_index].get("subgroup_id")
        lesson_id = schedule.lessons_data[l_index].get("journal_lesson_id")

        if not group_id:
            if subgroup_id:
                group_id = schedule.load_subgroups_data.get(subgroup_id).get("group_id")

        if group_id and lesson_id:
            event.add(
                "url",
                f"{Apeks.URL}/student/journal/view?group_id={group_id}"
                f"&lesson_id={lesson_id}",
            )
        alarm = Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add("description", "Напоминание")
        alarm.add("trigger", timedelta(minutes=-30))
        event.add_component(alarm)
        cal.add_component(event)

    month_name = Apeks.MONTH_DICT.get(int(schedule.month))
    filename = f"{staff_name} - {month_name} {schedule.year}.ics"

    with open(
        f"{FlaskConfig.EXPORT_FILE_DIR}{filename}",
        "wb",
    ) as f:
        f.write(cal.to_ical())
        f.close()
        logging.debug(f'Файл "{filename}" успешно сформирован')
    return filename
