from typing import Literal
from uuid import uuid4

from pydantic import Field, field_validator

from openprocurement.api.procedure.models.base import Model, validate_uniq_code
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.tender.cfaua.procedure.models.value import CFAUnitPriceValue
from openprocurement.tender.core.procedure.models.organization import BusinessOrganization
from openprocurement.tender.core.procedure.models.parameter import Parameter


class CFAUnitPrice(Model):
    relatedItem: str
    value: CFAUnitPriceValue | None = None


class CFAPatchAgreementContract(Model):
    parameters: list[Parameter] | None = None
    status: Literal["active", "unsuccessful"] | None = None
    unitPrices: list[CFAUnitPrice] | None = None

    @field_validator("parameters")
    @classmethod
    def validate_parameters_items(cls, value):
        validate_uniq_code(value)
        return value


class CFAAgreementContract(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    parameters: list[Parameter] | None = None
    status: Literal["active", "unsuccessful"] = "active"
    suppliers: list[BusinessOrganization] | None = None
    unitPrices: list[CFAUnitPrice] | None = None
    awardID: str | None = None
    bidID: str | None = None
    date: IsoDateTime | None = None

    @field_validator("parameters")
    @classmethod
    def validate_parameters_items(cls, value):
        validate_uniq_code(value)
        return value
