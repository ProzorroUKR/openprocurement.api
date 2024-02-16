from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneALPMixin,
)
from openprocurement.tender.open.tests.award import (
    BaseTenderUAContentWebTest,
    TenderAwardPendingResourceTestCase,
)
from openprocurement.tender.open.tests.base import (
    test_tender_open_bids,
    test_tender_open_data,
)


class TenderAwardMilestone24HTestCase(TenderAwardMilestone24HMixin, TenderAwardPendingResourceTestCase):
    initial_lots = test_tender_below_lots


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderUAContentWebTest):
    initial_data = test_tender_open_data
    initial_bids = test_tender_open_bids
    initial_lots = test_tender_below_lots * 2
