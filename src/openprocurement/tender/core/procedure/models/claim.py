from typing import Any, Literal
from uuid import uuid4

from pydantic import computed_field

from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.models.organization import Organization


class PostClaim(Model):
    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def date(self) -> Any:
        return get_request_now().isoformat()

    status: Literal["draft", "claim"] = "draft"
    type: Literal["claim"] | None = None
    relatedLot: MD5 | None = None
    author: Organization
    title: str
    description: str | None = None


class PostClaimFromBid(PostClaim):
    @computed_field
    def bid_id(self) -> Any:
        request = get_request()
        tender = get_tender()
        for bid in tender.get("bids", ""):
            if is_item_owner(request, bid):
                return bid["id"]


class TenderOwnerPatchClaim(Model):
    status: Literal["answered"] | None = None
    resolution: str | None = None
    resolutionType: Literal["invalid", "resolved", "declined"] | None = None


class ClaimOwnerPatchClaim(Model):
    title: str | None = None
    status: Literal["claim", "resolved", "cancelled"] | None = None
    satisfied: bool | None = None
    cancellationReason: str | None = None


class ClaimOwnerClaimDraft(Model):
    title: str | None = None
    description: str | None = None
    author: Organization | None = None
    status: Literal["draft", "claim"] | None = None


class ClaimOwnerClaimCancellation(Model):
    status: Literal["cancelled"] | None = None
    cancellationReason: str | None = None


class ClaimOwnerClaimSatisfy(Model):
    status: Literal["resolved"] | None = None
    satisfied: bool | None = None


class TenderOwnerClaimAnswer(Model):
    status: Literal["answered"] | None = None
    resolution: str | None = None
    resolutionType: Literal["invalid", "resolved", "declined"] | None = None
    tendererAction: str | None = None


class Claim(Model):
    id: MD5
    complaintID: str
    date: str
    documents: list[Document] | None = None
    author: Organization
    title: str
    description: str | None = None
    status: (
        Literal["draft", "claim", "answered", "invalid", "resolved", "declined", "cancelled", "ignored", "pending"]
        | None
    ) = None
    resolution: str | None = None
    resolutionType: Literal["invalid", "resolved", "declined"] | None = None
    dateAnswered: IsoDateTime | None = None
    dateSubmitted: IsoDateTime | None = None
    satisfied: bool | None = None
    cancellationReason: str | None = None
    owner: str
    owner_token: str
    transfer_token: str | None = None
    type: Literal["claim"]
    relatedLot: MD5 | None = None
    bid_id: MD5 | None = None
