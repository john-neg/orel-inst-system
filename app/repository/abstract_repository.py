import abc


class AbstractApiRepository(metaclass=abc.ABCMeta):
    """Абстрактный класс для запросов к API."""

    @abc.abstractmethod
    def get(self, endpoint: str, params: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def post(self, endpoint: str, params: dict, data: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, endpoint: str, params: dict, data: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def patch(self, endpoint: str, params: dict, data: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, endpoint: str, params: dict):
        raise NotImplementedError


class AbstractDBRepository(metaclass=abc.ABCMeta):
    """Абстрактный класс запросов к базе данных."""

    @abc.abstractmethod
    def list(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, *args, **kwargs):
        raise NotImplementedError
