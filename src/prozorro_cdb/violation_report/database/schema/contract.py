from datetime import datetime

from pydantic import Field

from prozorro_cdb.api.database.schema.common import BaseModel
from prozorro_cdb.api.database.schema.organization import Buyer, Supplier


class Contract(BaseModel):
    id: str = Field(alias="_id")
    tender_id: str

    buyer: Buyer
    suppliers: list[Supplier]

    dateSigned: datetime | None = None
