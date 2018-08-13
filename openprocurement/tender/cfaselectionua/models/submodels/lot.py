# -*- coding: utf-8 -*-
from openprocurement.tender.cfaselectionua.models.submodels.lotAuctionPeriod import LotAuctionPeriod
from schematics.types.compound import ModelType
from openprocurement.tender.core.models import Lot as BaseLot


class Lot(BaseLot):
    auctionPeriod = ModelType(LotAuctionPeriod, default={})

