import sys
from typing import ClassVar
from bson import ObjectId
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.synchronous.collection import Collection
from loguru import logger
from pymongo.synchronous.database import Database

#
from program_settings import ProgramSettings


class MongoDbBaseModel(BaseModel):
    """ common base model for all MongoDB models than use _id as their unique identifier.
    This saves having to copy/paste a lot of duplicate code into each model."""
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id")
    logger: ClassVar[logger]

    @staticmethod
    def start_logging():
        log_format: str = '{time} - {name} - {level} - {function} - {message}'
        logger.remove()
        logger.add('formatted_log.txt', format = log_format, rotation = '10 MB', retention = '5 days')
        # Add a handler that logs only DEBUG messages to stdout
        logger.add(sys.stdout, level = "DEBUG", filter = lambda record: record["level"].name == "DEBUG")


    @staticmethod
    def get_connection_string() -> str:
        """
        Get a connection string for MongoDB using the key/values stored in the .env file.
        :return: a string containing the connection string.
        """
        template: str = ProgramSettings.get_setting('MONGODB_CONNECTION_TEMPLATE')
        uid: str = ProgramSettings.get_setting('MONGODB_UID')
        pwd: str = ProgramSettings.get_setting('MONGODB_PWD')

        conn_string = f'mongodb+srv://{uid}:{pwd}@{template}'
        logger.info(f'{conn_string=}')
        return conn_string

    @staticmethod
    def get_mongodb_database(client: MongoClient, database_name: str) -> Database:
        return client.get_database(name = database_name)


    @staticmethod
    def find_by_unique_id(collection: Collection, unique_id: str) -> dict:
        """Find a record in a collection by its unique MongoDB Atlas _id value.

        Args:
            collection: PyMongo collection instance.
            unique_id: unique MongoDB Atlas _id as a string.

        Returns:
            Dictionary with a single MongoDB Atlas record that matches the unique_id.
            or None if no such record exists.
        """
        return collection.find_one({'_id': ObjectId(unique_id)})

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
