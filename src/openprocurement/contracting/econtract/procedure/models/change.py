from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, computed_field, field_validator

from openprocurement.api.procedure.models.base import Model, validate_uniq_id
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import ContractValue
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.api.utils import get_now
from openprocurement.contracting.core.procedure.models.change import BaseChange
from openprocurement.contracting.core.procedure.models.item import Item
from openprocurement.contracting.core.procedure.models.milestone import (
    ContractMilestone,
)
from openprocurement.contracting.core.procedure.models.organization import (
    Buyer,
    Supplier,
)
from openprocurement.contracting.econtract.procedure.models.cancellation import (
    Cancellation,
)
from openprocurement.contracting.econtract.procedure.models.document import (
    ChangeDocument,
)
from openprocurement.contracting.econtract.procedure.models.signatory import Signatory


class Modifications(Model):
    title: str | None = None
    title_en: str | None = None
    description: str | None = None
    description_en: str | None = None
    period: Period | None = None
    value: ContractValue | None = None
    items: list[Item] | None = None
    contractNumber: str | None = None
    buyer: Buyer | None = None
    suppliers: list[Supplier] | None = Field(None, min_length=1, max_length=1)
    milestones: list[ContractMilestone] | None = None

    @field_validator("milestones")
    @classmethod
    def validate_milestones_items(cls, value):
        validate_uniq_id(value)
        return value


class PostChange(BaseChange):
    modifications: Modifications

    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def status(self) -> Any:
        return "pending"

    @computed_field
    def date(self) -> Any:
        return get_now().isoformat()


class Change(BaseChange):
    id: MD5
    status: Literal["pending", "active", "cancelled"] | None = None
    date: IsoDateTime | None = None
    dateSigned: IsoDateTime | None = None
    modifications: Modifications
    documents: list[ChangeDocument] | None = None
    cancellations: list[Cancellation] | None = None
    author: str | None = None
    signatories: list[Signatory] | None = None
