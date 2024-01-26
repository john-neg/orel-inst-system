from flask import Blueprint

bp = Blueprint("plans", __name__)

from . import views
