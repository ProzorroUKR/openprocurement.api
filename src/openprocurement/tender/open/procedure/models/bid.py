from schematics.types import StringType, BooleanType
from schematics.types.compound import ModelType
from openprocurement.tender.core.models import validate_parameters_uniq
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.validation import validate_bid_value
from openprocurement.tender.core.procedure.models.base import ListType
from openprocurement.tender.core.procedure.models.parameter import Parameter, PatchParameter
from openprocurement.tender.core.procedure.models.req_response import PostBidResponsesMixin, PatchObjResponsesMixin
from openprocurement.tender.open.procedure.models.lot_value import LotValue, PostLotValue, PatchLotValue
from openprocurement.tender.open.procedure.models.document import PostDocument, Document
from openprocurement.tender.core.procedure.models.bid import (
    Bid as BaseBid,
    PostBid as BasePostBid,
    PatchBid as BasePatchBid,
)


class PatchBid(BasePatchBid, PatchObjResponsesMixin):
    selfEligible = BooleanType(choices=[True])
    selfQualified = BooleanType(choices=[True])
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PatchLotValue, required=True))
    parameters = ListType(ModelType(PatchParameter, required=True), validators=[validate_parameters_uniq])


class PostBid(BasePostBid, PostBidResponsesMixin):
    selfEligible = BooleanType(choices=[True])
    selfQualified = BooleanType(required=True, choices=[True])
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PostLotValue, required=True))
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])
    documents = ListType(ModelType(PostDocument, required=True))

    def validate_value(self, data, value):
        tender = get_tender()
        validate_bid_value(tender, value)


class Bid(BaseBid, PostBidResponsesMixin):
    selfEligible = BooleanType(choices=[True])
    selfQualified = BooleanType(required=True, choices=[True])
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(LotValue, required=True))
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])
    documents = ListType(ModelType(Document, required=True))

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            tender = get_tender()
            validate_bid_value(tender, value)
