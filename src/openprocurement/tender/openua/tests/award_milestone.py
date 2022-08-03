from openprocurement.tender.openua.tests.base import test_tender_data, test_bids
from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.openua.tests.award import TenderAwardPendingResourceTestCase, BaseTenderUAContentWebTest
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneALPMixin,
)


class TenderAwardMilestone24HTestCase(TenderAwardMilestone24HMixin, TenderAwardPendingResourceTestCase):
    pass


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderUAContentWebTest):
    initial_data = test_tender_data
    initial_bids = test_bids
    initial_lots = test_lots * 2
