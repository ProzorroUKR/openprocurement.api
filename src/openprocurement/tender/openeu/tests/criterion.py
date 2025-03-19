import unittest

from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_tender_openeu_data,
    test_tender_openeu_required_criteria_ids,
)
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaLccTestMixin,
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
)


class TenderEUCriteriaTest(TenderCriteriaTestMixin, TenderCriteriaLccTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_openeu_data
    initial_lots = test_tender_below_lots
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "draft"

    required_criteria = test_tender_openeu_required_criteria_ids
    article_16_criteria_required = True


class TenderEUCriteriaRGTest(TenderCriteriaRGTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_openeu_data
    test_lots_data = test_tender_below_lots


class TenderEUCriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, BaseTenderContentWebTest):
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
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEUCriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEUCriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEUCriteriaRGRequirementTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderEUCriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
