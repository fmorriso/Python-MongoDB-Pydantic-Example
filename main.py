import sys

#
import pymongo
#
from bson import ObjectId
#
from loguru import logger
from pymongo import MongoClient
from pymongo.synchronous.database import Database

from customer_model import Customer
from program_settings import ProgramSettings


def get_python_version() -> str:
    return f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'


def get_connection_string() -> str:
    """
    Get a connection string for MongoDB using the key/values stored in the .env file.
    :return: a string containing the connection string.
    """
    template: str = ProgramSettings.get_setting('MONGODB_CONNECTION_TEMPLATE')
    uid: str = ProgramSettings.get_setting('MONGODB_UID')
    pwd: str = ProgramSettings.get_setting('MONGODB_PWD')

    conn_string = f'mongodb+srv://{uid}:{pwd}@{template}'
    logger.debug(f'{conn_string=}')
    return conn_string


def get_mongodb_client() -> MongoClient:
    """get a client connection to my personal MongoDB Atlas cluster using my personal userid and password"""
    connection_string: str = get_connection_string()
    connection: MongoClient = MongoClient(connection_string)
    return connection


def get_mongodb_database(client: MongoClient, database_name: str) -> Database:
    return client.get_database(name = database_name)


def get_mongodb_collection(database, collection_name: str):
    return database.get_collection(collection_name)


def query_single_product():
    print('Query single product - TOP')
    logger.debug('top')

    database_name = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    database = get_mongodb_database(database_name)

    collection_name = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    collection = get_mongodb_collection(database, collection_name)

    doc = collection.find_one()

    # query: dict = {'_id': ObjectId(doc['_id'])}
    # doc = collection.find_one(Model = Product, query = query)

    msg = f'{doc=}'
    print(msg)
    logger.info(msg)

    logger.debug('leaving')


def verify_mongodb_database():
    logger.debug('top')
    client: MongoClient = get_mongodb_client()
    logger.info(f'{client=}')
    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    logger.info(f'{database_name=}')
    db = get_mongodb_database(client, database_name)
    logger.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')

    products_collection = get_mongodb_collection(db, collection_name)
    logger.info(f'{products_collection=}')
    logger.debug('leaving')


def start_logging():
    log_format: str = '{time} - {name} - {level} - {function} - {message}'
    logger.remove()
    logger.add('formatted_log.txt', format = log_format, rotation = '10 MB', retention = '5 days')
    # Add a handler that logs only DEBUG messages to stdout
    logger.add(sys.stdout, level = "DEBUG", filter = lambda record: record["level"].name == "DEBUG")


def verify_customer_model():
    """Verify that the Customer model works for retrieval from the customers collection within the sample_analytics
    collection."""
    logger.debug('top')
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

    logger.debug('leaving')


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

    copied_customer = original_customer.model_copy(deep = True)
    # change some fields to make a new record
    copied_customer.id = ObjectId()  # generate a new unique id
    copied_customer.username = 'daffyduck'
    copied_customer.email = 'daffy.duck@gmail.com'
    copied_customer.name = 'Daffy Duck'
    copied_customer.address = '9876 W. Maple Avenue\nDuck Pond, MN 55321'

    msg = f'{copied_customer=}'
    logger.info(msg)

    # now ask MongoDB to insert the record into the collection
    insert_result = collection.insert_one(copied_customer.model_dump(warnings = 'error'))
    logger.info(f'{insert_result=}')


def verify_can_query_by_unique_id(unique_id: str):
    """
    Verify a single record can be fetched by unique id
    """
    msg = f'top using {unique_id=}'
    logger.info(msg)

    client: MongoClient = get_mongodb_client()
    logger.info(f'{client=}')

    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    logger.info(f'{database_name=}')
    db = get_mongodb_database(client, database_name)
    logger.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    logger.info(f'{collection_name=}')
    collection = db[collection_name]

    msg = f'{unique_id=}'
    logger.info(msg)

    example_document = collection.find_one({'_id': ObjectId(unique_id)})
    msg = f'{example_document=}'
    logger.info(msg)

    print('verify_can_query_by_unique_id - BOTTOM')


def main():
    start_logging()

    msg = f'Python version: {get_python_version()}'
    print(msg)
    logger.info(msg)

    msg = f'PyMongo version: {pymongo.version}'
    print(msg)
    logger.info(msg)

    # verify_customer_model()

    # verify_can_create_new_customer()

    verify_can_query_by_unique_id('67ba172377e77ea34bc1c118')  # Elmer Fudd
    verify_can_query_by_unique_id('67ba1a6ede6fd6a19f1bb175')  # Daffy Duck


if __name__ == '__main__':
    main()
