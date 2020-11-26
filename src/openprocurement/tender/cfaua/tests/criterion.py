# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.tender.belowthreshold.tests.base import test_lots
from openprocurement.tender.cfaua.tests.base import test_tender_data, BaseTenderContentWebTest
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGRequirementEvidenceTestMixin,
)

tender_data = deepcopy(test_tender_data)
tender_data["status"] = "draft"


class TenderCriteriaTest(TenderCriteriaTestMixin, BaseTenderContentWebTest):
    initial_data = tender_data
    test_lots_data = test_lots


class TenderCriteriaRGTest(TenderCriteriaRGTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_data
    test_lots_data = test_lots


class TenderCriteriaRGRequirementTest(
    TenderCriteriaRGRequirementTestMixin,
    BaseTenderContentWebTest
):
    initial_data = test_tender_data
    test_lots_data = test_lots


class TenderCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseTenderContentWebTest,
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
