# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.competitivedialogue.tests.base import (
    test_tender_data_ua,
    test_tender_data_eu,
    BaseCompetitiveDialogEUContentWebTest,
    BaseCompetitiveDialogUAContentWebTest,
)
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGRequirementEvidenceTestMixin,
)


class TenderCDEUCriteriaTest(TenderCriteriaTestMixin, BaseCompetitiveDialogEUContentWebTest):
    initial_data = test_tender_data_eu
    test_lots_data = test_lots
    initial_status = "draft"


class TenderCDUACriteriaTest(TenderCriteriaTestMixin, BaseCompetitiveDialogUAContentWebTest):
    initial_data = test_tender_data_ua
    test_lots_data = test_lots
    initial_status = "draft"


class TenderCDEUCriteriaRGTest(TenderCriteriaRGTestMixin, BaseCompetitiveDialogEUContentWebTest):
    initial_data = test_tender_data_eu
    test_lots_data = test_lots


class TenderCDUACriteriaRGTest(TenderCriteriaRGTestMixin, BaseCompetitiveDialogUAContentWebTest):
    initial_data = test_tender_data_ua
    test_lots_data = test_lots


class TenderCDEUCriteriaRGRequirementTest(
    TenderCriteriaRGRequirementTestMixin,
    BaseCompetitiveDialogEUContentWebTest
):
    initial_data = test_tender_data_eu
    test_lots_data = test_lots


class TenderCDUACriteriaRGRequirementTest(
    TenderCriteriaRGRequirementTestMixin,
    BaseCompetitiveDialogUAContentWebTest
):
    initial_data = test_tender_data_ua
    test_lots_data = test_lots


class TenderCDEUCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseCompetitiveDialogEUContentWebTest,
):
    initial_data = test_tender_data_eu
    test_lots_data = test_lots


class TenderCDUACriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseCompetitiveDialogUAContentWebTest,
):
    initial_data = test_tender_data_ua
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
