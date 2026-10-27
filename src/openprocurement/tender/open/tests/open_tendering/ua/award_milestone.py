from openprocurement.tender.open.tests.below_threshold.base import test_tender_below_lots
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneALPMixin,
)
from openprocurement.tender.open.tests.open_tendering.ua.award import (
    BaseTenderOpenTenderingUAContentWebTest,
    TenderAwardPendingResourceTestCase,
)
from openprocurement.tender.open.tests.open_tendering.ua.base import (
    test_tender_open_tendering_ua_bids,
    test_tender_open_tendering_ua_data,
)


class TenderAwardMilestone24HTestCase(TenderAwardMilestone24HMixin, TenderAwardPendingResourceTestCase):
    pass


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderOpenTenderingUAContentWebTest):
    initial_data = test_tender_open_tendering_ua_data
    initial_bids = test_tender_open_tendering_ua_bids
    initial_lots = test_tender_below_lots * 2
