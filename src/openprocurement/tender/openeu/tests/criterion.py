# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_tender_openeu_data,
)
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaLccTestMixin,
)


class TenderEUCriteriaTest(TenderCriteriaTestMixin, TenderCriteriaLccTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_openeu_data
    test_lots_data = test_tender_below_lots
    initial_status = "draft"


class TenderEUCriteriaRGTest(TenderCriteriaRGTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_openeu_data
    test_lots_data = test_tender_below_lots


class TenderEUCriteriaRGRequirementTest(
    TenderCriteriaRGRequirementTestMixin,
    BaseTenderContentWebTest
):
    initial_data = test_tender_openeu_data
    test_lots_data = test_tender_below_lots


class TenderEUCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseTenderContentWebTest,
):
    initial_data = test_tender_openeu_data
    test_lots_data = test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderEUCriteriaTest))
    suite.addTest(unittest.makeSuite(TenderEUCriteriaRGTest))
    suite.addTest(unittest.makeSuite(TenderEUCriteriaRGRequirementTest))
    suite.addTest(unittest.makeSuite(TenderEUCriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
