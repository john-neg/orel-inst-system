from app import app
from app.func import *
from app.forms import *
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    form = CalendarForm()
    return render_template('calendar.html', form=form)


@app.route('/competencies')
def competencies():
    return render_template('competencies.html')
