from typing import Literal

from pydantic import Field

from prozorro_cdb.api.database.schema.common import BaseModel


class TenderAgreement(BaseModel):
    id: str


class Tender(BaseModel):
    id: str = Field(alias="_id")
    procurementMethodType: str
    agreement: TenderAgreement
    procurementMethodDetails: str | None = None
    mode: Literal["test"] | None = None
