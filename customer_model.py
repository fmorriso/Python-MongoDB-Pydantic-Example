from datetime import datetime
from typing import List, Optional, ClassVar, Dict

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

from mongodb_base_model import MongoDbBaseModel
from tier_details import TierDetails


class Customer(MongoDbBaseModel):

    #NOTE: _id is defined in MongoDbBaseModel

    username: str
    name: str
    address: str
    birthdate: datetime
    email: Optional[EmailStr] = None
    accounts: List[int]
    tier_and_details: Dict[str, TierDetails]

    # database: sample_analytics
    _collection: ClassVar = 'customers'

