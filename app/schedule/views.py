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

                        # получаем список имен групп и сортируем их
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

                            logging.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                            logging.info(group)
                            logging.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')



                            return render_template('schedule/disc_group_shced.html', active='schedule', form=form, department=department, discipline=discipline, group=group)





                    # получаем список id учебных планов для выбранной дисциплины
                    # curriculum_disciplines_service = get_apeks_db_plan_curriculum_disciplines_service()
                    # education_plan_ids = await curriculum_disciplines_service.get_education_plan_ids_for_discipline(discipline)

                    # получаем список групп у которых была выбранная дисциплина
                    # load_groups_service = get_apeks_load_groups_service()
                    # groups = []
                    # for education_plan_id in education_plan_ids:
                    #     group = await load_groups_service.get(education_plan_id=education_plan_id)
                    #     groups.extend(group)
                    # groups = [{item['id']: item['name']} for item in groups]
                    # logging.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                    # logging.info(groups)
                    # logging.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')


                    # lessons_service = get_apeks_schedule_schedule_student_service()
                    # # lessons = await lessons_service.get(group_id, month, year)
                    # # lessons = await lessons_service.get(group_id=506)
                    # lessons = await lessons_service.get(year=2026, group_id=506)

                    

                    return render_template('schedule/disc_group_shced.html', active='schedule', form=form, department=department, discipline=discipline)




                return render_template('schedule/disc_group_shced.html', active='schedule', form=form, department=department)
            




    return render_template('schedule/disc_group_shced.html', active='schedult', form=form)
