from flask import Blueprint

bp = Blueprint("library", __name__)

from app.library import views
