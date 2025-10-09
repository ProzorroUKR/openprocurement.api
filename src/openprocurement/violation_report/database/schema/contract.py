from datetime import datetime
from typing import Optional

from pydantic import Field

from openprocurement.api.models_async.common import BaseModel
from openprocurement.api.models_async.organization import Buyer, Supplier


class Contract(BaseModel):
    id: str = Field(alias="_id")
    tender_id: str

    buyer: Buyer
    suppliers: list[Supplier]

    dateSigned: Optional[datetime] = None
