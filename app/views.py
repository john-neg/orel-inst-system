from app.func import *
from app.forms import *
from flask import render_template, request


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    form = CalendarForm()
    form.department.choices = list(ApeksStaff.departments.items())

    if request.method == 'POST':
        department = request.form.get('department')
        form.prepod.choices = list(get_staff(department).items())
        return render_template('calendar.html', form=form, department=department)

    return render_template('calendar.html', form=form)  # department=department, month=month, year=year prepod=prepod


@app.route('/competencies')
def competencies():
    return render_template('competencies.html')
