from openprocurement.tender.competitivedialogue.tests.stage2.award import (
    BaseTenderUAAwardPendingTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    BaseCompetitiveDialogEUStage2ContentWebTest,
    test_tender_bids, test_lots
)
from openprocurement.tender.core.tests.qualification_milestone import (
    TenderQualificationMilestone24HMixin,
    TenderQualificationMilestoneALPMixin,

)


class TenderAwardMilestoneTestCase(TenderQualificationMilestone24HMixin, BaseTenderUAAwardPendingTest):
    context_name = "award"


class UATenderAwardMilestoneALPTestCase(TenderQualificationMilestoneALPMixin,
                                        BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_bids = test_tender_bids
    initial_lots = test_lots


class EUTenderAwardMilestoneALPTestCase(TenderQualificationMilestoneALPMixin,
                                        BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_bids = test_tender_bids
    initial_lots = test_lots
