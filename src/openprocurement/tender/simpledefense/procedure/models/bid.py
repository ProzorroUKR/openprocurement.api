from openprocurement.tender.core.procedure.models.req_response import (
    BidResponsesMixin,
    PatchObjResponsesMixin,
)
from openprocurement.tender.openuadefense.procedure.models.bid import Bid as BaseBid
from openprocurement.tender.openuadefense.procedure.models.bid import (
    PatchBid as BasePatchBid,
)
from openprocurement.tender.openuadefense.procedure.models.bid import (
    PatchQualificationBid as BasePatchQualificationBid,
)
from openprocurement.tender.openuadefense.procedure.models.bid import (
    PostBid as BasePostBid,
)


class PostBid(BasePostBid, BidResponsesMixin):
    def validate_selfEligible(self, data, value):
        return  # to deactivate validation of selfEligible from BidResponsesMixin


class PatchBid(BasePatchBid, PatchObjResponsesMixin):
    def validate_selfEligible(self, data, value):
        return  # to deactivate validation of selfEligible from BidResponsesMixin


class PatchQualificationBid(BasePatchQualificationBid):
    def validate_selfEligible(self, data, value):
        return  # to deactivate validation of selfEligible from BidResponsesMixin


class Bid(BaseBid, BidResponsesMixin):
    def validate_selfEligible(self, data, value):
        return  # to deactivate validation of selfEligible from BidResponsesMixin
