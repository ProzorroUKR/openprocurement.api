# -*- coding: utf-8 -*-
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist
from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType
from uuid import uuid4

from openprocurement.api.models import (
    IsoDateTimeType,
    ListType,
    Model,
    Organization,
    Period,
    Value,
    schematics_default_role,
    schematics_embedded_role
)
from openprocurement.api.utils import get_now

from openprocurement.frameworkagreement.cfaua.models.submodels.documents import Document
from openprocurement.frameworkagreement.cfaua.models.submodels.item import Item
# from openprocurement.frameworkagreement.cfaua.models.submodels.organization import Organization


class Agreement(Model):
    class Options:
        roles = {
            'create': blacklist('id', 'status', 'date', 'documents', 'dateSigned'),
            'edit': blacklist('id', 'documents', 'date', 'awardID', 'suppliers', 'items', 'agreementID'),
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }

    id = MD5Type(required=True, default=lambda: uuid4().hex)
    # awardIDs = ListType(StringType(), default=list())
    awardID = StringType()
    agreementID = StringType()
    agreementNumber = StringType()
    date = IsoDateTimeType()
    dateSigned = IsoDateTimeType()
    description = StringType()
    description_en = StringType()
    description_ru = StringType()
    documents = ListType(ModelType(Document), default=list())
    items = ListType(ModelType(Item))
    period = ModelType(Period)
    status = StringType(choices=['pending', 'terminated', 'active', 'cancelled'], default='pending')
    suppliers = ListType(ModelType(Organization), min_size=1, max_size=1)
    title = StringType()
    title_en = StringType()
    title_ru = StringType()
    value = ModelType(Value)

    def validate_dateSigned(self, data, value):
        if value and isinstance(data['__parent__'], Model):
            award = [i for i in data['__parent__'].awards if i.id == data['awardID']][0]
            if award.complaintPeriod.endDate >= value:
                raise ValidationError(
                    u"Agreement signature date should be after award complaint period end date ({})".format(
                        award.complaintPeriod.endDate.isoformat())
                )
            if value > get_now():
                raise ValidationError(u"Agreement signature date can't be in the future")

    def validate_awardID(self, data, awardID):
        if awardID and isinstance(data['__parent__'], Model) and \
                awardID not in [i.id for i in data['__parent__'].awards]:
            raise ValidationError(u"awardID should be one of awards")
