from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

class MongoDbBaseModel(BaseModel):
    """ common base model for all MongoDB models than use _id """
    id: ObjectId = Field(default_factory = ObjectId, alias = "_id")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

