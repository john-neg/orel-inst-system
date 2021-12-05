from flask import Blueprint

bp = Blueprint("programs", __name__)

from app.programs import programs
