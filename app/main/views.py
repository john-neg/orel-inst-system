import os

from flask import render_template, send_file, send_from_directory, flash
from werkzeug.exceptions import HTTPException

from config import FlaskConfig
from . import bp


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html", active="index")


@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(FlaskConfig.STATIC_FILE_DIR, 'img/favicons'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon',
    )


@bp.route("/<string:filename>", methods=["GET"])
def get_file(filename):
    """Отправляет файл из папки export."""
    file = os.path.join(FlaskConfig.EXPORT_FILE_DIR, filename)
    return send_file(
        file,
        mimetype="text/plain",
        download_name=filename,
        as_attachment=True,
    )


@bp.route("/templates/<string:filename>", methods=["GET"])
def get_temp_file(filename):
    """Отправляет файл шаблона из папки templates."""
    file = os.path.join(FlaskConfig.TEMPLATE_FILE_DIR, filename)
    return send_file(
        file,
        mimetype="text/plain",
        download_name=filename,
        as_attachment=True,
    )


@bp.app_errorhandler(Exception)
def handle_exception(error):
    # pass through HTTP errors
    if isinstance(error, HTTPException):
        return error

    # now you're handling non-HTTP exceptions only
    flash(error, category='danger')
    return render_template("errors/500_generic.html"), 500
