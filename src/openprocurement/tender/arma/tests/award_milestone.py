from openprocurement.tender.arma.tests.base import (
    BaseTenderContentWebTest,
    test_tender_arma_bids,
    test_tender_arma_lots,
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestoneALPMixin,
)


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderContentWebTest):
    initial_bids = test_tender_arma_bids
    initial_lots = test_tender_arma_lots
    alp_period_work_days = 2
