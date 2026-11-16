from typing import Any, Literal
from uuid import uuid4

from pydantic import Field, computed_field, field_validator

from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.base import Model, validate_uniq_id
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.types import (
    MD5,
    IsoDateTime,
)
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.tender.core.procedure.models.complaint_objection import (
    AwardComplaintObjection,
    CancellationComplaintObjection,
    Objection,
    QualificationComplaintObjection,
    TenderComplaintObjection,
)
from openprocurement.tender.core.procedure.models.document import (
    Document,
    PostComplaintDocument,
)
from openprocurement.tender.core.procedure.models.organization import Organization
from openprocurement.tender.core.procedure.models.value import BasicValue


class ComplaintIdentifier(Identifier):
    id: Any
    legalName: str


class ComplaintOrganization(Organization):
    identifier: ComplaintIdentifier


class PostComplaintOrganization(Organization):
    identifier: ComplaintIdentifier


class PostComplaint(Model):
    @computed_field
    def id(self) -> Any:
        return uuid4().hex

    @computed_field
    def date(self) -> Any:
        return get_request_now().isoformat()

    author: PostComplaintOrganization
    title: str
    description: str | None = None
    status: Literal["draft", "pending"] = "draft"
    type: Literal["complaint"] = "complaint"
    relatedLot: MD5 | None = None
    objections: list[TenderComplaintObjection] | None = Field(None, min_length=1)
    documents: list[PostComplaintDocument] | None = None

    @field_validator("objections")
    @classmethod
    def validate_objections_items(cls, value):
        validate_uniq_id(value)
        validate_numerated(field_name="sequenceNumber")(value)
        return value


class PostComplaintFromBid(PostComplaint):
    @computed_field
    def bid_id(self) -> Any:
        request = get_request()
        tender = get_tender()
        for bid in tender.get("bids", ""):
            if is_item_owner(request, bid):
                return bid["id"]


class PostAwardComplaint(PostComplaintFromBid):
    objections: list[AwardComplaintObjection] | None = Field(None, min_length=1)

    @field_validator("objections")
    @classmethod
    def validate_objections_items(cls, value):
        validate_uniq_id(value)
        validate_numerated(field_name="sequenceNumber")(value)
        return value


class PostCancellationComplaint(PostComplaint):
    objections: list[CancellationComplaintObjection] | None = Field(None, min_length=1)

    @field_validator("objections")
    @classmethod
    def validate_objections_items(cls, value):
        validate_uniq_id(value)
        validate_numerated(field_name="sequenceNumber")(value)
        return value


class PostQualificationComplaint(PostComplaintFromBid):
    objections: list[QualificationComplaintObjection] | None = Field(None, min_length=1)

    @field_validator("objections")
    @classmethod
    def validate_objections_items(cls, value):
        validate_uniq_id(value)
        validate_numerated(field_name="sequenceNumber")(value)
        return value


class DraftPatchComplaint(Model):
    status: Literal["draft", "pending", "mistaken"] | None = None
    author: ComplaintOrganization | None = None
    title: str | None = None
    description: str | None = None
    objections: list[TenderComplaintObjection] | None = Field(None, min_length=1)

    @field_validator("objections")
    @classmethod
    def validate_objections_items(cls, value):
        validate_uniq_id(value)
        validate_numerated(field_name="sequenceNumber")(value)
        return value


class DraftPatchAwardComplaint(DraftPatchComplaint):
    objections: list[AwardComplaintObjection] | None = Field(None, min_length=1)

    @field_validator("objections")
    @classmethod
    def validate_objections_items(cls, value):
        validate_uniq_id(value)
        validate_numerated(field_name="sequenceNumber")(value)
        return value


class DraftPatchCancellationComplaint(DraftPatchComplaint):
    objections: list[CancellationComplaintObjection] | None = Field(None, min_length=1)

    @field_validator("objections")
    @classmethod
    def validate_objections_items(cls, value):
        validate_uniq_id(value)
        validate_numerated(field_name="sequenceNumber")(value)
        return value


class DraftPatchQualificationComplaint(DraftPatchComplaint):
    objections: list[QualificationComplaintObjection] | None = Field(None, min_length=1)

    @field_validator("objections")
    @classmethod
    def validate_objections_items(cls, value):
        validate_uniq_id(value)
        validate_numerated(field_name="sequenceNumber")(value)
        return value


