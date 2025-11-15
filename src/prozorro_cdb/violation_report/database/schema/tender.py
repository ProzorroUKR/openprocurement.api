from typing import Literal, Optional

from pydantic import Field

from prozorro_cdb.api.database.schema.common import BaseModel


class TenderAgreement(BaseModel):
    id: str


class Tender(BaseModel):
    id: str = Field(alias="_id")
    procurementMethodType: str
    agreement: TenderAgreement
    procurementMethodDetails: Optional[str] = None
    mode: Optional[Literal["test"]] = None
