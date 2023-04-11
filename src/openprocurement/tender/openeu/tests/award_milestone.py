from openprocurement.tender.core.tests.qualification_milestone import TenderAwardMilestoneALPMixin
from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_tender_openeu_bids,
    test_tender_openeu_lots,
)


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderContentWebTest):
    initial_bids = test_tender_openeu_bids
    initial_lots = test_tender_openeu_lots
