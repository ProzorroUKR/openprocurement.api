from openprocurement.tender.core.procedure.models.req_response import (
    PatchObjResponsesMixin,
    PostBidResponsesMixin,
)
from openprocurement.tender.openuadefense.procedure.models.bid import Bid as BaseBid
from openprocurement.tender.openuadefense.procedure.models.bid import (
    PatchBid as BasePatchBid,
)
from openprocurement.tender.openuadefense.procedure.models.bid import (
    PostBid as BasePostBid,
)


class PostBid(BasePostBid, PostBidResponsesMixin):
    def validate_selfEligible(self, data, value):
        return  # to deactivate validation of selfEligible from BidResponsesMixin


class PatchBid(BasePatchBid, PatchObjResponsesMixin):
    def validate_selfEligible(self, data, value):
        return  # to deactivate validation of selfEligible from BidResponsesMixin


class Bid(BaseBid, PostBidResponsesMixin):
    def validate_selfEligible(self, data, value):
        return  # to deactivate validation of selfEligible from BidResponsesMixin
