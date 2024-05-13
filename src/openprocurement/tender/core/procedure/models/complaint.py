from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import BaseType, BooleanType, MD5Type, StringType
from schematics.types.serializable import serializable

from openprocurement.api.constants import COMPLAINT_IDENTIFIER_REQUIRED_FROM
from openprocurement.api.context import get_now, get_request
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.identifier import Identifier
from openprocurement.api.procedure.types import IsoDateTimeType, ListType, ModelType
from openprocurement.api.procedure.utils import is_item_owner
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.procedure.models.complaint_objection import (
    AwardComplaintObjection,
    CancellationComplaintObjection,
    Objection,
    QualificationComplaintObjection,
    TenderComplaintObjection,
)
from openprocurement.tender.core.procedure.models.document import Document, PostDocument
from openprocurement.tender.core.procedure.models.guarantee import Guarantee
from openprocurement.tender.core.procedure.models.organization import Organization
from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules
from openprocurement.tender.core.procedure.validation import (
    validate_numerated,
    validate_related_lot,
)


class ComplaintIdentifier(Identifier):
    id = BaseType(required=True)
    legalName = StringType(required=True)

    def validate_id(self, data, identifier_id):
        if not identifier_id:
            tender = get_tender()
            if get_first_revision_date(tender, default=get_now()) > COMPLAINT_IDENTIFIER_REQUIRED_FROM:
                raise ValidationError("This field is required.")

    def validate_legalName(self, data, value):
        if not value:
            tender = get_tender()
            if get_first_revision_date(tender, default=get_now()) > COMPLAINT_IDENTIFIER_REQUIRED_FROM:
                raise ValidationError("This field is required.")


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
        return get_now().isoformat()

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
            validate_items_uniq,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )
    documents = ListType(ModelType(PostDocument, required=True))

    def validate_status(self, data, value):
        if tender_created_after_2020_rules():
            data["status"] = "draft"

    def validate_type(self, data, value):
        if not value:
            if tender_created_after_2020_rules():
                raise ValidationError("This field is required")
            else:
                data["type"] = "complaint"

    def validate_relatedLot(self, data, related_lot):
        if related_lot:
            validate_related_lot(get_tender(), related_lot)


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
            validate_items_uniq,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )


class PostCancellationComplaint(PostComplaint):
    objections = ListType(
        ModelType(CancellationComplaintObjection, required=True),
        min_size=1,
        validators=[
            validate_items_uniq,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )


class PostQualificationComplaint(PostComplaintFromBid):
    objections = ListType(
        ModelType(QualificationComplaintObjection, required=True),
        min_size=1,
        validators=[
            validate_items_uniq,
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
            validate_items_uniq,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )


class DraftPatchAwardComplaint(DraftPatchComplaint):
    objections = ListType(
        ModelType(AwardComplaintObjection, required=True),
        min_size=1,
        validators=[
            validate_items_uniq,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )


class DraftPatchCancellationComplaint(DraftPatchComplaint):
    objections = ListType(
        ModelType(CancellationComplaintObjection, required=True),
        min_size=1,
        validators=[
            validate_items_uniq,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )


class DraftPatchQualificationComplaint(DraftPatchComplaint):
    objections = ListType(
        ModelType(QualificationComplaintObjection, required=True),
        min_size=1,
        validators=[
            validate_items_uniq,
            validate_numerated(field_name="sequenceNumber"),
        ],
    )


class CancellationPatchComplaint(Model):
    status = StringType(choices=["cancelled", "stopping"])  # TODO: different models for "cancelled", "stopping"
    cancellationReason = StringType()

    @serializable
    def dateCanceled(self):
        return get_now().isoformat()


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
        ]
    )
    rejectReasonDescription = StringType()
    reviewDate = IsoDateTimeType()
    reviewPlace = StringType()


class AdministratorPatchComplaint(Model):
    value = ModelType(Guarantee)


class Complaint(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    complaintID = StringType()
    date = IsoDateTimeType(default=get_now)  # autogenerated date of posting
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
            validate_items_uniq,
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

    value = ModelType(Guarantee)
    rejectReason = StringType(
        choices=[
            "buyerViolationsCorrected",
            "lawNonCompliance",
            "alreadyExists",
            "tenderCancelled",
            "cancelledByComplainant",
            "complaintPeriodEnded",
            "incorrectPayment",
        ]
    )

    # child structures
    posts = BaseType()
