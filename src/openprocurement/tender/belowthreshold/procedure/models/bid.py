from openprocurement.tender.core.procedure.models.req_response import PostBidResponsesMixin, PatchObjResponsesMixin
from openprocurement.tender.core.procedure.models.bid import (
    PostBid as BasePostBid,
    PatchBid as BasePatchBid,
    Bid as BaseBid,
)


class PostBid(BasePostBid, PostBidResponsesMixin):
    pass


class PatchBid(PatchObjResponsesMixin, BasePatchBid):
    pass


class Bid(PostBidResponsesMixin, BaseBid):
    pass
