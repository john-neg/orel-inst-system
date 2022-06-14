class ApeksApiException(Exception):
    """Класс для исключений API Апекс-ВУЗ"""
    pass


class ApeksWrongParameterException(Exception):
    """Исключение - передан неверный параметр рабочей программы"""
    pass


class ApeksParameterNonExistException(Exception):
    """Исключение - параметр не существует в таблице базы данных"""
    pass
