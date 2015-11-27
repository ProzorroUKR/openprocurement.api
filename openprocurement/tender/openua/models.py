# -*- coding: utf-8 -*-
from zope.interface import implementer
from schematics.types import IntType, StringType
from schematics.types.compound import ModelType, ListType
from openprocurement.api.models import Tender as BaseTender
from openprocurement.tender.openua.interfaces import ITenderUA


@implementer(ITenderUA)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    __name__ = ''

    procurementMethodType = StringType(default="aboveThresholdUA")
    magicUnicorns = IntType(required=True)
