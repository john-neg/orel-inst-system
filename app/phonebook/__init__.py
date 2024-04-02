from flask import Blueprint

phonebook_bp = Blueprint("phonebook", __name__)

from . import views
