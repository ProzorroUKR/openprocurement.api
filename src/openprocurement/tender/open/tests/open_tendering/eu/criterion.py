import unittest

from openprocurement.tender.open.tests.below_threshold.base import test_tender_below_lots
from openprocurement.tender.open.tests.open_tendering.eu.base import (
    BaseTenderContentWebTest,
    test_tender_open_tendering_eu_data,
    test_tender_open_tendering_eu_required_criteria_ids,
)
from openprocurement.tender.open.tests.open_tendering.ua.criterion import (
    TenderCriteriaLccTestMixin,
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
)


class TenderOpenTenderingEUCriteriaTest(TenderCriteriaTestMixin, TenderCriteriaLccTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_open_tendering_eu_data
    initial_lots = test_tender_below_lots
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "draft"

    required_criteria = test_tender_open_tendering_eu_required_criteria_ids
    article_16_criteria_required = True


class TenderOpenTenderingEUCriteriaRGTest(TenderCriteriaRGTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_open_tendering_eu_data
    test_lots_data = test_tender_below_lots


class TenderOpenTenderingEUCriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_open_tendering_eu_data
    test_lots_data = test_tender_below_lots


class TenderOpenTenderingEUCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseTenderContentWebTest,
):
    initial_data = test_tender_open_tendering_eu_data
    test_lots_data = test_tender_below_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderOpenTenderingEUCriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderOpenTenderingEUCriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderOpenTenderingEUCriteriaRGRequirementTest))
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TenderOpenTenderingEUCriteriaRGRequirementEvidenceTest)
    )
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
