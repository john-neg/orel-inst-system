from flask import Blueprint

bp = Blueprint("tools", __name__)

from app.tools import views
