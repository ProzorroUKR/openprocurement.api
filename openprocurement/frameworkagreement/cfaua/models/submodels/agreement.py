# -*- coding: utf-8 -*-
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist
from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType
from uuid import uuid4

from openprocurement.api.roles import RolesFromCsv
from openprocurement.api.models import (
    IsoDateTimeType,
    ListType,
    Model,
    Period,
    Value,
    schematics_default_role,
    schematics_embedded_role
)
from openprocurement.api.utils import get_now
from openprocurement.tender.core.models import Feature, validate_features_uniq

from openprocurement.frameworkagreement.cfaua.models.submodels.contract import Contract
from openprocurement.frameworkagreement.cfaua.models.submodels.documents import Document
from openprocurement.frameworkagreement.cfaua.models.submodels.item import Item


class Agreement(Model):
    class Options:
        roles = RolesFromCsv('Agreement.csv', relative_to=__file__)

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    agreementID = StringType()
    agreementNumber = StringType()
    date = IsoDateTimeType()
    dateSigned = IsoDateTimeType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    documents = ListType(ModelType(Document), default=list())
    features = ListType(ModelType(Feature), validators=[validate_features_uniq])
    items = ListType(ModelType(Item))
    period = ModelType(Period)
    status = StringType(choices=['pending', 'active', 'cancelled'], default='pending')
    contracts = ListType(ModelType(Contract))
    title = StringType()
    title_en = StringType()
    title_ru = StringType()

    def validate_dateSigned(self, data, value):
        awards_id = [c.awardID for c in data['contracts']]
        if value and isinstance(data['__parent__'], Model):
            award = [i for i in data['__parent__'].awards if i.id in awards_id][0]
            if award.complaintPeriod.endDate >= value:
                raise ValidationError(
                    u"Agreement signature date should be after award complaint period end date ({})".format(
                        award.complaintPeriod.endDate.isoformat())
                )
            if value > get_now():
                raise ValidationError(u"Agreement signature date can't be in the future")

    def get_awards_id(self):
        return tuple(c.awardID for c in self.contracts)
