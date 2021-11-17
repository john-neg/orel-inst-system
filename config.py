import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Apeks API configuration data
URL = 'https://avtorvuz.orurinst.site'
TOKEN = 'b41dfa22-0a72-477f-9f05-995b8409863a'
APEKS_DEPT_ID = '4'

# Flask config
SECRET_KEY = os.environ.get('SECRET_KEY') or 'verysupersecretkeystring'
EXPORT_FILE_DIR = 'files/'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False
UPLOAD_FOLDER = 'files/'
ALLOWED_EXTENSIONS = set(['xlxs', 'csv'])

# User roles in DB
ROLE_ADMIN = 1
ROLE_USER = 2
ROLE_METOD = 3
ROLE_BIBL = 4

# Setup of fields-id for Library list upload
BIBL_MAIN = 1
BIBL_ADD = 2
BIBL_NP = 3
