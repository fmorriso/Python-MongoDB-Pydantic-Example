import sys
from logging import Logger
from typing import ClassVar

from bson import ObjectId
from loguru import logger
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

#
from program_settings import ProgramSettings


class MongoDbBaseModel(BaseModel):
    """ common base model for all MongoDB models than use _id as their unique identifier.
    This saves having to copy/paste a lot of duplicate code into each model."""
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id")
    __logger: ClassVar[logger] = logger


    @classmethod
    @property
    def logger(cls) -> Logger:
        return cls.__logger


    @staticmethod
    def start_logging() -> logger:
        """

        :rtype: object
        """
        log_format: str = '{time} - {name} - {level} - {function} - {message}'
        MongoDbBaseModel.__logger.remove()
        MongoDbBaseModel.__logger.add('../formatted_log.txt', format = log_format, rotation = '10 MB',
                                      retention = '5 days')
        # Add a handler that logs only DEBUG messages to stdout
        MongoDbBaseModel.__logger.add(sys.stdout, level = "DEBUG",
                                      filter = lambda record: record["level"].name == "DEBUG")
        return MongoDbBaseModel.__logger


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
    def get_mongodb_client() -> MongoClient:
        """get a client connection to my personal MongoDB Atlas cluster using my personal userid and password"""
        connection_string: str = MongoDbBaseModel.get_connection_string()
        connection: MongoClient = MongoClient(connection_string)
        return connection


    @staticmethod
    def get_mongodb_database(client: MongoClient, database_name: str) -> Database:
        return client.get_database(name = database_name)


    @staticmethod
    def get_mongodb_collection(database, collection_name: str) -> Collection:
        return database.get_collection(collection_name)


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
