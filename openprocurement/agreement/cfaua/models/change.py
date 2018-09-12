# -*- coding: utf-8 -*-

from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType
from openprocurement.api.models import ListType

from openprocurement.agreement.core.models.change import Change as BaseChange


class Change(BaseChange):
    class Options:
        roles = RolesFromCsv('Change.csv', relative_to=__file__)

    rationaleTypes = ListType(StringType(choices=['volumeCuts', 'itemPriceVariation',
                                                  'qualityImprovement', 'thirdParty',
                                                  'durationExtension', 'priceReduction',
                                                  'taxRate', 'fiscalYearExtension'],
                                         required=True), min_size=1, required=True)
    agreementNumber = StringType()
