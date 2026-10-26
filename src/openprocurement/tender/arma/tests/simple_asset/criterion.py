import unittest

from openprocurement.tender.arma.tests.simple_asset.base import (
    BaseTenderSimpleAssetContentWebTest,
    test_tender_arma_simple_data,
    test_tender_arma_simple_lots,
    test_tender_arma_simple_required_criteria_ids,
)
from openprocurement.tender.open.tests.above_threshold_ua.criterion import (
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
)


class TenderCriteriaTest(TenderCriteriaTestMixin, BaseTenderSimpleAssetContentWebTest):
    initial_data = test_tender_arma_simple_data
    initial_lots = test_tender_arma_simple_lots
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "draft"

    required_criteria = test_tender_arma_simple_required_criteria_ids


class TenderCriteriaRGTest(TenderCriteriaRGTestMixin, BaseTenderSimpleAssetContentWebTest):
    initial_data = test_tender_arma_simple_data
    test_lots_data = test_tender_arma_simple_lots


class TenderCriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, BaseTenderSimpleAssetContentWebTest):
    initial_data = test_tender_arma_simple_data
    test_lots_data = test_tender_arma_simple_lots


class TenderCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseTenderSimpleAssetContentWebTest,
):
    initial_data = test_tender_arma_simple_data
    test_lots_data = test_tender_arma_simple_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGRequirementTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
