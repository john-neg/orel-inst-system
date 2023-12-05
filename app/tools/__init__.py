from flask import Blueprint

from .payment import payment_bp

bp = Blueprint("tools", __name__)
bp.register_blueprint(payment_bp)
