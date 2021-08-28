from schematics.types import BooleanType
from openprocurement.tender.core.procedure.models.bid import (
    PostBid as BasePostBid,
    PatchBid as BasePatchBid,
    Bid as BaseBid,
)
from openprocurement.tender.core.models import (
    ConfidentialDocumentModelType,
    validate_parameters_uniq,
)
from openprocurement.tender.core.procedure.models.parameter import Parameter, PatchParameter
from openprocurement.tender.openua.procedure.models.lot_value import LotValue, PostLotValue, PatchLotValue
from openprocurement.tender.openua.procedure.models.document import PostDocument, Document
from openprocurement.tender.core.procedure.models.base import ListType
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.validation import validate_bid_value
from schematics.types.compound import ModelType
from schematics.types import StringType


class PostBid(BasePostBid):
    selfEligible = BooleanType(choices=[True], required=True)
    selfQualified = BooleanType(choices=[True], required=True)
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PostLotValue, required=True))
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])
    documents = ListType(ConfidentialDocumentModelType(PostDocument, required=True))

    def validate_value(self, data, value):
        tender = get_tender()
        validate_bid_value(tender, value)


class PatchBid(BasePatchBid):
    selfEligible = BooleanType(choices=[True])
    selfQualified = BooleanType(choices=[True])
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PatchLotValue, required=True))
    parameters = ListType(ModelType(PatchParameter, required=True), validators=[validate_parameters_uniq])


class Bid(BaseBid):
    selfEligible = BooleanType(choices=[True], required=True)
    selfQualified = BooleanType(choices=[True], required=True)
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(LotValue, required=True))
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])
    documents = ListType(ConfidentialDocumentModelType(Document, required=True))

    def validate_value(self, data, value):
        tender = get_tender()
        validate_bid_value(tender, value)

