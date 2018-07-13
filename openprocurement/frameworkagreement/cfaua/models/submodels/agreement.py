# -*- coding: utf-8 -*-
from schematics.exceptions import ValidationError
from schematics.transforms import blacklist
from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.models import ListType, Model, schematics_default_role, schematics_embedded_role
from openprocurement.api.utils import get_now
from openprocurement.tender.core.models import Contract as BaseContract

from openprocurement.frameworkagreement.cfaua.models.submodels.documents import Document
from openprocurement.frameworkagreement.cfaua.models.submodels.item import Item


class Agreement(BaseContract):
    class Options:
        roles = {
            'create': blacklist('id', 'status', 'date', 'documents', 'dateSigned'),
            'edit': blacklist('id', 'documents', 'date', 'awardID', 'suppliers', 'items', 'agreementID'),
            'embedded': schematics_embedded_role,
            'view': schematics_default_role,
        }

    contractID = None
    agreementID = StringType()
    documents = ListType(ModelType(Document), default=list())
    items = ListType(ModelType(Item))

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
