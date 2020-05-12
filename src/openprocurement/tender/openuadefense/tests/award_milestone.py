from openprocurement.tender.openuadefense.tests.award import TenderAwardPendingResourceTestCase
from openprocurement.tender.openuadefense.tests.base import BaseTenderUAContentWebTest
from openprocurement.tender.openua.tests.base import test_bids
from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderQualificationMilestone24HMixin,
    TenderQualificationMilestoneALPMixin,
)


class TenderAwardMilestoneTestCase(TenderQualificationMilestone24HMixin, TenderAwardPendingResourceTestCase):
    context_name = "award"


class TenderAwardMilestoneALPTestCase(TenderQualificationMilestoneALPMixin, BaseTenderUAContentWebTest):
    initial_bids = test_bids
    initial_lots = test_lots

