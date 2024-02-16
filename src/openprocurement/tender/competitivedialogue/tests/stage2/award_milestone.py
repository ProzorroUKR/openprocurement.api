from openprocurement.tender.competitivedialogue.tests.stage2.award import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    BaseTenderUAAwardPendingTest,
    test_tender_bids,
    test_tender_cd_lots,
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneALPMixin,
)


class TenderAwardMilestoneTestCase(TenderAwardMilestone24HMixin, BaseTenderUAAwardPendingTest):
    initial_lots = test_tender_cd_lots


class UATenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_bids = test_tender_bids
    initial_lots = test_tender_cd_lots


class EUTenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin, BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_bids = test_tender_bids
    initial_lots = test_tender_cd_lots
