from openprocurement.tender.open.tests.below_threshold.base import test_tender_below_lots
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneALPMixin,
)
from openprocurement.tender.open.tests.above_threshold_ua.award import (
    BaseTenderUAContentWebTest,
    TenderAwardPendingResourceTestCase,
)
from openprocurement.tender.open.tests.above_threshold_ua.base import (
    test_tender_openua_bids,
    test_tender_openua_data,
)


class TenderAwardMilestone24HTestCase(TenderAwardMilestone24HMixin, TenderAwardPendingResourceTestCase):
    pass


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderUAContentWebTest):
    initial_data = test_tender_openua_data
    initial_bids = test_tender_openua_bids
    initial_lots = test_tender_below_lots * 2
