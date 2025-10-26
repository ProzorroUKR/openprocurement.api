from pydantic import Field

from prozorro_cdb.api.database.schema.common import BaseModel
from prozorro_cdb.api.database.schema.organization import ProcuringEntity


class Agreement(BaseModel):
    id: str = Field(alias="_id")
    procuringEntity: ProcuringEntity
