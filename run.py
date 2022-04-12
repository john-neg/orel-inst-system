import os

from app import create_app
from config import FlaskConfig as Config

if not os.path.exists(Config.EXPORT_FILE_DIR):
    os.mkdir(Config.EXPORT_FILE_DIR, 0o755)

if not os.path.exists(Config.UPLOAD_FILE_DIR):
    os.mkdir(Config.UPLOAD_FILE_DIR, 0o755)

app = create_app()

app.run(debug=True)
