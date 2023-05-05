from flask import Blueprint

from .payment import payment_bp
from .rewriter import rewriter_bp

bp = Blueprint("tools", __name__)
bp.register_blueprint(payment_bp)
bp.register_blueprint(rewriter_bp)
