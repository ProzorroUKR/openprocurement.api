from openprocurement.tender.core.procedure.models.bid import LocalizationBid as BaseBid
from openprocurement.tender.core.procedure.models.bid import (
    PatchLocalizationBid as BasePatchBid,
)
from openprocurement.tender.core.procedure.models.bid import (
    PatchQualificationLocalizationBid as BasePatchQualificationBid,
)
from openprocurement.tender.core.procedure.models.bid import (
    PostLocalizationBid as BasePostBid,
)
from openprocurement.tender.core.procedure.models.req_response import (
    BidResponsesMixin,
    PatchObjResponsesMixin,
)


class PostBid(BasePostBid, BidResponsesMixin):
    pass


class PatchBid(PatchObjResponsesMixin, BasePatchBid):
    pass


class PatchQualificationBid(PatchObjResponsesMixin, BasePatchQualificationBid):
    pass


class Bid(BidResponsesMixin, BaseBid):
    pass
