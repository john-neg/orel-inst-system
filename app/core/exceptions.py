class ApeksApiException(Exception):
    """Класс для исключений API Апекс-ВУЗ"""
    pass


class ApeksWrongParameterException(Exception):
    """Передан неверный параметр рабочей программы"""
    pass


class ApeksParameterNonExistException(Exception):
    """Параметр не существует в таблице базы данных"""
    pass
