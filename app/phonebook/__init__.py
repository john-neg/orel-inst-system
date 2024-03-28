from flask import Blueprint

bp_phbook = Blueprint("phonebook", __name__)
bp_phbook_get_data = Blueprint("get_data", __name__)

from . import views
