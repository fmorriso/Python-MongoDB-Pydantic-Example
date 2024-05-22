import os, sys

from loguru import logger

from dotenv import load_dotenv
from pymongo import MongoClient

from pyodmongo import DbEngine, DbModel
from pyodmongo.queries import eq

from store_models import Product


def get_python_version() -> str:
    return f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'


def get_mongodb_atlas_uri() -> str:
    load_dotenv()

    template: str = os.environ.get('mongodb_connection_template')
    uid: str = os.environ.get('mongodb_uid')
    pwd: str = os.environ.get('mongodb_pwd')

    return f'mongodb+srv://{uid}:{pwd}@{template}'


def get_mongodb_client() -> MongoClient:
    # print(f'{get_connection_string()=}')
    return MongoClient(get_mongodb_atlas_uri())


def get_mongodb_database(client: MongoClient, database_name: str):
    return client.get_database(name=database_name)


def get_mongodb_collection(database, collection_name: str):
    return database.get_collection(collection_name)


def query_single_product():
    uri: str = get_mongodb_atlas_uri()
    database_name: str = os.environ.get('mongodb_database_name')
    engine = DbEngine(mongo_uri=uri, db_name=database_name)
    print(f'{engine=}')
    query = eq(Product.id_visible, 3)
    print(f'{query=}')
    doc: Product = engine.find_one(Model=Product, query=query)
    print(f'{doc=}')


def verify_mongodb_database():
    logger.info('top')
    client: MongoClient = get_mongodb_client()
    logger.info(f'{client=}')
    database_name: str = os.environ.get('mongodb_database_name')
    print(f'{database_name=}')
    db = get_mongodb_database(client, database_name)
    print(f'{db=}')

    collection_name: str = os.environ.get('mongodb_collection_name')

    products_collection = get_mongodb_collection(db, collection_name)
    print(f'{products_collection=}')
    logger.info('leaving')


def start_logging():
    log_format: str = '{time} - {name} - {level} - {function} - {message}'
    logger.remove()
    logger.add('formatted_log.txt', format=log_format, rotation='10 MB')


if __name__ == '__main__':
    start_logging()
    logger.info(f'Python version {get_python_version()}')
    verify_mongodb_database()
    query_single_product()
