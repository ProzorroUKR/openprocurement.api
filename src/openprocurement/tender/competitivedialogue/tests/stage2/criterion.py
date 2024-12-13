import unittest
from datetime import timedelta
from unittest import mock

from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_tender_cdeu_stage2_data,
    test_tender_cdua_stage2_data,
)
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
)


class TenderCDEUCriteriaTest(TenderCriteriaTestMixin, BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_data = test_tender_cdeu_stage2_data
    initial_lots = test_lots_data = test_tender_below_lots
    initial_status = "draft"

    required_criteria = ()

    @mock.patch(
        "openprocurement.tender.core.procedure.state.tender_details.get_criteria_rules",
        mock.Mock(return_value={}),
    )
    @mock.patch(
        "openprocurement.tender.core.procedure.models.req_response.RELEASE_ECRITERIA_ARTICLE_17",
        get_now() - timedelta(days=1),
    )
    def setUp(self):
        super().setUp()


class TenderCDUACriteriaTest(TenderCriteriaTestMixin, BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_data = test_tender_cdua_stage2_data
    initial_lots = test_tender_below_lots
    initial_status = "draft"

    required_criteria = ()

    @mock.patch(
        "openprocurement.tender.core.procedure.state.tender_details.get_criteria_rules",
        mock.Mock(return_value={}),
    )
    @mock.patch(
        "openprocurement.tender.core.procedure.models.req_response.RELEASE_ECRITERIA_ARTICLE_17",
        get_now() - timedelta(days=1),
    )
    def setUp(self):
        super().setUp()


class TenderCDEUCriteriaRGTest(TenderCriteriaRGTestMixin, BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_data = test_tender_cdeu_stage2_data
    initial_lots = test_lots_data = test_tender_below_lots


class TenderCDUACriteriaRGTest(TenderCriteriaRGTestMixin, BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_data = test_tender_cdua_stage2_data
    initial_lots = test_lots_data = test_tender_below_lots


class TenderCDEUCriteriaRGRequirementTest(
    TenderCriteriaRGRequirementTestMixin, BaseCompetitiveDialogEUStage2ContentWebTest
):
    initial_data = test_tender_cdeu_stage2_data
    initial_lots = test_lots_data = test_tender_below_lots


class TenderCDUACriteriaRGRequirementTest(
    TenderCriteriaRGRequirementTestMixin,
    BaseCompetitiveDialogUAStage2ContentWebTest,
):
    initial_data = test_tender_cdua_stage2_data
    initial_lots = test_lots_data = test_tender_below_lots


class TenderCDEUCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseCompetitiveDialogEUStage2ContentWebTest,
):
    initial_data = test_tender_cdeu_stage2_data
    initial_lots = test_lots_data = test_tender_below_lots


class TenderCDUACriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseCompetitiveDialogUAStage2ContentWebTest,
):
    initial_data = test_tender_cdua_stage2_data
    initial_lots = test_lots_data = test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDEUCriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDEUCriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDEUCriteriaRGRequirementTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDEUCriteriaRGRequirementEvidenceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDUACriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDUACriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDUACriteriaRGRequirementTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCDUACriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
