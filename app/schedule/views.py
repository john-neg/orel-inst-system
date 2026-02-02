from datetime import date
import logging
from datetime import datetime

from flask import flash, redirect, render_template, request, url_for

from config import ApeksConfig as Apeks
from . import bp
from .forms import CalendarForm, DisciplineForm
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
from ..core.func.staff import get_state_staff
from ..core.reports.schedule_ical import generate_schedule_ical
from ..core.reports.schedule_xlsx import generate_schedule_xlsx
from ..core.services.apeks_db_state_departments_service import get_db_apeks_state_departments_service
from ..core.services.apeks_db_plan_disciplines_service import get_apeks_db_plan_disciplines_service
from ..core.services.apeks_db_schedule_day_schedule_lessons_service import get_apeks_db_schedule_day_schedule_lessons_service
from ..core.services.apeks_db_load_groups_service import get_apeks_load_groups_service
from ..core.services.apeks_db_schedule_day_schedule_lessons_staff_service import get_apeks_db_schedule_day_schedule_lessons_staff_service
from ..core.services.apeks_db_state_staff_service import get_apeks_db_state_staff_service
from ..core.services.apeks_db_state_special_ranks_service import get_apeks_db_state_special_ranks_service
from ..core.services.apeks_db_schedule_day_schedule_lessons_classrooms_service import get_apeks_db_schedule_day_schedule_lessons_classrooms_service
from ..core.services.apeks_db_schedule_classrooms import get_apeks_db_schedule_classrooms_service
from ..core.services.apeks_db_schedule_buildings import get_apeks_db_schedule_buildings_service


@bp.route("/schedule", methods=["GET", "POST"])
async def schedule():
    departments_service = get_db_apeks_state_departments_service()
    departments = await departments_service.get_departments(department_filter="kafedra")
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


