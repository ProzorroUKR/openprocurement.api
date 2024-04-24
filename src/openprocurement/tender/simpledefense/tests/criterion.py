import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_lots
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
)
from openprocurement.tender.simpledefense.tests.base import (
    BaseSimpleDefContentWebTest,
    test_tender_simpledefense_data,
)
from openprocurement.tender.simpledefense.tests.criterion_blanks import (
    delete_requirement_evidence,
)


class TenderCriteriaTest(TenderCriteriaTestMixin, BaseSimpleDefContentWebTest):
    initial_data = test_tender_simpledefense_data
    initial_lots = test_tender_below_lots
    test_lots_data = test_tender_below_lots
    initial_status = "draft"

    required_criteria = ()


class TenderCriteriaRGTest(TenderCriteriaRGTestMixin, BaseSimpleDefContentWebTest):
    initial_data = test_tender_simpledefense_data
    test_lots_data = test_tender_below_lots
    initial_lots = test_tender_below_lots


class TenderCriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, BaseSimpleDefContentWebTest):
    initial_data = test_tender_simpledefense_data
    test_lots_data = test_tender_below_lots
    initial_lots = test_tender_below_lots


class TenderCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    BaseSimpleDefContentWebTest,
):
    initial_data = test_tender_simpledefense_data
    test_lots_data = test_tender_below_lots
    initial_lots = test_tender_below_lots

    test_delete_requirement_evidence = snitch(delete_requirement_evidence)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGRequirementTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
