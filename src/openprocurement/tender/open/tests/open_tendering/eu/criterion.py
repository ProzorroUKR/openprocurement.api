import unittest

from openprocurement.tender.core.tests.base import test_article_20_criteria
from openprocurement.tender.open.tests.open_tendering.eu.base import (
    BaseTenderContentWebTest,
    test_tender_open_tendering_eu_data,
    test_tender_open_tendering_eu_lots,
    test_tender_open_tendering_eu_required_criteria_ids,
)
from openprocurement.tender.open.tests.open_tendering.ua.criterion import (
    TenderCriteriaLccTestMixin,
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
    TenderSelectionCriteriaPerLotTestMixin,
)


class TenderOpenTenderingEUCriteriaTest(TenderCriteriaTestMixin, TenderCriteriaLccTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_open_tendering_eu_data
    initial_lots = test_tender_open_tendering_eu_lots
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "draft"

    required_criteria = test_tender_open_tendering_eu_required_criteria_ids
    selection_criteria_required = True
    selection_criteria_label = "article 20"
    selection_criteria_data = test_article_20_criteria


class TenderOpenTenderingEUSelectionCriteriaPerLotTest(
    TenderSelectionCriteriaPerLotTestMixin, BaseTenderContentWebTest
):
    initial_data = test_tender_open_tendering_eu_data
    initial_lots = 2 * test_tender_open_tendering_eu_lots


class TenderOpenTenderingEUCriteriaRGTest(TenderCriteriaRGTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_open_tendering_eu_data
    test_lots_data = test_tender_open_tendering_eu_lots


class TenderOpenTenderingEUCriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, BaseTenderContentWebTest):
    initial_data = test_tender_open_tendering_eu_data
    test_lots_data = test_tender_open_tendering_eu_lots


class TenderOpenTenderingEUCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseTenderContentWebTest,
):
    initial_data = test_tender_open_tendering_eu_data
    test_lots_data = test_tender_open_tendering_eu_lots


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderOpenTenderingEUCriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderOpenTenderingEUSelectionCriteriaPerLotTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderOpenTenderingEUCriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderOpenTenderingEUCriteriaRGRequirementTest))
    suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TenderOpenTenderingEUCriteriaRGRequirementEvidenceTest)
    )
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
