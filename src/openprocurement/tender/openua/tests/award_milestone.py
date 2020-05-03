from openprocurement.tender.openua.tests.award import TenderAwardPendingResourceTestCase
from openprocurement.tender.core.tests.qualification_milestone import TenderQualificationMilestoneMixin


class TenderAwardMilestoneTestCase(TenderQualificationMilestoneMixin, TenderAwardPendingResourceTestCase):
    context_name = "award"
