from openprocurement.tender.competitivedialogue.tests.stage2.award import (
    BaseTenderUAAwardPendingTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    BaseCompetitiveDialogEUStage2ContentWebTest,
    test_tender_bids,
    test_tender_cd_lots
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderAwardMilestone24HMixin,
    TenderAwardMilestoneALPMixin,

)


class TenderAwardMilestoneTestCase(TenderAwardMilestone24HMixin, BaseTenderUAAwardPendingTest):
    pass


class UATenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin,
                                        BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_bids = test_tender_bids
    initial_lots = test_tender_cd_lots


class EUTenderAwardMilestoneALPTestCase(TenderAwardMilestoneALPMixin,
                                        BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_bids = test_tender_bids
    initial_lots = test_tender_cd_lots
