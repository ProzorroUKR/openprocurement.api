# -*- coding: utf-8 -*-
from zope.interface import implementer
from schematics.types import IntType
from openprocurement.api.models import BaseTender
from openprocurement.tender.openua.interfaces import ITenderUA


@implementer(ITenderUA)
class TenderUA(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    __name__ = ''

    magicUnicorns = IntType(required=True)

#    def validate_tenderPeriod(self, data, period):
#        return
