# -*- coding: utf-8 -*-
from openprocurement.tender.core.procedure.models.req_response import PostBidResponsesMixin, PatchBidResponsesMixin
from openprocurement.tender.core.procedure.models.bid import (
    PostBid as BasePostBid,
    PatchBid as BasePatchBid,
    Bid as BaseBid,
)


class PostBid(BasePostBid, PostBidResponsesMixin):
    pass


class PatchBid(PatchBidResponsesMixin, BasePatchBid):
    pass


class Bid(PostBidResponsesMixin, BaseBid):
    pass
