import logging
from dataclasses import dataclass
from typing import Any

from ..exceptions import ApeksApiException
from ..repository.abstract_repository import AbstractDBRepository
from ..repository.apeks_api_repository import ApeksApiRepository, ApeksApiEndpoints


@dataclass
class ApeksApiDbService(AbstractDBRepository):
    """Класс для доступа к базе данных АпексВУЗ через API."""

    repository: ApeksApiRepository
    token: str

    async def list(self, table):
        """Возвращает все объекты из таблицы базы данных АпексВУЗ."""
        return await self.get(table)

    async def get(self, table, **filters) -> list:
        """Возвращает список объектов из таблицы базы данных АпексВУЗ."""
        endpoint = ApeksApiEndpoints.DB_GET_ENDPOINT
        params = {"token": self.token, "table": table}
        if filters:
            for db_filter, db_value in filters.items():
                if isinstance(db_value, (int, str)):
                    values = str(db_value)
                else:
                    values = [str(val) for val in db_value]
                params[f"filter[{db_filter}][]"] = values
        logging.debug(f"Созданы параметры для GET запроса к таблице: {table}")
        return await self.repository.get(endpoint, params)

    async def create(self, table, **fields) -> dict | Any:
        """Создает объект в таблице базы данных АпексВУЗ."""
        endpoint = ApeksApiEndpoints.DB_ADD_ENDPOINT
        params = {"token": self.token}
        data = {"table": table}
        for db_field, db_value in fields.items():
            data[f"fields[{db_field}]"] = str(db_value)
        logging.debug(f"Созданы параметры для POST (CREATE) запроса к таблице {table}")
        return await self.repository.post(endpoint, params, data)

    async def update(self, table: str, filters: dict, fields: dict) -> dict | Any:
        """Изменяет объекты в таблице базы данных АпексВУЗ."""
        endpoint = ApeksApiEndpoints.DB_EDIT_ENDPOINT
        params = {"token": self.token}
        data = {"table": table}
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
            f"Переданы параметры для POST (CREATE) запроса к таблице '{table}'"
        )
        return await self.repository.post(endpoint, params, data)

    async def delete(self, table, **filters) -> dict | Any:
        """Удаляет объекты в таблице базы данных АпексВУЗ."""
        endpoint = ApeksApiEndpoints.DB_DEL_ENDPOINT
        params = {"token": self.token, "table": table}
        for db_field, db_value in filters.items():
            params[f"filter[{db_field}][]"] = db_value
            if not db_value:
                message = "Для операции DELETE передан параметр с пустым значением"
                logging.error(message)
                raise ApeksApiException(message)
        return await self.repository.delete(endpoint, params)


def data_processor(table_data: list[dict], dict_key: str = "id") -> dict:
    """
    Преобразует полученные данные из таблиц БД Апекс-ВУЗ.

    Parameters
    ----------
        table_data
            данные таблицы, содержащей список словарей в формате JSON
        dict_key: str
            название поля, значения которого станут ключами словаря
            (по умолчанию - 'id')

    Returns
    -------
        dict
            {id: {keys: values}}.
    """
    data = {}
    for d_val in table_data:
        key_val = d_val.get(dict_key)
        if key_val:
            data[int(key_val)] = d_val
    logging.debug(f"Обработаны данные. Ключ: {dict_key}")
    return data
