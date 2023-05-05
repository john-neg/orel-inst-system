from flask import Blueprint

payment_bp = Blueprint("payment", __name__)

from . import views