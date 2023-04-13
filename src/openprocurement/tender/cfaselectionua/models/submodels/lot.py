# -*- coding: utf-8 -*-
from openprocurement.api.models import Value
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.cfaselectionua.models.submodels.lotAuctionPeriod import LotAuctionPeriod
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from openprocurement.tender.core.models import Lot as BaseLot


class Lot(BaseLot):
    class Options:
        roles = RolesFromCsv("Lot.csv", relative_to=__file__)

    value = ModelType(Value)
    minimalStep = ModelType(Value)
    auctionPeriod = ModelType(LotAuctionPeriod, default={})

    @serializable(serialized_name="value", type=ModelType(Value), serialize_when_none=False)
    def lot_value(self):
        if self.value:
            return self.value

    @serializable(serialized_name="minimalStep", type=ModelType(Value), serialize_when_none=False)
    def lot_minimalStep(self):
        if self.minimalStep:
            return self.minimalStep
