# -*- coding: utf-8 -*-
import unittest

from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_tender_below_data,
    test_tender_below_lots,
)
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGRequirementEvidenceTestMixin,
)
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.criterion_blanks import (
    activate_tender,
    patch_tender_criteria_invalid,
    patch_criteria_rg,
    delete_requirement_evidence,
    put_rg_requirement_invalid,
    put_rg_requirement_valid,
    create_patch_delete_evidences_from_requirement,
)


class TenderCriteriaTest(TenderCriteriaTestMixin, TenderContentWebTest):
    initial_data = test_tender_below_data
    test_lots_data = test_tender_below_lots
    initial_status = "draft"

    test_activate_tender = snitch(activate_tender)
    test_patch_tender_criteria_invalid = snitch(patch_tender_criteria_invalid)


class TenderCriteriaRGTest(TenderCriteriaRGTestMixin, TenderContentWebTest):
    initial_data = test_tender_below_data
    test_lots_data = test_tender_below_lots
    initial_status = "draft"

    test_patch_criteria_rg = snitch(patch_criteria_rg)


class TenderCriteriaRGRequirementTest(
    TenderCriteriaRGRequirementTestMixin,
    TenderContentWebTest
):
    initial_data = test_tender_below_data
    test_lots_data = test_tender_below_lots
    initial_status = "draft"
    allowed_put_statuses = ["active.enquiries"]

    test_put_rg_requirement_invalid = snitch(put_rg_requirement_invalid)
    test_put_rg_requirement_valid = snitch(put_rg_requirement_valid)


class TenderCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderContentWebTest,
):
    initial_data = test_tender_below_data
    test_lots_data = test_tender_below_lots
    initial_status = "active.enquiries"

    test_create_patch_delete_evidences_from_requirement = snitch(create_patch_delete_evidences_from_requirement)
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
