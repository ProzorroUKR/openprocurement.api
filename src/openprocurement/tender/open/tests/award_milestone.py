from openprocurement.tender.open.tests.base import test_tender_open_data, test_tender_open_bids
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.open.tests.award import (
    TenderAwardPendingResourceTestCase,
    BaseTenderUAContentWebTest,
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneALPMixin,
)


class TenderAwardMilestone24HTestCase(TenderAwardMilestone24HMixin, TenderAwardPendingResourceTestCase):
    initial_lots = test_tender_below_lots


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderUAContentWebTest):
    initial_data = test_tender_open_data
    initial_bids = test_tender_open_bids
    initial_lots = test_tender_below_lots * 2
