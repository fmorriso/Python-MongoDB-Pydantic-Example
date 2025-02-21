from pydantic import BaseModel, Field, EmailStr, PositiveInt, PositiveFloat
from typing import List, Optional, ClassVar, Dict
from datetime import datetime
from bson import ObjectId

from mongodb_object_id import PyObjectId
from tier_details import TierDetails


class Customer(BaseModel):
    _id: ObjectId#= Field(default_factory=PyObjectId, alias='_id')
    #Optional[PyObjectId]  = Field(alias = "_id")

    username: str
    name: str
    address: str
    birthdate: datetime
    email: Optional[EmailStr] = None
    accounts: List[int]
    tier_and_details: Dict[str, TierDetails]

    # database: sample_analytics
    _collection: ClassVar = 'customers'


    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
