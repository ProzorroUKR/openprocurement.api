import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.core.tests.mock import MockCriteriaIDMixin, MockMarketMixin
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
)
from openprocurement.tender.pricequotation.tests.base import TenderContentWebTest
from openprocurement.tender.pricequotation.tests.criterion_blanks import (
    create_tender_criteria_invalid,
    create_tender_criteria_multi_profile,
    delete_requirement_evidence,
    get_tender_criteria,
    patch_criteria_rg,
    put_rg_requirement_valid,
)
from openprocurement.tender.pricequotation.tests.data import (
    test_tender_pq_required_criteria_ids,
)


class TenderPQCriteriaTest(MockMarketMixin, MockCriteriaIDMixin, TenderCriteriaTestMixin, TenderContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "draft"
    initial_criteria = None

    required_criteria = test_tender_pq_required_criteria_ids

    test_get_tender_criteria = snitch(get_tender_criteria)
    test_create_tender_criteria_invalid = snitch(create_tender_criteria_invalid)
    test_create_tender_criteria_multi_profile = snitch(create_tender_criteria_multi_profile)


class TenderPQCriteriaRGTest(MockMarketMixin, TenderCriteriaRGTestMixin, TenderContentWebTest):
    initial_criteria = None

    test_patch_criteria_rg = snitch(patch_criteria_rg)


class TenderPQCriteriaRGRequirementTest(MockMarketMixin, TenderCriteriaRGRequirementTestMixin, TenderContentWebTest):
    initial_criteria = None

    test_put_rg_requirement_valid = snitch(put_rg_requirement_valid)
    test_put_rg_requirement_valid_value_change = None


class TenderPQCriteriaRGRequirementEvidenceTest(
    MockMarketMixin,
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderContentWebTest,
):
    test_delete_requirement_evidence = snitch(delete_requirement_evidence)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderPQCriteriaTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
