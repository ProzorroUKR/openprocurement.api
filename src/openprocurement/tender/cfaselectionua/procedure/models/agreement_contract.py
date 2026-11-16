from typing import Literal
from uuid import uuid4

from pydantic import Field, field_validator

from openprocurement.api.procedure.models.base import Model, validate_uniq_code
from openprocurement.api.procedure.models.parameter import AgreementContractParameter
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.tender.cfaselectionua.procedure.models.organization import CFASelectionBusinessOrganization
from openprocurement.tender.cfaselectionua.procedure.models.value import CFASelectionUnitPriceValue


class CFASelectionUnitPrice(Model):
    relatedItem: str | None = None
    value: CFASelectionUnitPriceValue | None = None


class CFASelectionAgreementContract(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    parameters: list[AgreementContractParameter] | None = None
    status: Literal["active", "unsuccessful"] = "active"
    suppliers: list[CFASelectionBusinessOrganization] | None = None
    unitPrices: list[CFASelectionUnitPrice] | None = None
    awardID: str | None = None
    bidID: str | None = None
    date: IsoDateTime | None = None
    value: Value | None = None

    @field_validator("parameters")
    @classmethod
    def validate_parameters_items(cls, value):
        validate_uniq_code(value)
        return value
