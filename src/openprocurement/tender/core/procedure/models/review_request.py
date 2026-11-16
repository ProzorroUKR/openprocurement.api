from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    IsoDateTime,
)


class PostInspectorReview(Model):
    lotID: str | None = None


class PatchInspectorReviewRequest(Model):
    approved: bool
    description: str | None = None


class ReviewRequest(Model):
    id: str | None = None
    lotID: str | None = None
    tenderStatus: str
    approved: bool | None = None
    description: str | None = None
    dateCreated: IsoDateTime
    date: IsoDateTime | None = None
    is_valid: bool | None = None
