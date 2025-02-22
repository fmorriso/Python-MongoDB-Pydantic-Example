import os
import sys
from datetime import datetime

#
import pymongo
import pyodmongo.version
from bson import ObjectId
#
from loguru import logger
from pymongo import MongoClient
from pyodmongo import DbEngine
from pyodmongo.queries import eq

from customer_model import Customer
#
from program_settings import ProgramSettings
from store_models import Product


def get_python_version() -> str:
    return f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'


def get_mongodb_atlas_uri() -> str:
    template: str | None  = ProgramSettings.get_setting('MONGODB_CONNECTION_TEMPLATE')
    uid: str | None  = ProgramSettings.get_setting('MONGODB_UID')
    pwd: str | None = ProgramSettings.get_setting('mongodb_pwd')
    uri: str = f'mongodb+srv://{uid}:{pwd}@{template}'
    msg: str = f'{uri=}'
    logger.info(msg)
    return uri


def get_mongodb_client() -> MongoClient:
    uri: str = get_mongodb_atlas_uri()
    msg = f'{uri=}'
    logger.info(msg)
    return MongoClient(uri)


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


def verify_customer_model():
    """Verify that the Customer model works for retrieval from the customers collection within the sample_analytics
    collection."""
    logger.info('top')
    client: MongoClient = get_mongodb_client()
    logger.info(f'{client=}')
    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    logger.info(f'{database_name=}')
    db = get_mongodb_database(client, database_name)
    logger.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    logger.info(f'{collection_name=}')
    collection = db[collection_name]

    example_document = collection.find_one()
    msg = f'{example_document=}'
    logger.info(msg)

    validated_customer = Customer(**example_document)
    msg = f'{validated_customer=}'
    logger.info(msg)


def verify_can_create_new_customer():
    client: MongoClient = get_mongodb_client()
    logger.info(f'{client=}')
    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    logger.info(f'{database_name=}')
    db = get_mongodb_database(client, database_name)
    logger.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    logger.info(f'{collection_name=}')
    collection = db[collection_name]

    example_document = collection.find_one()
    msg = f'{example_document=}'
    logger.info(msg)

    original_customer = Customer(**example_document)

    copied_customer = original_customer.model_copy(deep = True, update = {"_id": ObjectId()})
    # change some fields to make a new record
    copied_customer.username = 'frederickmorrison'
    copied_customer.email = 'frederick.morrison@outlook.com'
    copied_customer.name = 'Frederick Morrison'
    copied_customer.address = '2132 Seaglass Street\nColorado Springs, CO 80921-4030'
    msg = f'{copied_customer=}'
    logger.info(msg)

    # save to MongoDB collection
    # convert to dictionary
    new_record = copied_customer.model_dump(by_alias=True)
    new_record.pop("_id", None) # prevent DuplicateKeyError
    msg = f'{new_record=}'
    logger.info(msg)

    # now ask MongoDB to insert into the collection as a new record
    insert_result = collection.insert_one(new_record)
    logger.info(f'{insert_result=}')


def verify_can_query_by_unique_id():
    """
    Verify a single record can be fetched by unique id
    """
    client: MongoClient = get_mongodb_client()
    logger.info(f'{client=}')
    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    logger.info(f'{database_name=}')
    db = get_mongodb_database(client, database_name)
    logger.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    logger.info(f'{collection_name=}')
    collection = db[collection_name]

    unique_id = '67b90df05a2ffff6369c798c'
    msg = f'{unique_id=}'
    logger.info(msg)

    example_document = collection.find_one({'_id': ObjectId(unique_id)})
    msg = f'{example_document=}'
    logger.info(msg)


def main():
    start_logging()

    msg = f'Python version: {get_python_version()}'
    print(msg)
    logger.info(msg)

    msg = f'PyMongo version: {pymongo.version}'
    print(msg)
    logger.info(msg)

    verify_customer_model()
    
    # verify_can_create_new_customer()

    verify_can_query_by_unique_id()


if __name__ == '__main__':
    main()
