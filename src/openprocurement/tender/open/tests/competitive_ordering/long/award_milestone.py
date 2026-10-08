from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.utils import calculate_date, get_now
from openprocurement.tender.open.tests.below_threshold.base import test_tender_below_lots
from openprocurement.tender.open.tests.competitive_ordering.long.award import (
    BaseTenderCOLongContentWebTest,
    TenderAwardPendingResourceTestCase,
)
from openprocurement.tender.open.tests.competitive_ordering.long.base import (
    test_tender_co_long_bids,
    test_tender_co_long_data,
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneALPMixin,
)


@patch(
    "openprocurement.tender.core.procedure.state.award.NEW_ARTICLE_17_CRITERIA_REQUIRED",
    calculate_date(get_now(), timedelta(days=1)),
)
class TenderAwardMilestone24HTestCase(TenderAwardMilestone24HMixin, TenderAwardPendingResourceTestCase):
    initial_lots = test_tender_below_lots


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderCOLongContentWebTest):
    initial_data = test_tender_co_long_data
    initial_bids = test_tender_co_long_bids
    initial_lots = test_tender_below_lots * 2
