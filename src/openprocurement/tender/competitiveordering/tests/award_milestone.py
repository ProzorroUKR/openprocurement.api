from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.competitiveordering.tests.award import (
    BaseTenderUAContentWebTest,
    TenderAwardPendingResourceTestCase,
)
from openprocurement.tender.competitiveordering.tests.base import (
    test_tender_co_bids,
    test_tender_co_data,
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneALPMixin,
)


class TenderAwardMilestone24HTestCase(TenderAwardMilestone24HMixin, TenderAwardPendingResourceTestCase):
    initial_lots = test_tender_below_lots


class TenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseTenderUAContentWebTest):
    initial_data = test_tender_co_data
    initial_bids = test_tender_co_bids
    initial_lots = test_tender_below_lots * 2
