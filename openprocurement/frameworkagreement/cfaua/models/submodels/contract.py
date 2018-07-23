# -*- coding: utf-8 -*-
from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType
from openprocurement.api.models import (
    IsoDateTimeType,
    ListType,
    Model,
    Organization,
)

from openprocurement.frameworkagreement.cfaua.models.submodels.unitprice import UnitPrice


class Contract(Model):
    id = MD5Type(required=True, default=lambda: uuid4().hex)
    status = StringType(choices=['active', 'unsuccessful'], default='active')
    suppliers = ListType(ModelType(Organization))
    unitPrices = ListType(ModelType(UnitPrice))
    awardID = StringType()
    bidID = StringType()
    date = IsoDateTimeType()

    def validate_awardID(self, data, awardID):
        if awardID and isinstance(data['__parent__'], Model) and \
                awardID not in [i.id for i in data['__parent__']['__parent__'].awards]:
            raise ValidationError(u"awardID should be one of awards")
