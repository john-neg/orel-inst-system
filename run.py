import os

from flask.logging import create_logger

from app import create_app
from config import FlaskConfig

if not os.path.exists(FlaskConfig.EXPORT_FILE_DIR):
    os.mkdir(FlaskConfig.EXPORT_FILE_DIR, 0o755)

if not os.path.exists(FlaskConfig.UPLOAD_FILE_DIR):
    os.mkdir(FlaskConfig.UPLOAD_FILE_DIR, 0o755)

if not os.path.exists(FlaskConfig.LOG_FILE_DIR):
    os.mkdir(FlaskConfig.LOG_FILE_DIR, 0o755)

app = create_app()

logger = create_logger(app)

app.run(debug=True)
