# -*- coding: utf-8 -*-
from zope.interface import implementer
from schematics.types import IntType, StringType
from schematics.types.compound import ModelType, ListType
from openprocurement.api.models import Tender as BaseTender
from openprocurement.api.models import Bid as BaseBid
from openprocurement.tender.openua.interfaces import ITenderUA


class Bid(BaseBid):
    status = StringType(choices=['registration', 'validBid', 'invalidBid', 'deleted'])#, default='registration')


@implementer(ITenderUA)
class Tender(BaseTender):
    """Data regarding tender process - publicly inviting prospective contractors to submit bids for evaluation and selecting a winner or winners."""

    __name__ = ''

    bids = ListType(ModelType(Bid), default=list())  # A list of all the companies who entered submissions for the tender.
    procurementMethodType = StringType(default="aboveThresholdUA")
    magicUnicorns = IntType(required=True)
