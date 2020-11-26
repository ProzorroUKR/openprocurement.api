# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.esco.tests.base import test_tender_data, BaseESCOContentWebTest
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGRequirementEvidenceTestMixin,
)


class TenderCriteriaTest(TenderCriteriaTestMixin, BaseESCOContentWebTest):
    initial_data = test_tender_data
    test_lots_data = test_lots
    initial_status = "draft"


class TenderCriteriaRGTest(TenderCriteriaRGTestMixin, BaseESCOContentWebTest):
    initial_data = test_tender_data
    test_lots_data = test_lots


class TenderCriteriaRGRequirementTest(
    TenderCriteriaRGRequirementTestMixin,
    BaseESCOContentWebTest,
):
    initial_data = test_tender_data
    test_lots_data = test_lots


class TenderCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseESCOContentWebTest,
):
    initial_data = test_tender_data
    test_lots_data = test_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCriteriaTest))
    suite.addTest(unittest.makeSuite(TenderCriteriaRGTest))
    suite.addTest(unittest.makeSuite(TenderCriteriaRGRequirementTest))
    suite.addTest(unittest.makeSuite(TenderCriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
