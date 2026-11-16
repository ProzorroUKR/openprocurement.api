from pydantic import Field

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import (
    MD5,
)
from openprocurement.tender.core.procedure.models.award import Award, PatchAward, PostAward
from openprocurement.tender.core.procedure.models.organization import ContactLessSupplier, Supplier


class LimitedAwardValue(Value):
    valueAddedTaxIncluded: bool = Field(default_factory=lambda: get_tender()["value"]["valueAddedTaxIncluded"])
    currency: str = Field(default_factory=lambda: get_tender()["value"]["currency"], min_length=3, max_length=3)


class LimitedPostAward(PostAward):
    bid_id: MD5 | None = None
    qualified: bool | None = None
    eligible: bool | None = None
    value: LimitedAwardValue
    weightedValue: LimitedAwardValue | None = None


class LimitedPatchAward(PatchAward):
    suppliers: list[Supplier] | None = Field(None, min_length=1, max_length=1)
    value: LimitedAwardValue | None = None
    lotID: MD5 | None = None


class LimitedAward(Award):
    bid_id: MD5 | None = None
    value: LimitedAwardValue
    weightedValue: LimitedAwardValue | None = None


class ReportingPostAward(LimitedPostAward):
    suppliers: list[ContactLessSupplier] = Field(min_length=1, max_length=1)
    value: Value


class ReportingPatchAward(LimitedPatchAward):
    suppliers: list[ContactLessSupplier] | None = Field(None, min_length=1, max_length=1)
    value: Value | None = None


class ReportingAward(LimitedAward):
    suppliers: list[ContactLessSupplier] = Field(min_length=1, max_length=1)
    value: Value
