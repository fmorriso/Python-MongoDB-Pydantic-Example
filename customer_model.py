from datetime import datetime
from typing import List, Optional, ClassVar, Dict

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

from tier_details import TierDetails


class Customer(BaseModel):

    id: ObjectId = Field(default_factory = ObjectId, alias = "_id")

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
