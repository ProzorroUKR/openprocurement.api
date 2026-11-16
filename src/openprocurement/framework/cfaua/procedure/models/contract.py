from typing import Literal
from uuid import uuid4

from pydantic import Field, field_validator

from openprocurement.api.procedure.models.base import Model, validate_uniq_code
from openprocurement.api.procedure.models.organization import BusinessOrganization
from openprocurement.api.procedure.models.parameter import AgreementContractParameter as Parameter
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.framework.cfaua.procedure.models.unitprice import UnitPrice


class Contract(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    status: Literal["active", "unsuccessful"] | None = None
    suppliers: list[BusinessOrganization] | None = None
    unitPrices: list[UnitPrice] | None = None
    awardID: str | None = None
    bidID: str | None = None
    date: IsoDateTime | None = None
    parameters: list[Parameter] = []

    @field_validator("parameters")
    @classmethod
    def validate_parameters_items(cls, value):
        validate_uniq_code(value)
        return value
