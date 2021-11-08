from app.func import *
from app.forms import *
from flask import render_template, request, send_file, send_from_directory

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
            form.prepod.choices = list(get_staff(department).items())
            send_from_directory(directory=app.export_folder, filename=lessons_exp_cal(department, prepod, month, year))
            return render_template('calendar.html', form=form, department=department, month=month, year=year, prepod=prepod)
        elif request.form.get('department'):
            department = request.form.get('department')
            form.prepod.choices = list(get_staff(department).items())
            return render_template('calendar.html', form=form, department=department)

    return render_template('calendar.html', form=form)  # department=department, month=month, year=year, prepod=prepod

# def exp_cal():
#     month = request.form.get('month')
#     year = request.form.get('year')
#     prepod = request.form.get('prepod')
#     lessons_exp_cal(prepod, month, year)
#     return render_template('calendar.html')

@app.route('/competencies')
def competencies():
    return render_template('competencies.html')
