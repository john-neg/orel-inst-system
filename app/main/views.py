import os

from flask import render_template, send_file

from app.main import bp
from config import FlaskConfig


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html", active="index")


@bp.route("/<string:filename>", methods=["GET"])
def get_file(filename):
    """Отправляет файл и удаляет его из EXPORT_FILE_DIR."""
    file = os.path.join(FlaskConfig.EXPORT_FILE_DIR, filename)
    return send_file(
        file,
        mimetype="text/plain",
        download_name=filename,
        as_attachment=True,
    )


@bp.route("/templates/<string:filename>", methods=["GET"])
def get_temp_file(filename):
    """Отправляет файл шаблона."""
    file = os.path.join(FlaskConfig.TEMPLATE_FILE_DIR, filename)
    return send_file(
        file,
        mimetype="text/plain",
        download_name=filename,
        as_attachment=True,
    )
