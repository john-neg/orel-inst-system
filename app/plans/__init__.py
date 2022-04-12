from flask import Blueprint

bp = Blueprint("plans", __name__)

from app.plans import views
