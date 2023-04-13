from openprocurement.tender.belowthreshold.tests.award import TenderAwardPendingResourceTestCase
from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_tender_below_bids,
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneNoALPMixin,
)


class TenderAwardMilestone24HTestCase(TenderAwardMilestone24HMixin, TenderAwardPendingResourceTestCase):
    pass


class TenderAwardMilestoneNoALPTestCase(TenderAwardMilestoneNoALPMixin, TenderContentWebTest):
    initial_bids = test_tender_below_bids
