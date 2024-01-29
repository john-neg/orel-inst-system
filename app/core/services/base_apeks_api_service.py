import logging
from dataclasses import dataclass
from typing import Any

from ..exceptions import ApeksApiException
from ..repository.abstract_repository import AbstractDBRepository
from ..repository.apeks_api_repository import ApeksApiRepository, ApeksApiEndpoints


@dataclass
class ApeksApiDbService(AbstractDBRepository):
    """
    Класс для доступа к базе данных АпексВУЗ через API.

    Attributes
    ----------
    table : str
        название таблицы базы данных АпексВУЗ
    repository : ApeksApiRepository
        репозитория для запросов к API АпексВУЗ
    token : str
        токен доступа к API АпексВУЗ
    """

    table: str
    repository: ApeksApiRepository
    token: str

    async def list(self):
        """Возвращает все объекты из таблицы базы данных АпексВУЗ."""
        return await self.get()

    async def get(self, **filters) -> list:
        """Возвращает список объектов из таблицы базы данных АпексВУЗ."""
        endpoint = ApeksApiEndpoints.DB_GET_ENDPOINT.value
        params = {"token": self.token, "table": self.table}
        if filters:
            for db_filter, db_value in filters.items():
                if isinstance(db_value, (int, str)):
                    values = str(db_value)
                else:
                    values = [str(val) for val in db_value]
                params[f"filter[{db_filter}][]"] = values
        logging.debug(f"Созданы параметры для GET запроса к таблице: {self.table}")
        return await self.repository.get(endpoint, params)

    async def create(self, **fields) -> dict | Any:
        """Создает объект в таблице базы данных АпексВУЗ."""
        endpoint = ApeksApiEndpoints.DB_ADD_ENDPOINT.value
        params = {"token": self.token}
        data = {"table": self.table}
        for db_field, db_value in fields.items():
            data[f"fields[{db_field}]"] = str(db_value)
        logging.debug(
            f"Созданы параметры для POST (CREATE) запроса к таблице {self.table}"
        )
        return await self.repository.post(endpoint, params, data)

    async def update(self, filters: dict, fields: dict) -> dict | Any:
        """Изменяет объекты в таблице базы данных АпексВУЗ."""
        endpoint = ApeksApiEndpoints.DB_EDIT_ENDPOINT.value
        params = {"token": self.token}
        data = {"table": self.table}
        for db_field, db_value in filters.items():
            if type(db_value) in (int, str):
                values = str(db_value)
            else:
                values = [str(val) for val in db_value]
            data[f"filter[{db_field}][]"] = values
            if not values:
                message = (
                    "Для фильтра операции POST (UPDATE) "
                    "передан параметр с пустым значением"
                )
                logging.error(message)
                raise ApeksApiException(message)
        for db_field, db_value in fields.items():
            data[f"fields[{db_field}]"] = str(db_value)
        logging.debug(
            f"Переданы параметры для POST (CREATE) запроса к таблице '{self.table}'"
        )
        return await self.repository.post(endpoint, params, data)

    async def delete(self, **filters) -> dict | Any:
        """Удаляет объекты в таблице базы данных АпексВУЗ."""
        endpoint = ApeksApiEndpoints.DB_DEL_ENDPOINT.value
        params = {"token": self.token, "table": self.table}
        for db_field, db_value in filters.items():
            params[f"filter[{db_field}][]"] = db_value
            if not db_value:
                message = "Для операции DELETE передан параметр с пустым значением"
                logging.error(message)
                raise ApeksApiException(message)
        return await self.repository.delete(endpoint, params)


# При рефакторинге со старой функции убрать преобразование в int
def data_processor(
    table_data: list[dict[str, Any]], key: str = "id"
) -> dict[str, dict[str, Any]]:
    """
    Преобразует полученные данные из таблиц БД Апекс-ВУЗ.

    Parameters
    ----------
        table_data
            данные таблицы, содержащей список словарей в формате JSON
        key: str
            название поля, значения которого станут ключами словаря
            (по умолчанию - 'id')

    Returns
    -------
        dict
            {id: {keys: values}}.
    """
    data = {item.get(key): item for item in table_data if item.get(key)}
    logging.debug(f"Обработаны данные. Ключ: {key}")
    return data
