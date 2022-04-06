import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class ApeksAPI(object):
    """Apeks Vuz API data"""
    URL = 'https://avtorvuz.orurinst.site'
    TOKEN = 'b41dfa22-0a72-477f-9f05-995b8409863a'
    APEKS_DEPT_ID = '4'  # ID of Department divisions type


class FlaskConfig(object):
    """Flask configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'verysupersecretkeystring'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXPORT_FILE_DIR = os.path.join(BASEDIR, 'app/files/export/')
    UPLOAD_FILE_DIR = os.path.join(BASEDIR, 'app/files/upload/')
    TEMP_FILE_DIR = os.path.join(BASEDIR, 'app/files/templates/')
    ALLOWED_EXTENSIONS = {'xlsx', 'csv'}


class DbRoles(object):
    """User roles"""
    ROLE_ADMIN = 1
    ROLE_USER = 2
    ROLE_METOD = 3
    ROLE_BIBL = 4


class LibConfig(object):
    """Setup of fields-id for Library list upload"""
    BIBL_MAIN = 1
    BIBL_ADD = 2
    BIBL_NP = 3
    BIBL_INT = 18
    BIBL_DB = 17
