import json
import sys
from importlib.metadata import version

#
#
from bson import ObjectId
#
from pydantic import create_model
from pydantic.fields import FieldInfo
#
from pymongo import MongoClient
from pymongo.synchronous.database import Database

from logging_utility import LoggingUtility as LU
#
from models.customer_model import Customer
from models.mongodb_base_model import MongoDbBaseModel
from program_settings import ProgramSettings


def get_python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def get_package_version(package_name: str) -> str:
    return version(package_name)


def verify_mongodb_database():
    LU.start_logging()

    msg = 'top'
    LU.log_info_and_debug(msg)

    client: MongoClient = MongoDbBaseModel.get_mongodb_client()
    msg = f'{client=}'
    LU.log_info_and_debug(msg)

    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    msg = f'Program settings database name: {database_name}'
    LU.log_info_and_debug(msg)

    db: Database = MongoDbBaseModel.get_mongodb_database(client, database_name)
    msg = f'connected database name: {db.name}'
    LU.log_info_and_debug(msg)

    assert database_name == db.name, 'Program settings database name does not match connected database name'

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    msg = f'Program settings collection name: {collection_name}'
    LU.log_info_and_debug(msg)

    collection = MongoDbBaseModel.get_mongodb_collection(db, collection_name)
    msg = f'connected collection name: {collection.name}'
    LU.log_info_and_debug(msg)

    assert collection_name == collection.name, ('Program settings collection name does not match connected collection '
                                                'name')

    LU.debug('leaving')


def verify_customer_model():
    """Verify that the Customer model works for retrieval from the customers collection within the sample_analytics
    collection."""
    LU.debug('top')
    client: MongoClient = MongoDbBaseModel.get_mongodb_client()
    LU.debug(f'{client=}')
    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    LU.info(f'{database_name=}')
    db = MongoDbBaseModel.get_mongodb_database(client, database_name)
    LU.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    LU.info(f'{collection_name=}')
    collection = db[collection_name]

    example_document = collection.find_one()
    msg = f'{example_document=}'
    LU.info(msg)

    validated_customer = Customer(**example_document)
    msg = f'{validated_customer=}'
    LU.info(msg)

    LU.debug('leaving')


def verify_can_create_new_customer():
    msg = 'verify_can_create_new_customer - top'
    LU.info(msg)
    LU.debug(msg)

    client: MongoClient = MongoDbBaseModel.get_mongodb_client()
    msg = f'{client=}'
    LU.info(msg)

    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    LU.info(f'{database_name=}')

    db = MongoDbBaseModel.get_mongodb_database(client, database_name)
    LU.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    LU.info(f'{collection_name=}')
    collection = db[collection_name]

    example_document = collection.find_one()
    msg = f'{example_document=}'
    LU.info(msg)

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
    LU.info(f'{insert_result=}')


def verify_can_query_by_unique_id():
    """
    Verify a single record can be fetched by unique id
    """
    unique_id = ProgramSettings.get_setting('CUSTOMER_UNIQUE_ID')
    msg = f'top using {unique_id=}'
    LU.log_info_and_debug(msg)

    client: MongoClient = MongoDbBaseModel.get_mongodb_client()
    LU.info(f'{client=}')

    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    LU.info(f'{database_name=}')
    db = MongoDbBaseModel.get_mongodb_database(client, database_name)
    LU.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    LU.info(f'{collection_name=}')
    collection = db[collection_name]

    msg = f'{unique_id=}'
    LU.log_info_and_debug(msg)

    example_document = Customer.find_by_unique_id(collection, unique_id)
    msg = f'{type(example_document)=}'
    LU.debug(msg)

    msg = f'{example_document=}'
    LU.info(msg)

    cust = Customer(**example_document)
    msg = f'{cust=}'
    LU.log_info_and_debug(msg)

    LU.info('verify_can_query_by_unique_id - BOTTOM')


def extract_customer_schema():
    """Determine Customer Pydantic model by interrogating MongoDB Atlas for metadata about the customers collection."""
    msg = f'top'
    LU.log_info_and_debug(msg)

    client: MongoClient = MongoDbBaseModel.get_mongodb_client()
    LU.info(f'{client=}')

    database_name: str = ProgramSettings.get_setting('MONGODB_DATABASE_NAME')
    LU.info(f'{database_name=}')
    db = MongoDbBaseModel.get_mongodb_database(client, database_name)
    LU.info(f'{db=}')

    collection_name: str = ProgramSettings.get_setting('MONGODB_COLLECTION_NAME')
    LU.info(f'{collection_name=}')
    collection = db[collection_name]

    sample_document = collection.find_one()
    msg = f'{sample_document=}'
    LU.info(msg)

    # Generate Pydantic model dynamically
    model_name = 'Customer'
    customer_model = create_model(model_name, **{key: (type(value), ...) for key, value in sample_document.items() if
                                                 key != '_id'})
    msg = f'{type(customer_model)=}'
    LU.info(msg)

    model_fields: dict[str, FieldInfo] = customer_model.model_fields
    for field_name, field_info in model_fields.items():
        field_type: str = str(field_info.annotation)
        # print(f'{type(field_type)=}')
        field_type = field_type.replace("<class '", "").replace('>', '').replace("'", '')
        msg = f'{field_name=} {field_info=} {field_type=}'
        LU.info(msg)
    msg = json.dumps(customer_model.model_json_schema(), indent = 2)
    LU.info(msg)
    LU.debug(msg)


def get_mongodb_atlas_version() -> str:
    client = MongoDbBaseModel.get_mongodb_client()
    server_info = client.server_info()
    mongo_version: str = server_info['version']
    return mongo_version


def main():
    mongo_version = get_mongodb_atlas_version()
    msg = f'MongoDB Atlas version: {mongo_version}'
    LU.log_info_and_debug(msg)

    verify_mongodb_database()
    verify_customer_model()
    # extract_customer_schema()

    # verify_can_create_new_customer()

    verify_can_query_by_unique_id()


def get_required_package_names() -> list[str]:
    """
    read the requirements.txt file and return a sorted list of package names.
    :return: sorted list of package names
    :rtype: list[str
    """
    packages: list[str] = []
    with open('requirements.txt') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # skip blank lines and comments
            package = line.split('~')[0].strip()  # works for ~=, >=, ==, etc.
            packages.append(package)

    packages.sort()
    return packages


if __name__ == '__main__':
    LU.log_info_and_debug(f"Python version: {get_python_version()}")

    package_names = get_required_package_names()

    for pkg in package_names:
        package_name = f'{pkg}'.ljust(16)
        try:
            LU.log_info_and_debug(f'{package_name}{get_package_version(pkg)}')
        except Exception as e:
            print(e)

    main()
