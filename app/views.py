import os
from app.func import *
from app.forms import *
from app.models import User
from werkzeug.utils import redirect, secure_filename
from flask import render_template, request, send_file, url_for, send_from_directory
from flask_login import logout_user, login_user, current_user, login_required

from config import FlaskConfig


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', active='index')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            error = 'Неверный логин или пароль'
            return render_template('login.html', title='Авторизация', form=form,
                                   error=error)  # redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    form = CalendarForm()
    form.department.choices = list(ApeksData.departments.items())

    if request.method == 'POST':
        if request.form.get('ical_exp') or request.form.get('xlsx_exp'):
            department = request.form.get('department')
            month = request.form.get('month')
            year = request.form.get('year')
            prepod = request.form.get('prepod')
            filename = lessons_ical_exp(department, prepod, month, year) if request.form.get('ical_exp') \
                else lessons_xlsx_exp(department, prepod, month, year)

            if filename == 'no data':
                form.prepod.choices = list(get_staff(department).items())
                error = f'{staff_name(prepod, department)} - нет занятий в указанный период'
                return render_template('calendar.html', active='calendar',
                                       form=form, department=department, error=error)
            else:
                return redirect(url_for('getfile', filename=filename))
        elif request.form['dept_choose']:  # request.form.get('department'):
            department = request.form.get('department')
            form.prepod.choices = list(get_staff(department).items())
            return render_template('calendar.html', active='calendar', form=form, department=department)

    return render_template('calendar.html', active='calendar', form=form)


@app.route('/programs', methods=['GET', 'POST'])
@login_required
def programs():
    form = WorkProgramUpdate()
    form.edu_spec.choices = list(education_specialty().items())
    if request.method == 'POST':
        if request.form.get('wp_update') and form.validate_on_submit():
            edu_spec = request.form.get('edu_spec')
            form.edu_plan.choices = list(education_plans(edu_spec).items())
            edu_plan = request.form.get('edu_plan')
            date_methodical = request.form.get('date_methodical') if request.form.get('date_methodical') else ''
            document_methodical = request.form.get('document_methodical') if request.form.get(
                'document_methodical') else ''
            date_academic = request.form.get('date_academic') if request.form.get('date_academic') else ''
            document_academic = request.form.get('document_academic') if request.form.get('document_academic') else ''
            date_approval = request.form.get('date_approval') if request.form.get('date_approval') else ''
            disciplines, non_exist = wp_update_list(edu_plan)
            results = []
            for disc in disciplines:
                load_info = wp_update(disc, date_methodical, document_methodical,
                                      date_academic, document_academic, date_approval)
                if load_info == 1:
                    results.append(disciplines[disc])
            return render_template('programs.html', active='programs', form=form,
                                   edu_plan=edu_plan, edu_spec=edu_spec, results=results, non_exist=non_exist)
        elif request.form.get('edu_spec'):
            edu_spec = request.form.get('edu_spec')
            form.edu_plan.choices = list(education_plans(edu_spec).items())
            return render_template('programs.html', active='programs', form=form, edu_spec=edu_spec)
    return render_template('programs.html', active='programs', form=form)


@app.route('/competencies_load', methods=['GET', 'POST'])
@login_required
def competencies_load():
    form = ChoosePlan()
    form.edu_spec.choices = list(education_specialty().items())
    if request.method == 'POST':
        if request.form.get('plan_choose') and request.form.get('edu_spec'):
            edu_spec = request.form.get('edu_spec')
            edu_plan = request.form.get('edu_plan')
            form.edu_plan.choices = list(education_plans(edu_spec).items())
            return render_template('competencies_load.html', active='programs', form=form,
                                   edu_plan=edu_plan, edu_spec=edu_spec)
        elif request.form.get('edu_spec'):
            edu_spec = request.form.get('edu_spec')
            form.edu_plan.choices = list(education_plans(edu_spec).items())
            return render_template('competencies_load.html', active='programs', form=form, edu_spec=edu_spec)
    return render_template('competencies_load.html', active='programs', form=form)


@app.route('/library')
@login_required
def library():
    return render_template('library.html', active='library')


@app.route('/<string:filename>', methods=['GET'])  # Send file and delete it
def getfile(filename):  # check dir name on prod server
    return send_file(FlaskConfig.EXPORT_FILE_DIR + filename,
                     mimetype='text/plain',
                     attachment_filename=filename,
                     as_attachment=True), os.remove(FlaskConfig.EXPORT_FILE_DIR + filename)


@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(FlaskConfig.UPLOAD_FOLDER, filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(FlaskConfig.UPLOAD_FOLDER,
                               filename)
