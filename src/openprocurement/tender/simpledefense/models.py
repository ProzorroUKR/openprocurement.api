# -*- coding: utf-8 -*-
from schematics.types import StringType, BooleanType
from schematics.exceptions import ValidationError
from schematics.types.compound import ModelType
from zope.interface import implementer

from openprocurement.api.models import (
    SifterListType,
)
from openprocurement.tender.core.constants import (
    AWARD_CRITERIA_LOWEST_COST,
    AWARD_CRITERIA_LIFE_CYCLE_COST,
)
from openprocurement.tender.core.models import (
    BidResponsesMixin,
)
from openprocurement.tender.openuadefense.models import (
    Bid as BaseBid,
    Tender as BaseTender,
    IAboveThresholdUADefTender,
)


class ISimpleDefTender(IAboveThresholdUADefTender):
    """ Marker interface for aboveThresholdUA defense tenders """


class Bid(BaseBid, BidResponsesMixin):

    def validate_selfEligible(self, data, value):
        # for deactivate validation of selfEligible from BidResponsesMixin
        return


@implementer(ISimpleDefTender)
class Tender(BaseTender):
    """
    Data regarding tender process - publicly inviting prospective contractors
    to submit bids for evaluation and selecting a winner or winners.
    """

    awardCriteria = StringType(
        choices=[
            AWARD_CRITERIA_LOWEST_COST,
            AWARD_CRITERIA_LIFE_CYCLE_COST
        ],
        default=AWARD_CRITERIA_LOWEST_COST
    )
    procurementMethodType = StringType(default="simple.defense")
    bids = SifterListType(
        ModelType(Bid, required=True), default=list(), filter_by="status", filter_in_values=["invalid", "deleted"]
    )

    def validate_criteria(self, data, value):
        # for deactivate validation of criteria from parent class
        return

    def validate_awardCriteria(self, data, value):
        if value == AWARD_CRITERIA_LIFE_CYCLE_COST:
            if data.get("features", []):
                raise ValidationError("Can`t add features with {} awardCriteria".format(AWARD_CRITERIA_LIFE_CYCLE_COST))
