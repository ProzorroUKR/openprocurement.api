from uuid import uuid4

from schematics.types import BaseType, BooleanType, MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.context import get_request, get_request_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.api.validation import validate_uniq_id
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
from openprocurement.tender.core.procedure.validation import (
    validate_numerated,
)


class ComplaintIdentifier(Identifier):
    id = BaseType(required=True)
    legalName = StringType(required=True)


class ComplaintOrganization(Organization):
    identifier = ModelType(ComplaintIdentifier, required=True)


class PostComplaintOrganization(Organization):
    identifier = ModelType(ComplaintIdentifier, required=True)


class PostComplaint(Model):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def date(self):
        return get_request_now().isoformat()

    author = ModelType(PostComplaintOrganization, required=True)
    title = StringType(required=True)
    description = StringType()
    status = StringType(choices=["draft", "pending"], default="draft")
    type = StringType(choices=["complaint"], default="complaint")  # feel free to choose
    relatedLot = MD5Type()
    objections = ListType(
        ModelType(TenderComplaintObjection, required=True),
        min_size=1,
        validators=[
            validate_uniq_id,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )
    documents = ListType(ModelType(PostComplaintDocument, required=True))


class PostComplaintFromBid(PostComplaint):
    @serializable
    def bid_id(self):
        request = get_request()
        tender = get_tender()
        for bid in tender.get("bids", ""):
            if is_item_owner(request, bid):
                return bid["id"]


class PostAwardComplaint(PostComplaintFromBid):
    objections = ListType(
        ModelType(AwardComplaintObjection, required=True),
        min_size=1,
        validators=[
            validate_uniq_id,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )


class PostCancellationComplaint(PostComplaint):
    objections = ListType(
        ModelType(CancellationComplaintObjection, required=True),
        min_size=1,
        validators=[
            validate_uniq_id,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )


class PostQualificationComplaint(PostComplaintFromBid):
    objections = ListType(
        ModelType(QualificationComplaintObjection, required=True),
        min_size=1,
        validators=[
            validate_uniq_id,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )


class DraftPatchComplaint(Model):
    status = StringType(choices=["draft", "pending", "mistaken"])  # pending is for old rules
    author = ModelType(ComplaintOrganization)  # author of claim
    title = StringType()  # title of the claim
    description = StringType()  # description of the claim
    objections = ListType(
        ModelType(TenderComplaintObjection, required=True),
        min_size=1,
        validators=[
            validate_uniq_id,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )


class DraftPatchAwardComplaint(DraftPatchComplaint):
    objections = ListType(
        ModelType(AwardComplaintObjection, required=True),
        min_size=1,
        validators=[
            validate_uniq_id,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )


class DraftPatchCancellationComplaint(DraftPatchComplaint):
    objections = ListType(
        ModelType(CancellationComplaintObjection, required=True),
        min_size=1,
        validators=[
            validate_uniq_id,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )


class DraftPatchQualificationComplaint(DraftPatchComplaint):
    objections = ListType(
        ModelType(QualificationComplaintObjection, required=True),
        min_size=1,
        validators=[
            validate_uniq_id,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )


class CancellationPatchComplaint(Model):
    status = StringType(choices=["cancelled", "stopping"])  # TODO: different models for "cancelled", "stopping"
    cancellationReason = StringType()

    @serializable
    def dateCanceled(self):
        return get_request_now().isoformat()


class BotPatchComplaint(Model):
    status = StringType(choices=["pending", "mistaken"])
    rejectReason = StringType(
        choices=[
            "buyerViolationsCorrected",
            "lawNonCompliance",
            "alreadyExists",
            "tenderCancelled",
            "cancelledByComplainant",
            "complaintPeriodEnded",
            "incorrectPayment",
            "tenderOrLotCancelledBeforePayment",
        ]
    )


class TendererActionPatchComplaint(Model):
    tendererAction = StringType()

    # @serializable
    # def tendererActionDate(self):
    #     return get_now().isoformat()


class TendererResolvePatchComplaint(Model):
    tendererAction = StringType()
    status = StringType(choices=["satisfied", "resolved"])


class ReviewPatchComplaint(Model):
    status = StringType(choices=["accepted", "declined", "satisfied", "invalid", "mistaken", "stopped"])
    decision = StringType()
    rejectReason = StringType(
        choices=[
            "buyerViolationsCorrected",
            "lawNonCompliance",
            "alreadyExists",
            "tenderCancelled",
            "cancelledByComplainant",
            "complaintPeriodEnded",
            "incorrectPayment",
            "tenderOrLotCancelledBeforePayment",
        ]
    )
    rejectReasonDescription = StringType()
    reviewDate = IsoDateTimeType()
    reviewPlace = StringType()


class AdministratorPatchComplaint(Model):
    value = ModelType(BasicValue)


class Complaint(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    complaintID = StringType()
    date = IsoDateTimeType(default=get_request_now)  # autogenerated date of posting
    status = StringType(
        choices=[
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
    )
    documents = ListType(ModelType(Document, required=True))
    type = StringType(
        choices=["claim", "complaint"],
    )  # 'complaint' if status in ['pending'] or 'claim' if status in ['draft', 'claim', 'answered']
    owner_token = StringType()
    transfer_token = StringType()
    owner = StringType()
    relatedLot = MD5Type()
    bid_id = MD5Type()
    # complainant
    author = ModelType(ComplaintOrganization, required=True)  # author of claim
    title = StringType(required=True)  # title of the claim
    description = StringType()  # description of the claim
    dateSubmitted = IsoDateTimeType()
    objections = ListType(
        ModelType(Objection, required=True),
        min_size=1,
        validators=[
            validate_uniq_id,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )
    # tender owner
    resolution = StringType()
    resolutionType = StringType(choices=["invalid", "resolved", "declined"])
    dateAnswered = IsoDateTimeType()
    tendererAction = StringType()
    tendererActionDate = IsoDateTimeType()
    # complainant
    satisfied = BooleanType()
    dateEscalated = IsoDateTimeType()
    # reviewer
    decision = StringType()
    dateDecision = IsoDateTimeType()
    acceptance = BooleanType()
    dateAccepted = IsoDateTimeType()
    rejectReasonDescription = StringType()
    reviewDate = IsoDateTimeType()
    reviewPlace = StringType()

    # complainant
    cancellationReason = StringType()
    dateCanceled = IsoDateTimeType()

    value = ModelType(BasicValue)
    rejectReason = StringType(
        choices=[
            "buyerViolationsCorrected",
            "lawNonCompliance",
            "alreadyExists",
            "tenderCancelled",
            "cancelledByComplainant",
            "complaintPeriodEnded",
            "incorrectPayment",
            "tenderOrLotCancelledBeforePayment",
        ]
    )

    # child structures
    posts = BaseType()
    appeals = BaseType()
