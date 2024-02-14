import abc


class AbstractApiRepository(metaclass=abc.ABCMeta):
    """Абстрактный класс для запросов к API."""

    @abc.abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def post(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def put(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def patch(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, *args, **kwargs):
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
