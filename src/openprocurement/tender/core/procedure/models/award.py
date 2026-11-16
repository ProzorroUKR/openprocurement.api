from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, computed_field

from openprocurement.api.context import get_request_now
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.tender.core.procedure.models.award_milestone import (
    AwardMilestoneListMixin,
)
from openprocurement.tender.core.procedure.models.base import BaseAward
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.models.item import Item
from openprocurement.tender.core.procedure.models.organization import (
    Supplier,
)
from openprocurement.tender.core.procedure.models.req_response import (
    ObjResponseMixin,
)
from openprocurement.tender.core.procedure.models.value import (
    WeightedValue,
)


class PostAward(BaseAward):
    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def date(self) -> Any:
        return get_request_now().isoformat()

    status: Literal["pending"] = "pending"
    value: Value | None = None
    weightedValue: WeightedValue | None = None
    suppliers: list[Supplier] = Field(min_length=1, max_length=1)
    items: list[Item] | None = None
    bid_id: MD5
    lotID: MD5 | None = None
    complaintPeriod: Period | None = None
    subcontractingDetails: str | None = None


class PatchAward(ObjResponseMixin, BaseAward):
    status: Literal["pending", "active", "unsuccessful", "cancelled"] | None = None
    qualified: bool | None = None
    eligible: bool | None = None
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
    items: list[Item] | None = None
    subcontractingDetails: str | None = None


class Award(AwardMilestoneListMixin, ObjResponseMixin, BaseAward):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    status: Literal["pending", "active", "unsuccessful", "cancelled"]
    date: IsoDateTime
    value: Value | None = None
    weightedValue: WeightedValue | None = None
    suppliers: list[Supplier] = Field(min_length=1, max_length=1)
    bid_id: MD5
    lotID: MD5 | None = None
    complaintPeriod: Period | None = None
    subcontractingDetails: str | None = None
    complaints: Any = None
    documents: list[Document] | None = None
    items: list[Item] | None = None
    period: Period | None = None
    qualified: bool | None = None
    eligible: bool | None = None
    title: str | None = None
    title_en: str | None = None
    title_ru: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_ru: str | None = None
