# -*- coding: utf-8 -*-
from uuid import uuid4
from schematics.types import StringType, MD5Type
from schematics.exceptions import ValidationError
from schematics.transforms import whitelist
from openprocurement.api.utils import get_now
from openprocurement.api.models import Model, ListType, IsoDateTimeType
from openprocurement.api.models import  schematics_default_role, schematics_embedded_role


class Change(Model):
    class Options:
        roles = {
            # 'edit': blacklist('id', 'date'),
            'create': whitelist('rationale', 'rationale_ru', 'rationale_en', 'rationaleTypes', 'contractNumber', 'dateSigned'),
            'edit': whitelist('rationale', 'rationale_ru', 'rationale_en', 'rationaleTypes', 'contractNumber', 'status', 'dateSigned'),
            'view': schematics_default_role,
            'embedded': schematics_embedded_role,
        }

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
