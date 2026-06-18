import os
from functools import lru_cache
import certifi

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi


load_dotenv()


@lru_cache(maxsize=1)
def get_mongo_client() -> MongoClient:
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is not set")
    return MongoClient(uri, server_api=ServerApi("1"), tlsCAFile=certifi.where())


def get_database():
    db_name = os.getenv("MONGODB_DB_NAME", "ciphersplit")
    return get_mongo_client()[db_name]


def get_sessions_collection():
    return get_database()["image_sessions"]