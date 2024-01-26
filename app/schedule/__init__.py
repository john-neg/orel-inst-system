from flask import Blueprint

bp = Blueprint("schedule", __name__)

from . import views
