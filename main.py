import json
import sys

#
import pymongo
#
from bson import ObjectId
#
from loguru import logger
from pydantic import create_model
from pydantic.fields import FieldInfo
#
from pymongo import MongoClient
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

#
#
#
from customer_model import Customer
from mongodb_base_model import MongoDbBaseModel
from program_settings import ProgramSettings


def get_python_version() -> str:
    return f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}'


def get_mongodb_client() -> MongoClient:
    """get a client connection to my personal MongoDB Atlas cluster using my personal userid and password"""
    connection_string: str = MongoDbBaseModel.get_connection_string()
    connection: MongoClient = MongoClient(connection_string)
    return connection


def get_mongodb_database(client: MongoClient, database_name: str) -> Database:
    return client.get_database(name = database_name)


def get_mongodb_collection(database, collection_name: str) -> Collection:
    return database.get_collection(collection_name)


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

    # example_document = collection.find_one({'_id': ObjectId(unique_id)})
    example_document = Customer.find_by_unique_id(collection, unique_id)
    msg = f'{type(example_document)=}'
    logger.debug(msg)

    msg = f'{example_document=}'
    logger.info(msg)

    cust = Customer(**example_document)

    logger.info('verify_can_query_by_unique_id - BOTTOM')


def extract_customer_schema():
    """Determine Customer Pydantic model by interrogating MongoDB Atlas for metadata about the customers collection."""
    msg = f'top'
    logger.info(msg)
    logger.debug(msg)

    client: MongoClient = get_mongodb_client()
    logger.info(f'{client=}')

    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    logger.info(f'{database_name=}')
    db = get_mongodb_database(client, database_name)
    logger.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    logger.info(f'{collection_name=}')
    collection = db[collection_name]

    sample_document = collection.find_one()
    msg = f'{sample_document=}'
    logger.info(msg)

    # Generate Pydantic model dynamically
    model_name = 'Customer'
    customer_model = create_model(model_name, **{key: (type(value), ...) for key, value in sample_document.items() if
                                                 key != '_id'})
    msg = f'{type(customer_model)=}'
    logger.info(msg)

    model_fields: dict[str, FieldInfo] = customer_model.model_fields
    for field_name, field_info in model_fields.items():
        field_type: str = str(field_info.annotation)
        # print(f'{type(field_type)=}')
        field_type = field_type.replace("<class '", "").replace('>', '').replace("'", '')
        msg = f'{field_name=} {field_info=} {field_type=}'
        logger.info(msg)
    msg = json.dumps(customer_model.model_json_schema(), indent = 2)
    logger.info(msg)
    logger.debug(msg)


def main():
    MongoDbBaseModel.start_logging()

    msg = f'Python version: {get_python_version()}'
    logger.info(msg)
    logger.debug(msg)

    msg = f'PyMongo version: {pymongo.version}'
    logger.info(msg)
    logger.debug(msg)

    client = get_mongodb_client()
    server_info = client.server_info()
    mongo_version = server_info['version']
    msg = f'MongoDB Atlas version: {mongo_version}'
    logger.info(msg)
    logger.debug(msg)

    # verify_customer_model()
    # extract_customer_schema()

    # verify_can_create_new_customer()

    verify_can_query_by_unique_id('67ba172377e77ea34bc1c118')  # Elmer Fudd
    # verify_can_query_by_unique_id('67ba1a6ede6fd6a19f1bb175')  # Daffy Duck


if __name__ == '__main__':
    main()
