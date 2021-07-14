from openprocurement.tender.core.procedure.models.base import (
    ListType,
    BaseBid,
    PatchBusinessOrganization,
    PostBusinessOrganization,
)
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.validation import validate_bid_value
from openprocurement.tender.competitivedialogue.procedure.models.lot_value import LotValue, PatchLotValue, PostLotValue
from openprocurement.tender.competitivedialogue.procedure.models.document import PostDocument, Document
from openprocurement.tender.core.procedure.models.req_response import PostBidResponsesMixin, PatchBidResponsesMixin
from openprocurement.tender.core.procedure.models.bid import MetaBid, validate_lot_values
from schematics.types.compound import ModelType
from schematics.types import BooleanType, StringType
from schematics.types.serializable import serializable
from uuid import uuid4


class PatchBid(PatchBidResponsesMixin, BaseBid):
    tenderers = ListType(ModelType(PatchBusinessOrganization, required=True), min_size=1, max_size=1)
    lotValues = ListType(ModelType(PatchLotValue, required=True))
    subcontractingDetails = StringType()
    selfQualified = BooleanType(choices=[True])
    selfEligible = BooleanType(choices=[True])
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
    )


class PostBid(PostBidResponsesMixin, BaseBid):

    @serializable
    def id(self):
        return uuid4().hex

    tenderers = ListType(ModelType(PostBusinessOrganization, required=True), required=True, min_size=1, max_size=1)
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PostLotValue, required=True), default=list)
    documents = ListType(ModelType(PostDocument, required=True), default=list)
    financialDocuments = ListType(ModelType(PostDocument, required=True), default=list)
    eligibilityDocuments = ListType(ModelType(PostDocument, required=True), default=list)
    qualificationDocuments = ListType(ModelType(PostDocument, required=True), default=list)

    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(choices=[True])
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
        default="pending",
    )

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            tender = get_tender()
            validate_bid_value(tender, value)

    def validate_lotValues(self, data, values):
        if data.get("status") != "draft":
            validate_lot_values(values)


class Bid(MetaBid, PostBidResponsesMixin, BaseBid):
    tenderers = ListType(ModelType(PostBusinessOrganization, required=True), required=True, min_size=1, max_size=1)
    lotValues = ListType(ModelType(LotValue, required=True))
    documents = ListType(ModelType(Document, required=True))
    financialDocuments = ListType(ModelType(Document, required=True))
    eligibilityDocuments = ListType(ModelType(Document, required=True))
    qualificationDocuments = ListType(ModelType(Document, required=True))
    subcontractingDetails = StringType()
    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(choices=[True])
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
    )

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            tender = get_tender()
            validate_bid_value(tender, value)

    def validate_lotValues(self, data, values):
        if data.get("status") != "draft":
            validate_lot_values(values)