@bp.route('/disc_group_shced', methods=['GET', 'POST'])
async def disc_group_shced():
    # список кафедр
    departments_service = get_db_apeks_state_departments_service()
    departments = await departments_service.get_departments(department_filter='kafedra')
    
    # форма вывода расписания дисциплины для группы
    form = DisciplineForm()

    # заполняем выпадающий список кафедр
    form.department.choices.extend([(k, v.get('full'), {}) for k, v in departments.items()])

    # определяем начался ли новый учебный год в этом году или нет
    current_date = date.today()
    current_month_day = (current_date.month, current_date.day)
    start_academic_year_month_day = (Apeks.START_ACADEMIC_YEAR.month, Apeks.START_ACADEMIC_YEAR.day)
    if current_month_day < start_academic_year_month_day:
        year = current_date.year - 1
    else:
        year = current_date.year

    # заполняем список с годами за которые будет отображаться расписание
    form.year.choices = [year, year - 1, year - 2]
    # form.year.data = year

    if request.method == 'POST':
        # получаем из формы выбранную кафедру
        department = request.form.get('department')
        discipline = request.form.get('discipline')

        if department:
            if department != '0':  # если кафедра выбрана

                # получаем список дисциплин на кафедре
                disciplines_service = get_apeks_db_plan_disciplines_service()
                disciplines = await disciplines_service.get_disciplines(department)
                # заполняем выпадающий список дисциплин кафедры
                form.discipline.choices = [('0', '-- выберите дисциплину --')]
                form.discipline.choices.extend([(d.get('id'), d.get('name_short')) for d in disciplines])

                if discipline:
                    if discipline != '0':

                        # получаем список пар в выбранном учебном году для выбранной дисциплины
                        year = int(request.form.get('year'))
                        schedule_day_schedule_lessons_service = get_apeks_db_schedule_day_schedule_lessons_service()
                        
                        lessons = await schedule_day_schedule_lessons_service.get_discipline_lessons_for_period(
                            discipline,
                            datetime.strptime(f'{year}-{Apeks.START_ACADEMIC_YEAR.month}-{Apeks.START_ACADEMIC_YEAR.day}', '%Y-%m-%d').date(),
                            datetime.strptime(f'{year + 1}-{Apeks.END_ACADEMIC_YEAR.month}-{Apeks.END_ACADEMIC_YEAR.day}', '%Y-%m-%d').date()
                        )
                        group_ids = list(set([lesson['group_id'] for lesson in lessons]))

                        # получаем список имен групп, сортируем их и добавляем в выпадающий список
                        load_groups_service = get_apeks_load_groups_service()
                        groups = []
                        for group_id in group_ids:
                            group_name = await load_groups_service.get(id=group_id)
                            groups.append({'id': group_id, 'name': group_name[0]['name']})
                        groups = sorted(groups, key=lambda item: item['name'])
                        form.group.choices.extend([(group.get('id'), group.get('name')) for group in groups])

                        group = request.form.get('group')
                        # если выбрали группу
                        if group:

                            # получаем список сопоставляющий пару и преподавателя
                            schedule_day_schedule_lessons_staff_service = get_apeks_db_schedule_day_schedule_lessons_staff_service()
                            schedule_day_schedule_lessons_staff = await schedule_day_schedule_lessons_staff_service.list()
                            # получаем список преподавателей
                            state_staff_service = get_apeks_db_state_staff_service()
                            state_staff = await state_staff_service.list()
                            # получаем список званий
                            state_special_ranks_service = get_apeks_db_state_special_ranks_service()
                            state_special_ranks = await state_special_ranks_service.list()
                            # получаем список сопоставляющий пару и аудиторию
                            schedule_day_schedule_lessons_classrooms_service = get_apeks_db_schedule_day_schedule_lessons_classrooms_service()
                            schedule_day_schedule_lessons_classrooms = await schedule_day_schedule_lessons_classrooms_service.list()
                            # получаем список аудиторий
                            schedule_classrooms_service = get_apeks_db_schedule_classrooms_service()
                            schedule_classrooms = await schedule_classrooms_service.list()
                            # получаем список зданий (корпусов)
                            schedule_buildings_service = get_apeks_db_schedule_buildings_service()
                            schedule_buildings = await schedule_buildings_service.list()

                            schedule = []
                            for lesson in lessons:  # просматриваем все пары
                                if group == lesson['group_id']:  # если пара у группы, которая выбрана
                                    staff = []
                                    # ищем преподавателей ведущих пару
                                    for lesson_staff in schedule_day_schedule_lessons_staff:
                                        if lesson_staff['lesson_id'] == lesson['id']:
                                            for employee in state_staff:
                                                if employee['id'] == lesson_staff['staff_id']:
                                                    staff.append(employee)
                                    # ищем звания преподавателей
                                    for employee in staff:
                                        for rank in state_special_ranks:
                                            if employee['special_rank_id'] == rank['id']:
                                                employee['special_rank_id'] = rank['name_short']
                                    # TODO: сделать сортировку по званиям преподавателей
                                    
                                    classrooms = []
                                    # ищем аудитории в которых проходит пара
                                    for lesson_classroom in schedule_day_schedule_lessons_classrooms:
                                        if lesson_classroom['lesson_id'] == lesson['id']:
                                            for classroom in schedule_classrooms:
                                                if classroom['id'] == lesson_classroom['classroom_id']:
                                                    classrooms.append(classroom)
                                    # ищем корпуса в которых находится аудитории
                                    for classroom in classrooms:
                                        for building in schedule_buildings:
                                            if classroom['building_id'] == building['id']:
                                                classroom['building_id'] = building['name_short']
                                    # TODO: сделать сортировку по букве корпуса и номеру кабинета


                                    schedule_lesson = {
                                        'date': lesson['date'],
                                        'time': '',
                                        'topic_code': lesson['topic_code'],
                                        'topic_name': lesson['topic_name'],
                                        'class_type': '',
                                        'classrooms': classrooms,
                                        'staff': staff
                                    }
                                    schedule.append(schedule_lesson)


                            logging.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                            logging.info(schedule)
                            logging.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                            
                            schedule = sorted(schedule, key=lambda item: item['date'])

                            return render_template('schedule/disc_group_shced.html', active='schedule', form=form, department=department, discipline=discipline, schedule=schedule)

                    return render_template('schedule/disc_group_shced.html', active='schedule', form=form, department=department, discipline=discipline)

                return render_template('schedule/disc_group_shced.html', active='schedule', form=form, department=department)

    return render_template('schedule/disc_group_shced.html', active='schedult', form=form)