class CancellationPatchComplaint(Model):
    status: Literal["cancelled", "stopping"] | None = None
    cancellationReason: str | None = None

    @computed_field
    def dateCanceled(self) -> Any:
        return get_request_now().isoformat()


class BotPatchComplaint(Model):
    status: Literal["pending", "mistaken"] | None = None
    rejectReason: (
        Literal[
            "buyerViolationsCorrected",
            "lawNonCompliance",
            "alreadyExists",
            "tenderCancelled",
            "cancelledByComplainant",
            "complaintPeriodEnded",
            "incorrectPayment",
            "tenderOrLotCancelledBeforePayment",
        ]
        | None
    ) = None


class TendererActionPatchComplaint(Model):
    tendererAction: str | None = None


class TendererResolvePatchComplaint(Model):
    tendererAction: str | None = None
    status: Literal["satisfied", "resolved"] | None = None


class ReviewPatchComplaint(Model):
    status: Literal["accepted", "declined", "satisfied", "invalid", "mistaken", "stopped"] | None = None
    decision: str | None = None
    rejectReason: (
        Literal[
            "buyerViolationsCorrected",
            "lawNonCompliance",
            "alreadyExists",
            "tenderCancelled",
            "cancelledByComplainant",
            "complaintPeriodEnded",
            "incorrectPayment",
            "tenderOrLotCancelledBeforePayment",
        ]
        | None
    ) = None
    rejectReasonDescription: str | None = None
    reviewDate: IsoDateTime | None = None
    reviewPlace: str | None = None


class AdministratorPatchComplaint(Model):
    value: BasicValue | None = None


class Complaint(Model):
    id: MD5 = Field(default_factory=lambda: uuid4().hex)
    complaintID: str | None = None
    date: IsoDateTime = Field(default_factory=get_request_now)
    status: (
        Literal[
            "draft",
            "claim",
            "answered",
            "pending",
            "invalid",
            "resolved",
            "declined",
            "cancelled",
            "ignored",
            "mistaken",
            "accepted",
            "satisfied",
            "stopped",
        ]
        | None
    ) = None
    documents: list[Document] | None = None
    type: Literal["claim", "complaint"] | None = None
    owner_token: str | None = None
    transfer_token: str | None = None
    owner: str | None = None
    relatedLot: MD5 | None = None
    bid_id: MD5 | None = None
    author: ComplaintOrganization
    title: str
    description: str | None = None
    dateSubmitted: IsoDateTime | None = None
    objections: list[Objection] | None = Field(None, min_length=1)
    resolution: str | None = None
    resolutionType: Literal["invalid", "resolved", "declined"] | None = None
    dateAnswered: IsoDateTime | None = None
    tendererAction: str | None = None
    tendererActionDate: IsoDateTime | None = None
    satisfied: bool | None = None
    dateEscalated: IsoDateTime | None = None
    decision: str | None = None
    dateDecision: IsoDateTime | None = None
    acceptance: bool | None = None
    dateAccepted: IsoDateTime | None = None
    rejectReasonDescription: str | None = None
    reviewDate: IsoDateTime | None = None
    reviewPlace: str | None = None
    cancellationReason: str | None = None
    dateCanceled: IsoDateTime | None = None
    value: BasicValue | None = None
    rejectReason: (
        Literal[
            "buyerViolationsCorrected",
            "lawNonCompliance",
            "alreadyExists",
            "tenderCancelled",
            "cancelledByComplainant",
            "complaintPeriodEnded",
            "incorrectPayment",
            "tenderOrLotCancelledBeforePayment",
        ]
        | None
    ) = None
    posts: Any = None
    appeals: Any = None

    @field_validator("objections")
    @classmethod
    def validate_objections_items(cls, value):
        validate_uniq_id(value)
        validate_numerated(field_name="sequenceNumber")(value)
        return value


def validate_numerated(field_name="sequenceNumber"):
    def validator(value):
        if not value:
            return
        for i, obj in enumerate(value):
            number = getattr(obj, field_name)
            if number is not None and number != i + 1:  # field can be optional
                raise ValidationError(
                    f"Field {field_name} should contain incrementing sequence numbers starting from 1"
                )

    return validator
