from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType, ModelType, IsoDateTimeType
from openprocurement.api.context import get_now, get_request
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.organization import Organization
from openprocurement.tender.core.procedure.models.document import Document
from openprocurement.tender.core.procedure.validation import validate_related_lot
from openprocurement.tender.core.procedure.utils import tender_created_after_2020_rules
from openprocurement.api.procedure.utils import is_item_owner
from schematics.types import StringType, MD5Type, BooleanType
from schematics.types.serializable import serializable
from schematics.exceptions import ValidationError
from uuid import uuid4


class PostClaim(Model):
    @serializable
    def id(self):
        return uuid4().hex

    @serializable
    def date(self):
        return get_now().isoformat()

    status = StringType(
        choices=[
            "draft",
            "claim",
            # "answered",
            # "pending",  # TODO delete pending status for claims?
            # "invalid",
            # "resolved",
            # "declined",
            # "cancelled",
            # "ignored",
        ],
        default="draft",
    )
    type = StringType(choices=["claim"])  # feel free to choose
    relatedLot = MD5Type()
    author = ModelType(Organization, required=True)
    title = StringType(required=True)
    description = StringType()

    def validate_type(self, data, value):
        if not value:
            if tender_created_after_2020_rules():
                raise ValidationError("This field is required")
            else:
                data["type"] = "claim"

    def validate_relatedLot(self, data, related_lot):
        if related_lot:
            validate_related_lot(get_tender(), related_lot)


class PostClaimFromBid(PostClaim):
    @serializable
    def bid_id(self):
        request = get_request()
        tender = get_tender()
        for bid in tender.get("bids", ""):
            if is_item_owner(request, bid):
                return bid["id"]


class TenderOwnerPatchClaim(Model):
    status = StringType(choices=["answered"])
    resolution = StringType()
    resolutionType = StringType(choices=["invalid", "resolved", "declined"])


class ClaimOwnerPatchClaim(Model):
    title = StringType()
    status = StringType(choices=["claim", "resolved", "cancelled"])
    satisfied = BooleanType()
    cancellationReason = StringType()


# patch actions
class ClaimOwnerClaimDraft(Model):
    title = StringType()
    description = StringType()
    author = ModelType(Organization)
    status = StringType(choices=["draft", "claim"])


class ClaimOwnerClaimCancellation(Model):
    status = StringType(choices=["cancelled"])
    cancellationReason = StringType()


class ClaimOwnerClaimSatisfy(Model):
    status = StringType(choices=["resolved"])
    satisfied = BooleanType()


class TenderOwnerClaimAnswer(Model):
    status = StringType(choices=["answered"])
    resolution = StringType()
    resolutionType = StringType(choices=["invalid", "resolved", "declined"])
    tendererAction = StringType()


class Claim(Model):
    id = MD5Type(required=True)
    complaintID = StringType(required=True)
    date = StringType(required=True)
    documents = ListType(ModelType(Document, required=True))

    author = ModelType(Organization, required=True)
    title = StringType(required=True)
    description = StringType()
    status = StringType(
        choices=[
            "draft",
            "claim",
            "answered",
            "pending",  # TODO delete pending status for claims?
            "invalid",
            "resolved",
            "declined",
            "cancelled",
            "ignored",
        ],
    )

    # tender owner
    resolution = StringType()
    resolutionType = StringType(choices=["invalid", "resolved", "declined"])
    dateAnswered = IsoDateTimeType()
    dateSubmitted = IsoDateTimeType()
    # tendererAction = StringType()
    # tendererActionDate = IsoDateTimeType()

    # complainant
    satisfied = BooleanType()
    cancellationReason = StringType()

    # system
    owner = StringType(required=True)
    owner_token = StringType(required=True)
    transfer_token = StringType()
    type = StringType(choices=["claim"], required=True)
    relatedLot = MD5Type()
    bid_id = MD5Type()
