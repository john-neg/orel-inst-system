from app.func import *
from app.forms import *
from werkzeug.utils import redirect
from flask import render_template, request, send_file, url_for


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    form = CalendarForm()
    form.department.choices = list(ApeksStaff.departments.items())

    if request.method == 'POST':
        if request.form.get('prepod'):
            department = request.form.get('department')
            month = request.form.get('month')
            year = request.form.get('year')
            prepod = request.form.get('prepod')
            filename = lessons_exp_cal(department, prepod, month, year)
            if filename == 'no data':
                form.prepod.choices = list(get_staff(department).items())
                error = f'{staff_name(prepod, department)} - нет занятий в указанный период'
                return render_template('calendar.html', form=form, department=department, prepod=None, error=error)
            else:
                return redirect(url_for('getfile', filename=filename))
        elif request.form.get('department'):
            department = request.form.get('department')
            form.prepod.choices = list(get_staff(department).items())
            return render_template('calendar.html', form=form, department=department)

    return render_template('calendar.html', form=form)  # department=department, month=month, year=year, prepod=prepod


@app.route('/<string:filename>', methods=['GET'])  # this is a job for GET, not POST
def getfile(filename):  # check dir name on prod server
    return send_file(app.config['EXPORT_FILE_DIR'] + filename,
                     mimetype='text/plain',
                     attachment_filename=filename,
                     as_attachment=True)


@app.route('/competencies')
def competencies():
    return render_template('competencies.html')
