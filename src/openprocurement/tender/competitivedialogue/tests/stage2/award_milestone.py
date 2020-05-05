from openprocurement.tender.competitivedialogue.tests.stage2.award import BaseTenderUAAwardPendingTest
from openprocurement.tender.core.tests.qualification_milestone import TenderQualificationMilestoneMixin


class TenderAwardMilestoneTestCase(TenderQualificationMilestoneMixin, BaseTenderUAAwardPendingTest):
    context_name = "award"
