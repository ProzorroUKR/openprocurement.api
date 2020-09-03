from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.cfaua.models.submodels.guarantee import Guarantee
from openprocurement.tender.cfaua.models.submodels.periods import LotAuctionPeriod
from openprocurement.tender.cfaua.models.submodels.value import Value
from openprocurement.tender.core.models import LotWithMinimalStepLimitsValidation as BaseLot
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable


class Lot(BaseLot):
    class Options:
        roles = RolesFromCsv("Lot.csv", relative_to=__file__)

    auctionPeriod = ModelType(LotAuctionPeriod, default={})
    value = ModelType(Value, required=True)
    minimalStep = ModelType(Value, required=True)
    guarantee = ModelType(Guarantee)

    @serializable
    def numberOfBids(self):
        """A property that is serialized by schematics exports."""
        bids = [
            bid
            for bid in self.__parent__.bids
            if self.id in [i.relatedLot for i in bid.lotValues if i.status in ["active", "pending"]]
            and bid.status in ["active", "pending"]
        ]
        return len(bids)
