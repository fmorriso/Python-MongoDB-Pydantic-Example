import json
import sys
from importlib.metadata import version
#
import pymongo
#
from bson import ObjectId
#
from pydantic import create_model
from pydantic.fields import FieldInfo
#
from pymongo import MongoClient
from pymongo.synchronous.database import Database

from logging_utility import LoggingUtility as lu, LoggingUtility
#
from models.customer_model import Customer
from models.mongodb_base_model import MongoDbBaseModel
from program_settings import ProgramSettings

log = lu.start_logging()



def get_python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_package_version(package_name: str) -> str:
    return version(package_name)


def verify_mongodb_database():
    msg = 'top'
    log.info(msg)
    log.debug(msg)

    client: MongoClient = MongoDbBaseModel.get_mongodb_client()
    msg = f'{client=}'
    log.info(msg)
    log.debug(msg)

    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    msg = f'Program settings database name: {database_name}'
    log.info(msg)
    log.debug(msg)

    db: Database = MongoDbBaseModel.get_mongodb_database(client, database_name)
    msg = f'connected database name: {db.name}'
    log.info(msg)
    log.debug(msg)

    assert database_name == db.name, 'Program settings database name does not match connected database name'

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    msg = f'Program settings collection name: {collection_name}'
    log.info(msg)
    log.debug(msg)

    collection = MongoDbBaseModel.get_mongodb_collection(db, collection_name)
    msg = f'connected collection name: {collection.name}'
    log.info(msg)
    log.debug(msg)

    assert collection_name == collection.name, ('Program settings collection name does not match connected collection '
                                                'name')

    log.debug('leaving')


def verify_customer_model():
    """Verify that the Customer model works for retrieval from the customers collection within the sample_analytics
    collection."""
    log.debug('top')
    client: MongoClient = MongoDbBaseModel.get_mongodb_client()
    log.info(f'{client=}')
    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    log.info(f'{database_name=}')
    db = MongoDbBaseModel.get_mongodb_database(client, database_name)
    log.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    log.info(f'{collection_name=}')
    collection = db[collection_name]

    example_document = collection.find_one()
    msg = f'{example_document=}'
    log.info(msg)

    validated_customer = Customer(**example_document)
    msg = f'{validated_customer=}'
    log.info(msg)

    log.debug('leaving')


def verify_can_create_new_customer():
    msg = 'verify_can_create_new_customer - top'
    log.info(msg)
    log.debug(msg)

    client: MongoClient = MongoDbBaseModel.get_mongodb_client()
    msg = f'{client=}'
    log.info(msg)

    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    log.info(f'{database_name=}')

    db = MongoDbBaseModel.get_mongodb_database(client, database_name)
    log.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    log.info(f'{collection_name=}')
    collection = db[collection_name]

    example_document = collection.find_one()
    msg = f'{example_document=}'
    log.info(msg)

    original_customer = Customer(**example_document)

    copied_customer = original_customer.model_copy(deep = True)
    # change some fields to make a new record
    copied_customer.id = ObjectId()  # generate a new unique id
    copied_customer.username = 'daffyduck'
    copied_customer.email = 'daffy.duck@gmail.com'
    copied_customer.name = 'Daffy Duck'
    copied_customer.address = '9876 W. Maple Avenue\nDuck Pond, MN 55321'

    msg = f'{copied_customer=}'
    lu.log_info_and_debug(msg)

    # now ask MongoDB to insert the record into the collection
    insert_result = collection.insert_one(copied_customer.model_dump(warnings = 'error'))
    log.info(f'{insert_result=}')


def verify_can_query_by_unique_id():
    """
    Verify a single record can be fetched by unique id
    """
    unique_id = ProgramSettings.get_setting('CUSTOMER_UNIQUE_ID')
    msg = f'top using {unique_id=}'
    lu.log_info_and_debug(msg)

    client: MongoClient = MongoDbBaseModel.get_mongodb_client()
    log.info(f'{client=}')

    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    log.info(f'{database_name=}')
    db = MongoDbBaseModel.get_mongodb_database(client, database_name)
    log.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    log.info(f'{collection_name=}')
    collection = db[collection_name]

    msg = f'{unique_id=}'
    lu.log_info_and_debug(msg)

    example_document = Customer.find_by_unique_id(collection, unique_id)
    msg = f'{type(example_document)=}'
    log.debug(msg)

    msg = f'{example_document=}'
    log.info(msg)

    cust = Customer(**example_document)
    msg = f'{cust=}'
    lu.log_info_and_debug(msg)

    log.info('verify_can_query_by_unique_id - BOTTOM')


def extract_customer_schema():
    """Determine Customer Pydantic model by interrogating MongoDB Atlas for metadata about the customers collection."""
    msg = f'top'
    lu.log_info_and_debug(msg)

    client: MongoClient = MongoDbBaseModel.get_mongodb_client()
    log.info(f'{client=}')

    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    log.info(f'{database_name=}')
    db = MongoDbBaseModel.get_mongodb_database(client, database_name)
    log.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    log.info(f'{collection_name=}')
    collection = db[collection_name]

    sample_document = collection.find_one()
    msg = f'{sample_document=}'
    log.info(msg)

    # Generate Pydantic model dynamically
    model_name = 'Customer'
    customer_model = create_model(model_name, **{key: (type(value), ...) for key, value in sample_document.items() if
                                                 key != '_id'})
    msg = f'{type(customer_model)=}'
    log.info(msg)

    model_fields: dict[str, FieldInfo] = customer_model.model_fields
    for field_name, field_info in model_fields.items():
        field_type: str = str(field_info.annotation)
        # print(f'{type(field_type)=}')
        field_type = field_type.replace("<class '", "").replace('>', '').replace("'", '')
        msg = f'{field_name=} {field_info=} {field_type=}'
        log.info(msg)
    msg = json.dumps(customer_model.model_json_schema(), indent = 2)
    log.info(msg)
    log.debug(msg)


def get_mongodb_atlas_version() -> str:
    client = MongoDbBaseModel.get_mongodb_client()
    server_info = client.server_info()
    mongo_version: str = server_info['version']
    return mongo_version


def main():
    global log
    if log is None:
        log = LoggingUtility.start_logging()

    msg = f'Python version: {get_python_version()}'
    lu.log_info_and_debug(msg)

    msg = f"PyMongo version: {get_package_version('pymongo')}"
    lu.log_info_and_debug(msg)

    msg = f"Pydantic version: {get_package_version('pydantic')}"
    lu.log_info_and_debug(msg)

    msg = f"python-dotenv version: {get_package_version('python-dotenv')}"
    lu.log_info_and_debug(msg)

    msg = f"loguru version: {get_package_version('loguru')}"
    lu.log_info_and_debug(msg)

    msg = f"cryptography version: {get_package_version('cryptography')}"
    lu.log_info_and_debug(msg)

    mongo_version = get_mongodb_atlas_version()
    msg = f'MongoDB Atlas version: {mongo_version}'
    lu.log_info_and_debug(msg)

    verify_mongodb_database()
    verify_customer_model()
    # extract_customer_schema()

    # verify_can_create_new_customer()

    verify_can_query_by_unique_id()


if __name__ == '__main__':
    print(f"Python version: {get_python_version()}")
    print(f"PyMongo version: {get_package_version('pymongo')}")
    print(f"Pydantic version: {get_package_version('pydantic')}")
    print(f"python-dotenv version: {get_package_version('python-dotenv')}")
    print(f"loguru version: {get_package_version('loguru')}")
    print(f"cryptography version: {get_package_version('cryptography')}")

    main()
