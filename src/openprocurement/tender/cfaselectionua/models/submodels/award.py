# -*- coding: utf-8 -*-
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.core.models import BaseAward
from schematics.exceptions import ValidationError
from schematics.types import (MD5Type)
from openprocurement.api.models import Model


class Award(BaseAward):
    """ An award for the given procurement. There may be more than one award
        per contracting process e.g. because the contract is split amongst
        different providers, or because it is a standing offer.
    """
    class Options:
        roles = RolesFromCsv('Award.csv', relative_to=__file__)
    bid_id = MD5Type(required=True)
    lotID = MD5Type()

    def validate_lotID(self, data, lotID):
        if isinstance(data['__parent__'], Model):
            if not lotID and data['__parent__'].lots:
                raise ValidationError(u'This field is required.')
            if lotID and lotID not in [i.id for i in data['__parent__'].lots]:
                raise ValidationError(u"lotID should be one of lots")
