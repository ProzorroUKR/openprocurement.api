from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_tender_cfaua_bids,
    test_tender_cfaua_lots,
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestoneALPMixin,
)


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderContentWebTest):
    initial_bids = test_tender_cfaua_bids
    initial_lots = test_tender_cfaua_lots
