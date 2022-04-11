import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class FlaskConfig(object):
    """Flask configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'verysupersecretkeystring'
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL'
    ) or 'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXPORT_FILE_DIR = os.path.join(BASEDIR, 'app/files/export/')
    UPLOAD_FILE_DIR = os.path.join(BASEDIR, 'app/files/upload/')
    TEMP_FILE_DIR = os.path.join(BASEDIR, 'app/files/templates/')
    ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

    TIMEZONE: int = 3

    # ApeksVUZ API data
    APEKS_URL = 'https://avtorvuz.orurinst.site'
    APEKS_TOKEN = 'b41dfa22-0a72-477f-9f05-995b8409863a'
    APEKS_DEPT_ID = '4'  # ID of Department divisions type

    # User roles
    ROLE_ADMIN: int = 1
    ROLE_USER: int = 2
    ROLE_METOD: int = 3
    ROLE_BIBL: int = 4

    # IDs of ApeksVUZ's fields in mm_work_programs_data_items table
    MM_WORK_PROGRAMS_DATA_ITEMS = {
        # Автор(ы) рабочей программы (для печати)
        "authorprint": 29,
        # Пояснение к таблице с последующими дисциплинами (информация об отсутствии)
        "no_next_disc": 30,
        # Примечание к тематическому плану
        "templan_info": 31,
        # Обеспечение самостоятельной работы
        "self_provision": 8,
        # Критерии оценки для сдачи промежуточной аттестации в форме тестирования
        "test_criteria": 32,
        # Тематика курсовых работ
        "course_works": 12,
        # Практикум
        "practice": 10,
        # Тематика контрольных работ
        "control_works": 13,
        # Примерные оценочные средства для проведения промежуточной аттестации
        "exam_form_desc": 33,
        # Задачи
        "task_works": 9,
        # Тесты
        "tests": 19,
        # Нормативные акты
        "regulations": 16,
        # Основная литература
        "library_main": 1,
        # Дополнительная литература
        "library_add": 2,
        # Научная продукция
        "library_np": 3,
        # Ресурсы информационно-телекоммуникационной сети Интернет
        "internet": 18,
        # Программное обеспечение
        "software": 15,
        # Базы данных, информационно-справочные и поисковые системы
        "ref_system": 17,
        # Описание материально-технической базы
        "materials_base": 20,
    }

    # Идентификаторы видов занятий
    CLASS_TYPE_ID = {
        # Лекция
        'lecture': 1,
        # Семинар
        'seminar': 2,
        # Практическое занятие
        'prakt': 3,
    }

    # Идентификаторы форм контроля
    CONTROL_TYPE_ID = {
        # Экзамен
        'exam': 1,
        # Зачет
        'zachet': 2,
        # Зачет с оценкой
        'zachet_mark': 6,
        # Итоговая письменная аудиторная к/р
        'itog_kontr': 10,
        # Входной контроль
        'in_control': 12,
        # Выходной контроль
        'out_control': 13,
        # Итоговая аттестация
        'final_att': 14,
        # Консультация
        'group_cons': 15,
        # Кандидатский экзамен
        'kandidat_exam': 16,
    }

    # Идентификаторы форм обучения
    EDUCATION_FORM_ID = {
        # Очное обучение
        'ochno': 1,
        # Заочное обучение
        'zaochno': 3,
        # Дополнительное проф образование
        'dpo': 5,
        # Проф. подготовка
        "prof_pod": 7,
    }

    # Идентификаторы уровней обучения
    EDUCATION_LEVEL_ID = {
        # Среднее профессиональное образование
        'spo': 2,
        # Бакалавриат
        'bak': 3,
        # Специалитет
        'spec': 5,
        # Адъюнктура
        'adj': 7,
    }
