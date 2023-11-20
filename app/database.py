from . import config

import pymongo
from pymongo.mongo_client import MongoClient

settings = config.get_settings()

client = MongoClient(settings.db_uri)

db = client[settings.db_name]

profiles = db.scholars_info

papers = db.papers

profiles.create_index([("name", pymongo.ASCENDING)], unique=True)

papers.create_index([("name", pymongo.ASCENDING)], unique=True)
