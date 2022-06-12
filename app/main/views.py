import os

from flask import render_template, send_file, request, send_from_directory
from werkzeug.utils import secure_filename

from app.common.func.app_core import allowed_file
from app.main import bp
from config import FlaskConfig


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html", active="index")


@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(FlaskConfig.STATIC_FILE_DIR, 'favicons'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@bp.route("/<string:filename>", methods=["GET"])
def get_file(filename):
    """Отправляет файл и удаляет его из EXPORT_FILE_DIR."""
    file = os.path.join(FlaskConfig.EXPORT_FILE_DIR, filename)
    return (
        send_file(
            file,
            mimetype="text/plain",
            attachment_filename=filename,
            as_attachment=True,
        ),
        os.remove(file)
    )


@bp.route("/templates/<string:filename>", methods=["GET"])
def get_temp_file(filename):
    """Отправляет файл шаблона."""
    file = FlaskConfig.TEMPLATE_FILE_DIR + filename
    return send_file(
        file,
        mimetype="text/plain",
        attachment_filename=filename,
        as_attachment=True,
    )


@bp.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["user_file"]
        if file and allowed_file(file.filename):
            filename = file.filename
            # filename = secure_filename(file.filename)
            # (проблема с русскими названиями)
            file.save(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename))
            return filename
    return render_template("common/upload.html")


@bp.route("/read_file/", methods=["GET"])
def read_uploaded_file():
    filename = secure_filename(request.args.get("filename"))
    try:
        if filename and allowed_file(filename):
            with open(os.path.join(FlaskConfig.UPLOAD_FILE_DIR, filename)) as f:
                return f.read()
    except IOError:
        pass
    return "Unable to read file"
