import os
from flask import render_template, send_file, request, url_for, send_from_directory
from werkzeug.utils import secure_filename, redirect
from app.main.func import allowed_file
from app.main import bp
from config import FlaskConfig


@bp.route("/")
@bp.route("/index")
def index():
    return render_template("index.html", active="index")


@bp.route("/<string:filename>", methods=["GET"])
def getfile(filename):
    """Send file and delete it from server"""
    return (
        send_file(
            FlaskConfig.EXPORT_FILE_DIR + filename,
            mimetype="text/plain",
            attachment_filename=filename,
            as_attachment=True,
        ),
        os.remove(FlaskConfig.EXPORT_FILE_DIR + filename),
    )


# @bp.route("/uploads", methods=["GET", "POST"])
# def upload_file():
#     if request.method == "POST":
#         file = request.files["file"]
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file.save(os.path.join(FlaskConfig.UPLOAD_FOLDER, filename))
#             return redirect(url_for("uploaded_file", filename=filename))
#
#
# @bp.route("/uploads/<filename>")
# def uploaded_file(filename):
#     return send_from_directory(FlaskConfig.UPLOAD_FOLDER, filename)
