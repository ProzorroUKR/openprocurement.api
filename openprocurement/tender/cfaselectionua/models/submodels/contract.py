# -*- coding: utf-8 -*-
from openprocurement.api.roles import RolesFromCsv
from schematics.exceptions import ValidationError
from schematics.types.compound import ModelType
from schematics.types import StringType
from openprocurement.api.utils import get_now
from openprocurement.api.models import (
    Model, ListType,
    Contract as BaseContract,
    Value,
    Document
)


class Contract(BaseContract):
    class Options:
        roles = RolesFromCsv('Contract.csv', relative_to=__file__)

    value = ModelType(Value)
    awardID = StringType(required=True)
    documents = ListType(ModelType(Document), default=list())

    def validate_awardID(self, data, awardID):
        if awardID and isinstance(data['__parent__'], Model) and awardID not in [i.id for i in data['__parent__'].awards]:
            raise ValidationError(u"awardID should be one of awards")

    def validate_dateSigned(self, data, value):
        if value and isinstance(data['__parent__'], Model):
            if value > get_now():
                raise ValidationError(u"Contract signature date can't be in the future")
