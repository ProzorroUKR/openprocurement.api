from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, computed_field, field_validator

from openprocurement.api.procedure.models.base import Model, validate_uniq_code, validate_uniq_id
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.tender.core.procedure.models.base import BaseBid
from openprocurement.tender.core.procedure.models.document import (
    Document,
    PostDocument,
)
from openprocurement.tender.core.procedure.models.item import LocalizationItem
from openprocurement.tender.core.procedure.models.lot_value import (
    LotValue,
    PatchLotValue,
    PostLotValue,
)
from openprocurement.tender.core.procedure.models.organization import Supplier
from openprocurement.tender.core.procedure.models.parameter import (
    Parameter,
    PatchParameter,
)
from openprocurement.tender.core.procedure.models.req_response import (
    ObjResponseMixin,
)
from openprocurement.tender.core.procedure.models.value import (
    WeightedValue,
)


class PatchBid(ObjResponseMixin, BaseBid):
    items: list[LocalizationItem] | None = None
    parameters: list[PatchParameter] | None = None
    value: Value | None = None
    lotValues: list[PatchLotValue] | None = None
    tenderers: list[Supplier] | None = Field(None, min_length=1, max_length=1)
    status: (
        Literal["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"] | None
    ) = None
    subcontractingDetails: str | None = None
    selfQualified: Literal[True] | None = None
    selfEligible: Literal[True] | None = None

    @field_validator("parameters")
    @classmethod
    def validate_parameters_items(cls, value):
        validate_uniq_code(value)
        return value


class AdministratorPatchBid(Model):
    """
    Administrator may only fix the supplier identity of a bid,
    the commercial part (value, lotValues, status, ...) is untouchable
    """

    tenderers: list[Supplier] | None = Field(None, min_length=1, max_length=1)


class PatchQualificationBid(PatchBid):
    lotValues: list[LotValue] | None = None


class CommonBid(BaseBid):
    items: list[LocalizationItem] | None = Field(None, min_length=1)
    parameters: list[Parameter] | None = None
    value: Value | None = None
    initialValue: Value | None = None
    participationUrl: str | None = None
    lotValues: list[LotValue] | None = None
    tenderers: list[Supplier] | None = Field(None, min_length=1, max_length=1)
    status: Literal["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"]
    subcontractingDetails: str | None = None
    weightedValue: WeightedValue | None = None

    @field_validator("items")
    @classmethod
    def validate_items_items(cls, value):
        validate_uniq_id(value)
        return value

    @field_validator("parameters")
    @classmethod
    def validate_parameters_items(cls, value):
        validate_uniq_code(value)
        return value


class PostBid(ObjResponseMixin, CommonBid):
    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    tenderers: list[Supplier] = Field(min_length=1, max_length=1)
    lotValues: list[PostLotValue] | None = None
    parameters: list[Parameter] | None = None
    status: Literal["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"] = (
        "draft"
    )
    documents: list[PostDocument] | None = None
    financialDocuments: list[PostDocument] | None = None
    eligibilityDocuments: list[PostDocument] | None = None
    qualificationDocuments: list[PostDocument] | None = None
    selfQualified: Literal[True] | None = None
    selfEligible: Literal[True] | None = None

    @field_validator("parameters")
    @classmethod
    def validate_parameters_items(cls, value):
        validate_uniq_code(value)
        return value


class MetaBid(Model):
    id: MD5 | None = None
    date: str | None = None
    owner: str | None = None
    owner_token: str | None = None
    transfer_token: str | None = None
    submissionDate: IsoDateTime | None = None


class Bid(MetaBid, ObjResponseMixin, CommonBid):
    documents: list[Document] | None = None
    financialDocuments: list[Document] | None = None
    eligibilityDocuments: list[Document] | None = None
    qualificationDocuments: list[Document] | None = None
    selfQualified: Literal[True] | None = None
    selfEligible: Literal[True] | None = None
