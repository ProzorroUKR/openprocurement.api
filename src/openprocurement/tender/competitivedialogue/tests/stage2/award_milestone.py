from openprocurement.tender.competitivedialogue.tests.stage2.award import (
    BaseTenderUAAwardPendingTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    BaseCompetitiveDialogEUStage2ContentWebTest,
    test_tender_bids, test_lots
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderMilestoneALPMixin,

)


class TenderAwardMilestoneTestCase(TenderAwardMilestone24HMixin, BaseTenderUAAwardPendingTest):
    pass


class UATenderAwardMilestoneALPTestCase(TenderMilestoneALPMixin,
                                        BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_bids = test_tender_bids
    initial_lots = test_lots


class EUTenderAwardMilestoneALPTestCase(TenderMilestoneALPMixin,
                                        BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_bids = test_tender_bids
    initial_lots = test_lots
