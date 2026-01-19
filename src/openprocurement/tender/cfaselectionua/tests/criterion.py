import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.criterion_blanks import (
    create_patch_delete_evidences_from_requirement,
    delete_requirement_evidence,
    patch_criteria_rg,
    patch_tender_criteria_invalid,
)
from openprocurement.tender.cfaselectionua.tests.base import (
    TenderContentWebTest,
    test_tender_cfaselectionua_data,
    test_tender_cfaselectionua_lots,
    test_tender_cfaselectionua_required_criteria_ids,
)
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
)


class TenderCriteriaTest(TenderCriteriaTestMixin, TenderContentWebTest):
    initial_data = test_tender_cfaselectionua_data
    initial_lots = test_tender_cfaselectionua_lots
    test_lots_data = test_tender_cfaselectionua_lots
    initial_status = "draft"

    required_criteria = test_tender_cfaselectionua_required_criteria_ids

    test_patch_tender_criteria_invalid = snitch(patch_tender_criteria_invalid)


class TenderCriteriaRGTest(TenderCriteriaRGTestMixin, TenderContentWebTest):
    initial_data = test_tender_cfaselectionua_data
    test_lots_data = test_tender_cfaselectionua_lots
    initial_lots = test_tender_cfaselectionua_lots

    test_patch_criteria_rg = snitch(patch_criteria_rg)


class TenderCriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, TenderContentWebTest):
    initial_data = test_tender_cfaselectionua_data
    test_lots_data = test_tender_cfaselectionua_lots
    initial_lots = test_tender_cfaselectionua_lots
    allowed_put_statuses = ["active.enquiries", "active.tendering"]

    test_put_rg_requirement_valid_value_change = None  # FIXME: adopt test


class TenderCriteriaRGRequirementEvidenceTest(
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderContentWebTest,
):
    initial_data = test_tender_cfaselectionua_data
    test_lots_data = test_tender_cfaselectionua_lots
    initial_lots = test_tender_cfaselectionua_lots

    test_delete_requirement_evidence = snitch(delete_requirement_evidence)
    test_create_patch_delete_evidences_from_requirement = snitch(create_patch_delete_evidences_from_requirement)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGRequirementTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderCriteriaRGRequirementEvidenceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
