from bson import ObjectId
from pydantic import BaseModel, Field
from pymongo.synchronous.collection import Collection


class MongoDbBaseModel(BaseModel):
    """ common base model for all MongoDB models than use _id as their unique identifier.
    This saves having to copy/paste a lot of duplicate code into each model."""
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id")


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
