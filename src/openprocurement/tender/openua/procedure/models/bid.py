from schematics.types import StringType, BooleanType
from schematics.types.compound import ModelType
from openprocurement.api.models import Model
from openprocurement.tender.core.models import (
    ConfidentialDocumentModelType,
    validate_parameters_uniq,
)
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.validation import validate_bid_value
from openprocurement.tender.core.procedure.models.base import ListType
from openprocurement.tender.core.procedure.models.parameter import Parameter, PatchParameter
from openprocurement.tender.core.procedure.models.req_response import PostBidResponsesMixin, PatchBidResponsesMixin
from openprocurement.tender.openua.procedure.models.lot_value import LotValue, PostLotValue
from openprocurement.tender.openua.procedure.models.document import PostDocument, Document
from openprocurement.tender.core.procedure.models.bid import (
    Bid as BaseBid,
    PostBid as BasePostBid,
    PatchBid as BasePatchBid,
)


class UABidMixin(Model):
    selfEligible = BooleanType(choices=[True])
    selfQualified = BooleanType(choices=[True])
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PostLotValue, required=True))
    # parameters field below is the same as in the parent, but I keep order, so the tests pass
    # like, self.assertEqual(response.json["errors"], [error1, error2]) will fail if errors in different order
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])


class PatchBid(UABidMixin, BasePatchBid, PatchBidResponsesMixin):
    parameters = ListType(ModelType(PatchParameter, required=True), validators=[validate_parameters_uniq])


class PostBid(UABidMixin, BasePostBid, PostBidResponsesMixin):
    selfQualified = BooleanType(required=True, choices=[True])
    documents = ListType(ConfidentialDocumentModelType(PostDocument, required=True))

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            tender = get_tender()
            validate_bid_value(tender, value)


class Bid(UABidMixin, BaseBid, PostBidResponsesMixin):
    lotValues = ListType(ModelType(LotValue, required=True))
    documents = ListType(ConfidentialDocumentModelType(Document, required=True))

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            tender = get_tender()
            validate_bid_value(tender, value)
