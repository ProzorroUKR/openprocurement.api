import unittest

from openprocurement.tender.arma.tests.base import (
    BaseTenderContentWebTest,
    test_tender_arma_data,
    test_tender_arma_lots,
    test_tender_arma_required_criteria_ids,
)
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
)


class TenderCriteriaTest(TenderCriteriaTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_arma_data
    initial_lots = test_tender_arma_lots
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "draft"

    required_criteria = test_tender_arma_required_criteria_ids


class TenderCriteriaRGTest(TenderCriteriaRGTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_arma_data
    test_lots_data = test_tender_arma_lots


class TenderCriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_arma_data
    test_lots_data = test_tender_arma_lots


class TenderCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseTenderContentWebTest,
):
    initial_data = test_tender_arma_data
    test_lots_data = test_tender_arma_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGRequirementTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
