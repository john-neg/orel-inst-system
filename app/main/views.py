import logging
import os

from flask import render_template, send_file, send_from_directory, flash
from werkzeug.exceptions import HTTPException

from config import FlaskConfig
from . import bp


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html", active="index", title="Главная")


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
    return send_from_directory(
        FlaskConfig.EXPORT_FILE_DIR,
        filename,
        as_attachment=True,
        download_name=filename.replace(',', ''),
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
    """Обработка и вывод всех ошибок (кроме HTTP) в виде flash-сообщений."""
    if isinstance(error, HTTPException):
        return error
    message = f"Произошла ошибка - {type(error).__name__} - {error}"
    flash(message, category='danger')
    logging.error(message)
    return render_template("errors/500_generic.html"), 500
