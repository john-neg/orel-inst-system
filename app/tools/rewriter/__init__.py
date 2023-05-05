from flask import Blueprint

rewriter_bp = Blueprint("rewriter", __name__)

from . import views