from schematics.types import StringType
from schematics.types.compound import ModelType
from openprocurement.tender.core.procedure.models.req_response import PostBidResponsesMixin, PatchObjResponsesMixin
from openprocurement.tender.core.procedure.models.base import ListType
from openprocurement.tender.core.procedure.models.bid import (
    PostBid as BasePostBid,
    PatchBid as BasePatchBid,
    Bid as BaseBid,
)
from openprocurement.tender.belowthreshold.procedure.models.lot_value import LotValue, PostLotValue, PatchLotValue


class PostBid(BasePostBid, PostBidResponsesMixin):
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PostLotValue, required=True))


class PatchBid(PatchObjResponsesMixin, BasePatchBid):
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PatchLotValue, required=True))


class Bid(PostBidResponsesMixin, BaseBid):
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(LotValue, required=True))
