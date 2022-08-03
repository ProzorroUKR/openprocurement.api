from openprocurement.tender.core.tests.qualification_milestone import TenderAwardMilestoneALPMixin
from openprocurement.tender.openeu.tests.base import BaseTenderContentWebTest, test_bids, test_lots


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderContentWebTest):
    initial_bids = test_bids
    initial_lots = test_lots
