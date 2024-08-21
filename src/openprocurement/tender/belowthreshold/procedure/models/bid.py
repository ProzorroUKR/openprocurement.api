from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.tender.belowthreshold.procedure.models.lot_value import (
    LotValue,
    PostLotValue,
)
from openprocurement.tender.core.procedure.models.bid import Bid as BaseBid
from openprocurement.tender.core.procedure.models.bid import PatchBid as BasePatchBid
from openprocurement.tender.core.procedure.models.bid import PostBid as BasePostBid
from openprocurement.tender.core.procedure.models.req_response import (
    PatchObjResponsesMixin,
    PostBidResponsesMixin,
)


class PostBid(BasePostBid, PostBidResponsesMixin):
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PostLotValue, required=True))


class PatchBid(PatchObjResponsesMixin, BasePatchBid):
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(LotValue, required=True))


class Bid(PostBidResponsesMixin, BaseBid):
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(LotValue, required=True))
