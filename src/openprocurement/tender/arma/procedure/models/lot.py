from schematics.types import StringType, URLType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.value import AmountPercentageValue
from openprocurement.tender.arma.procedure.models.value import ARMAMinExpectedIncome
from openprocurement.tender.core.procedure.models.lot import BaseLot, PostBaseLot, TenderLotMixin
from openprocurement.tender.core.procedure.models.period import LotAuctionPeriod
from openprocurement.tender.core.procedure.models.value import BasicValue


class ARMAPostLot(PostBaseLot):
    value = ModelType(AmountPercentageValue, required=True)
    minimalStep = ModelType(AmountPercentageValue)
    guarantee = ModelType(BasicValue)
    minExpectedIncome = ModelType(ARMAMinExpectedIncome)


class ARMAPatchLot(BaseLot):
    title = StringType()
    value = ModelType(AmountPercentageValue)
    minimalStep = ModelType(AmountPercentageValue)
    guarantee = ModelType(BasicValue)
    minExpectedIncome = ModelType(ARMAMinExpectedIncome)
    status = StringType(choices=["active"])


class ARMAPostTenderLot(ARMAPostLot, TenderLotMixin):
    pass


class ARMAPatchTenderLot(BaseLot, TenderLotMixin):
    value = ModelType(AmountPercentageValue)
    minimalStep = ModelType(AmountPercentageValue)
    guarantee = ModelType(BasicValue)
    minExpectedIncome = ModelType(ARMAMinExpectedIncome)


class ARMALot(BaseLot, TenderLotMixin):
    value = ModelType(AmountPercentageValue, required=True)
    minimalStep = ModelType(AmountPercentageValue)
    guarantee = ModelType(BasicValue)
    minExpectedIncome = ModelType(ARMAMinExpectedIncome)

    auctionPeriod = ModelType(LotAuctionPeriod)
    auctionUrl = URLType()
