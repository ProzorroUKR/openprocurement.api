# -*- coding: utf-8 -*-
from uuid import uuid4

from openprocurement.api.roles import RolesFromCsv
from schematics.types import StringType, MD5Type
from schematics.exceptions import ValidationError
from openprocurement.api.utils import get_now
from openprocurement.api.models import Model, ListType, IsoDateTimeType


class Change(Model):
    class Options:
        roles = RolesFromCsv('Change.csv', relative_to=__file__)

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(choices=['pending', 'active'], default='pending')
    date = IsoDateTimeType(default=get_now)
    rationale = StringType(required=True, min_length=1)
    rationale_en = StringType()
    rationale_ru = StringType()
    rationaleTypes = ListType(StringType(choices=['volumeCuts', 'itemPriceVariation',
                                                  'qualityImprovement', 'thirdParty',
                                                  'durationExtension', 'priceReduction',
                                                  'taxRate', 'fiscalYearExtension'],
                                         required=True), min_size=1, required=True)
    contractNumber = StringType()
    dateSigned = IsoDateTimeType()

    def validate_dateSigned(self, data, value):
        if value and value > get_now():
            raise ValidationError(u"Contract signature date can't be in the future")
