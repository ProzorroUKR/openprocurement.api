# -*- coding: utf-8 -*-
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.cfaselectionua.models.submodels.lotAuctionPeriod import LotAuctionPeriod
from schematics.types.compound import ModelType
from openprocurement.tender.core.models import Lot as BaseLot


class Lot(BaseLot):
    class Options:
        roles = RolesFromCsv('Lot.csv', relative_to=__file__)
    auctionPeriod = ModelType(LotAuctionPeriod, default={})

