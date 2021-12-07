import os
from flask import render_template, send_file, request
from werkzeug.utils import secure_filename
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


@bp.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["user_file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(FlaskConfig.UPLOAD_FOLDER, filename))
            return filename
    return render_template('main/upload.html')


@bp.route('/read_file', methods=['GET'])
def read_uploaded_file():
    filename = secure_filename(request.args.get('filename'))
    try:
        if filename and allowed_file(filename):
            with open(os.path.join(FlaskConfig['UPLOAD_FOLDER'], filename)) as f:
                return f.read()
    except IOError:
        pass
    return "Unable to read file"
