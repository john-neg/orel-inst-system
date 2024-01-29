from app.core.db.mongo_db import get_mongo_db
from config import MongoDBSettings

db = get_mongo_db()

db.create_collection(MongoDBSettings.STAFF_STABLE_COLLECTION)
db.create_collection(MongoDBSettings.STAFF_VARIOUS_COLLECTION)
db.create_collection(MongoDBSettings.STAFF_LOGS_COLLECTION)
