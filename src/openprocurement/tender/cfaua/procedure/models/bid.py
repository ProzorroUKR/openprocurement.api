from schematics.types import StringType, BooleanType
from schematics.types.serializable import serializable
from openprocurement.tender.core.procedure.context import get_tender, get_now
from openprocurement.tender.core.procedure.models.req_response import PostBidResponsesMixin, PatchBidResponsesMixin
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from openprocurement.tender.core.procedure.models.bid import (
    Bid as BaseBid,
    PostBid as BasePostBid,
    PatchBid as BasePatchBid,
)
from openprocurement.tender.core.procedure.models.base import ListType
from openprocurement.tender.cfaua.procedure.models.lot_value import LotValue, PostLotValue, PatchLotValue
from openprocurement.tender.openua.procedure.models.document import (
    PostDocument,
    Document,
)
from openprocurement.api.constants import TWO_PHASE_COMMIT_FROM
from schematics.types.compound import ModelType


class PatchBid(PatchBidResponsesMixin, BasePatchBid):
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PatchLotValue, required=True))
    selfQualified = BooleanType(choices=[True])  # selfQualified, selfEligible are the same as in the parent but
    selfEligible = BooleanType(choices=[True])   # tests fail because they in different order
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
    )


class PostBid(PostBidResponsesMixin, BasePostBid):
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PostLotValue, required=True), default=list)

    documents = ListType(ModelType(PostDocument, required=True), default=list)
    financialDocuments = ListType(ModelType(PostDocument, required=True), default=list)
    eligibilityDocuments = ListType(ModelType(PostDocument, required=True), default=list)
    qualificationDocuments = ListType(ModelType(PostDocument, required=True), default=list)

    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(choices=[True])
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"]
    )

    @serializable(serialized_name="status", serialize_when_none=True)
    def default_status(self):
        if not self.status:
            if get_first_revision_date(get_tender(), default=get_now()) > TWO_PHASE_COMMIT_FROM:
                return "draft"
            return "pending"
        return self.status


class Bid(PostBidResponsesMixin, BaseBid):
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(LotValue, required=True))

    documents = ListType(ModelType(Document, required=True))
    financialDocuments = ListType(ModelType(Document, required=True))
    eligibilityDocuments = ListType(ModelType(Document, required=True))
    qualificationDocuments = ListType(ModelType(Document, required=True))

    selfQualified = BooleanType(required=True, choices=[True])

    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
        required=True
    )
