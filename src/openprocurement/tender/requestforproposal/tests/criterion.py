import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.criterion_blanks import (
    create_patch_delete_evidences_from_requirement,
    patch_criteria_rg,
    patch_tender_criteria_invalid,
    put_rg_requirement_valid,
)
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
)
from openprocurement.tender.requestforproposal.tests.base import (
    TenderContentWebTest,
    test_tender_rfp_data,
    test_tender_rfp_lots,
)
from openprocurement.tender.requestforproposal.tests.criterion_blanks import (
    delete_requirement_evidence,
    put_rg_requirement_invalid,
)


class TenderCriteriaTest(TenderCriteriaTestMixin, TenderContentWebTest):
    initial_data = test_tender_rfp_data
    initial_lots = test_lots_data = test_tender_rfp_lots
    initial_status = "draft"

    required_criteria = ()

    test_patch_tender_criteria_invalid = snitch(patch_tender_criteria_invalid)


class TenderCriteriaRGTest(TenderCriteriaRGTestMixin, TenderContentWebTest):
    initial_data = test_tender_rfp_data
    test_lots_data = test_tender_rfp_lots
    initial_status = "draft"

    test_patch_criteria_rg = snitch(patch_criteria_rg)


class TenderCriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, TenderContentWebTest):
    initial_data = test_tender_rfp_data
    test_lots_data = test_tender_rfp_lots
    initial_status = "draft"
    allowed_put_statuses = ["active.enquiries"]

    test_put_rg_requirement_invalid = snitch(put_rg_requirement_invalid)
    test_put_rg_requirement_valid = snitch(put_rg_requirement_valid)
    test_put_rg_requirement_valid_value_change = None  # FIXME: adopt test


class TenderCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderContentWebTest,
):
    initial_data = test_tender_rfp_data
    test_lots_data = test_tender_rfp_lots
    initial_status = "active.enquiries"

    test_create_patch_delete_evidences_from_requirement = snitch(create_patch_delete_evidences_from_requirement)
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
