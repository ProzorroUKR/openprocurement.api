from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestoneALPMixin,
)
from openprocurement.tender.open.tests.open_tendering.eu.base import (
    BaseTenderContentWebTest,
    test_tender_open_tendering_eu_bids,
    test_tender_open_tendering_eu_lots,
)


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderContentWebTest):
    initial_bids = test_tender_open_tendering_eu_bids
    initial_lots = test_tender_open_tendering_eu_lots
