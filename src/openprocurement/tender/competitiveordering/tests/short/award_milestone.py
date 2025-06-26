from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.competitiveordering.tests.short.award import (
    BaseTenderCOShortContentWebTest,
    TenderAwardPendingResourceTestCase,
)
from openprocurement.tender.competitiveordering.tests.short.base import (
    test_tender_co_short_bids,
    test_tender_co_short_data,
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneALPMixin,
)


@patch(
    "openprocurement.tender.competitiveordering.procedure.state.award.NEW_ARTICLE_17_CRITERIA_REQUIRED",
    get_now() + timedelta(days=1),
)
class TenderAwardMilestone24HTestCase(TenderAwardMilestone24HMixin, TenderAwardPendingResourceTestCase):
    initial_lots = test_tender_below_lots


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderCOShortContentWebTest):
    initial_data = test_tender_co_short_data
    initial_bids = test_tender_co_short_bids
    initial_lots = test_tender_below_lots * 2
