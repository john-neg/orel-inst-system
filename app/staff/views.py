import logging
from datetime import date

from flask import render_template, request, url_for
from flask_login import login_required
from werkzeug.utils import redirect

from config import ApeksConfig as Apeks
from . import bp
from ..common.classes.EducationStaff import EducationStaff
from ..common.classes.LoadReportProcessor import LoadReportProcessor
from ..common.func.api_get import check_api_db_response, api_get_db_table, get_lessons
from ..common.func.organization import get_departments
from ..common.func.staff import get_state_staff
from ..common.reports.holidays_report import generate_holidays_report
from ..common.reports.load_report import generate_load_report
from ..db.database import db
from ..db.reports_models import (
    ProductionCalendarHolidays,
    ProductionCalendarWorkingDays,
)
from ..services.base_db_service import BaseDBService



