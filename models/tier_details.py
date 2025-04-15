from typing import List

from pydantic import BaseModel


class TierDetails(BaseModel):
    tier: str
    benefits: List[str]
    active: bool
    id: str