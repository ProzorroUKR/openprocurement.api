import unittest
from datetime import timedelta
from unittest.mock import Mock, patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.openua.tests.criterion import (
    TenderCriteriaRGRequirementEvidenceTestMixin,
    TenderCriteriaRGRequirementTestMixin,
    TenderCriteriaRGTestMixin,
    TenderCriteriaTestMixin,
)
from openprocurement.tender.pricequotation.tests.base import (
    BaseTenderWebTest,
    TenderContentWebTest,
)
from openprocurement.tender.pricequotation.tests.criterion_blanks import (
    activate_tender,
    create_tender_criteria_invalid,
    create_tender_criteria_multi_profile,
    delete_requirement_evidence,
    get_tender_criteria,
    patch_criteria_rg,
    put_rg_requirement_valid,
)
from openprocurement.tender.pricequotation.tests.data import (
    test_tender_pq_category,
    test_tender_pq_short_profile,
)


@patch(
    "openprocurement.tender.core.procedure.models.criterion.PQ_CRITERIA_ID_FROM",
    get_now() + timedelta(days=1),
)
@patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_profile",
    Mock(return_value=test_tender_pq_short_profile),
)
@patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_category",
    Mock(return_value=test_tender_pq_category),
)
class TenderPQCriteriaTest(BaseTenderWebTest):
    def setUp(self):
        super().setUp()
        self.create_agreement()

    test_create_tender_criteria_multi_profile = snitch(create_tender_criteria_multi_profile)


class TenderPQ1CriteriaTest(TenderCriteriaTestMixin, TenderContentWebTest):
    initial_auth = ("Basic", ("broker", ""))
    initial_status = "draft"

    required_criteria = {}
    test_get_tender_criteria = snitch(get_tender_criteria)
    test_create_tender_criteria_invalid = snitch(create_tender_criteria_invalid)
    test_activate_tender = snitch(activate_tender)


class TenderPQCriteriaRGTest(TenderCriteriaRGTestMixin, TenderContentWebTest):
    test_patch_criteria_rg = snitch(patch_criteria_rg)


class TenderPQCriteriaRGRequirementTest(TenderCriteriaRGRequirementTestMixin, TenderContentWebTest):
    test_put_rg_requirement_valid = snitch(put_rg_requirement_valid)
    test_put_rg_requirement_valid_value_change = None


class TenderPQCriteriaRGRequirementEvidenceTest(
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
