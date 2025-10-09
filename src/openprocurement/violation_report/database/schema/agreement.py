from pydantic import Field

from openprocurement.api.models_async.common import BaseModel
from openprocurement.api.models_async.organization import ProcuringEntity


class Agreement(BaseModel):
    id: str = Field(alias="_id")
    procuringEntity: ProcuringEntity
