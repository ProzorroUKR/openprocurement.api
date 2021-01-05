# -*- coding: utf-8 -*-
from schematics.types import StringType
from zope.interface import implementer
from openprocurement.tender.openuadefense.models import (
    Tender as BaseTender,
    IAboveThresholdUADefTender,
)


class ISimpleDefTender(IAboveThresholdUADefTender):
    """ Marker interface for aboveThresholdUA defense tenders """


@implementer(ISimpleDefTender)
class Tender(BaseTender):
    """
    Data regarding tender process - publicly inviting prospective contractors
    to submit bids for evaluation and selecting a winner or winners.
    """

    procurementMethodType = StringType(default="simple.defense")
