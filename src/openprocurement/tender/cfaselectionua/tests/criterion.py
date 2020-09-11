# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.criterion_blanks import (
    activate_tender,
    patch_tender_criteria_invalid,
    patch_criteria_rg,
    delete_requirement_evidence,
)
from openprocurement.tender.cfaselectionua.tests.base import test_tender_data, test_lots, TenderContentWebTest
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGRequirementEvidenceTestMixin,
)


class TenderCriteriaTest(TenderCriteriaTestMixin, TenderContentWebTest):
    initial_data = test_tender_data
    initial_lots = test_lots
    test_lots_data = test_lots
    initial_status = "active.enquiries"

    test_activate_tender = snitch(activate_tender)
    test_patch_tender_criteria_invalid = snitch(patch_tender_criteria_invalid)


class TenderCriteriaRGTest(TenderCriteriaRGTestMixin, TenderContentWebTest):
    initial_data = test_tender_data
    test_lots_data = test_lots
    initial_lots = test_lots

    test_patch_criteria_rg = snitch(patch_criteria_rg)


class TenderCriteriaRGRequirementTest(
    TenderCriteriaRGRequirementTestMixin,
    TenderContentWebTest
):
    initial_data = test_tender_data
    test_lots_data = test_lots
    initial_lots = test_lots


class TenderCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderContentWebTest,
):
    initial_data = test_tender_data
    test_lots_data = test_lots
    initial_lots = test_lots

    test_delete_requirement_evidence = snitch(delete_requirement_evidence)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderCriteriaTest))
    suite.addTest(unittest.makeSuite(TenderCriteriaRGTest))
    suite.addTest(unittest.makeSuite(TenderCriteriaRGRequirementTest))
    suite.addTest(unittest.makeSuite(TenderCriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
