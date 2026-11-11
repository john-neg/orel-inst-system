from typing import Any, Mapping

from pymongo import MongoClient
from pymongo.database import Database

from config import MongoDBSettings


def get_mongo_db(
    dbname: str = MongoDBSettings.MONGO_DB_NAME,
) -> Database[Mapping[str, Any]]:
    """Подключение к базе данных MongoDB."""
    client = MongoClient(MongoDBSettings.CONNECTION_STRING)
    # mongodb://str_user:MasterSTR-24@172.16.1.23:37017/?authMechanism=DEFAULT&authSource=admin
    #client = MongoClient("mongodb://str_user:MasterSTR-24@172.16.1.23:37017/?authMechanism=DEFAULT&authSource=organization_staff")
    return client[dbname]
