import os
import sys
#
import pymongo
import pyodmongo.version
#
from loguru import logger
from pymongo import MongoClient
from pyodmongo import DbEngine
from pyodmongo.queries import eq
#
from program_settings import ProgramSettings
from store_models import Product


def get_python_version() -> str:
    return f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'


def get_mongodb_atlas_uri() -> str:


    template: str | None  = ProgramSettings.get_setting('MONGODB_CONNECTION_TEMPLATE')
    uid: str | None  = ProgramSettings.get_setting('MONGODB_UID')
    pwd: str | None = ProgramSettings.get_setting('mongodb_pwd')

    return f'mongodb+srv://{uid}:{pwd}@{template}'


def get_mongodb_client() -> MongoClient:
    # print(f'{get_connection_string()=}')
    return MongoClient(get_mongodb_atlas_uri())


def get_mongodb_database(client: MongoClient, database_name: str):
    return client.get_database(name=database_name)


def get_mongodb_collection(database, collection_name: str):
    return database.get_collection(collection_name)


def query_single_product():
    logger.info('top')
    uri: str = get_mongodb_atlas_uri()
    database_name: str | None = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    engine = DbEngine(mongo_uri=uri, db_name=database_name)
    logger.info(f'{engine=}')
   
    query = eq(Product.id_visible, 3)
    logger.info(f'{query=}')
    doc: Product = engine.find_one(Model=Product, query=query)

    msg = f'{doc=}'
    print(msg)
    logger.info(msg)

    logger.info('leaving')


def verify_mongodb_database():
    logger.info('top')
    client: MongoClient = get_mongodb_client()
    logger.info(f'{client=}')
    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    logger.info(f'{database_name=}')
    db = get_mongodb_database(client, database_name)
    logger.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')

    products_collection = get_mongodb_collection(db, collection_name)
    logger.info(f'{products_collection=}')
    logger.info('leaving')


def start_logging():
    log_format: str = '{time} - {name} - {level} - {function} - {message}'
    logger.remove()
    logger.add('formatted_log.txt', format=log_format, rotation='10 MB', retention='5 days')

def main():
    start_logging()

    msg = f'Python version: {get_python_version()}'
    print(msg)
    logger.info(msg)

    msg = f'PyMongo version: {pymongo.version}'
    print(msg)
    logger.info(msg)

    msg = f'PyODmongo version {pyodmongo.version.VERSION}'
    print(msg)
    logger.info(msg)

    verify_mongodb_database()
    query_single_product()


if __name__ == '__main__':
    main()
