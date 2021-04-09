# -*- coding: utf-8 -*-
from schematics.types import StringType
from schematics.exceptions import ValidationError
from zope.interface import implementer

from openprocurement.tender.core.models import (
    AWARD_CRITERIA_LOWEST_COST,
    AWARD_CRITERIA_LIFE_CYCLE_COST,
)
from openprocurement.tender.core.constants import CRITERION_LIFE_CYCLE_COST_IDS
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

    awardCriteria = StringType(
        choices=[
            AWARD_CRITERIA_LOWEST_COST,
            AWARD_CRITERIA_LIFE_CYCLE_COST
        ],
        default=AWARD_CRITERIA_LOWEST_COST
    )
    procurementMethodType = StringType(default="simple.defense")

    def validate_criteria(self, data, value):
        # for deactivate validation of criteria from parent class
        return

    def validate_awardCriteria(self, data, value):
        if value == AWARD_CRITERIA_LIFE_CYCLE_COST:
            if data.get("features", []):
                raise ValidationError("Can`t add features with {} awardCriteria".format(AWARD_CRITERIA_LIFE_CYCLE_COST))
