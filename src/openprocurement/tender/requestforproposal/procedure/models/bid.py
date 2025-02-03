from openprocurement.tender.core.procedure.models.bid import LocalizationBid as BaseBid
from openprocurement.tender.core.procedure.models.bid import (
    PatchLocalizationBid as BasePatchBid,
)
from openprocurement.tender.core.procedure.models.bid import (
    PostLocalizationBid as BasePostBid,
)
from openprocurement.tender.core.procedure.models.req_response import (
    PatchObjResponsesMixin,
    PostBidResponsesMixin,
)


class PostBid(BasePostBid, PostBidResponsesMixin):
    pass


class PatchBid(PatchObjResponsesMixin, BasePatchBid):
    pass


class Bid(PostBidResponsesMixin, BaseBid):
    pass
