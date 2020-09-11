# -*- coding: utf-8 -*-
import unittest
from mock import patch
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_stage2_data_ua,
    test_tender_stage2_data_eu,
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
)
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGRequirementEvidenceTestMixin,
)
from openprocurement.tender.competitivedialogue.tests.stage2.criterion_blanks import activate_tender


class TenderCDEUCriteriaTest(TenderCriteriaTestMixin, BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_data = test_tender_stage2_data_eu
    test_lots_data = test_lots
    initial_status = "draft"

    test_activate_tender = snitch(activate_tender)

    @patch("openprocurement.tender.core.validation.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
    def setUp(self):
        super(TenderCDEUCriteriaTest, self).setUp()


class TenderCDUACriteriaTest(TenderCriteriaTestMixin, BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_data = test_tender_stage2_data_ua
    test_lots_data = test_lots
    initial_status = "draft"

    test_activate_tender = snitch(activate_tender)

    @patch("openprocurement.tender.core.validation.RELEASE_ECRITERIA_ARTICLE_17", get_now() - timedelta(days=1))
    def setUp(self):
        super(TenderCDUACriteriaTest, self).setUp()


class TenderCDEUCriteriaRGTest(TenderCriteriaRGTestMixin, BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_data = test_tender_stage2_data_eu
    test_lots_data = test_lots


class TenderCDUACriteriaRGTest(TenderCriteriaRGTestMixin, BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_data = test_tender_stage2_data_ua
    test_lots_data = test_lots


class TenderCDEUCriteriaRGRequirementTest(
    TenderCriteriaRGRequirementTestMixin,
    BaseCompetitiveDialogEUStage2ContentWebTest
):
    initial_data = test_tender_stage2_data_eu
    test_lots_data = test_lots


class TenderCDUACriteriaRGRequirementTest(
    TenderCriteriaRGRequirementTestMixin,
    BaseCompetitiveDialogUAStage2ContentWebTest,
):
    initial_data = test_tender_stage2_data_ua
    test_lots_data = test_lots


class TenderCDEUCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseCompetitiveDialogEUStage2ContentWebTest,
):
    initial_data = test_tender_stage2_data_eu
    test_lots_data = test_lots


class TenderCDUACriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseCompetitiveDialogUAStage2ContentWebTest,
):
    initial_data = test_tender_stage2_data_ua
    test_lots_data = test_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCDEUCriteriaTest))
    suite.addTest(unittest.makeSuite(TenderCDEUCriteriaRGTest))
    suite.addTest(unittest.makeSuite(TenderCDEUCriteriaRGRequirementTest))
    suite.addTest(unittest.makeSuite(TenderCDEUCriteriaRGRequirementEvidenceTest))
    suite.addTest(unittest.makeSuite(TenderCDUACriteriaTest))
    suite.addTest(unittest.makeSuite(TenderCDUACriteriaRGTest))
    suite.addTest(unittest.makeSuite(TenderCDUACriteriaRGRequirementTest))
    suite.addTest(unittest.makeSuite(TenderCDUACriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
