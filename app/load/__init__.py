from flask import Blueprint

bp = Blueprint("load", __name__)

from app.load import views
