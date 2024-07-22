import unittest
from copy import deepcopy
from datetime import timedelta
from unittest.mock import Mock, patch

from openprocurement.api.tests.base import snitch
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    create_tender_bid_document_json,
    create_tender_bid_document_json_bulk,
    create_tender_bid_with_document,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_documents,
    not_found,
    put_tender_bid_document_json,
)
from openprocurement.tender.openua.tests.bid_blanks import bids_related_product
from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest,
    test_tender_pq_bids,
    test_tender_pq_category,
    test_tender_pq_criteria,
    test_tender_pq_organization,
    test_tender_pq_requirement_response,
    test_tender_pq_short_profile,
)
from openprocurement.tender.pricequotation.tests.bid_blanks import (
    bid_Administrator_change,
    create_tender_bid,
    create_tender_bid_invalid,
    delete_tender_bid,
    deleted_bid_do_not_locks_tender_in_state,
    deleted_bid_is_not_restorable,
    get_tender_bid,
    get_tender_tenderers,
    invalidate_not_agreement_member_bid_via_chronograph,
    patch_tender_bid,
    patch_tender_bid_document,
    requirement_response_validation_multiple_criterias,
    requirement_response_validation_multiple_groups,
    requirement_response_validation_multiple_groups_multiple_requirements,
    requirement_response_validation_one_group_multiple_requirements,
    requirement_response_value_validation_for_expected_values,
)
from openprocurement.tender.pricequotation.tests.data import (
    test_tender_pq_criteria_1,
    test_tender_pq_criteria_2,
    test_tender_pq_criteria_3,
    test_tender_pq_criteria_4,
)
from openprocurement.tender.pricequotation.tests.utils import criteria_drop_uuids


@patch(
    "openprocurement.tender.core.procedure.models.criterion.PQ_CRITERIA_ID_FROM",
    get_now() + timedelta(days=1),
)
class TenderBidResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = test_tender_pq_criteria
    test_bids_data = test_tender_pq_bids

    test_create_tender_bid_invalid = snitch(create_tender_bid_invalid)
    test_create_tender_bid = snitch(create_tender_bid)
    test_patch_tender_bid = snitch(patch_tender_bid)
    test_get_tender_bid = snitch(get_tender_bid)
    test_delete_tender_bid = snitch(delete_tender_bid)
    test_deleted_bid_is_not_restorable = snitch(deleted_bid_is_not_restorable)
    test_deleted_bid_do_not_locks_tender_in_state = snitch(deleted_bid_do_not_locks_tender_in_state)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_invalidate_not_agreement_member_bid_via_chronograph = snitch(
        invalidate_not_agreement_member_bid_via_chronograph
    )
    test_bids_related_product = snitch(bids_related_product)


@patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_profile",
    Mock(return_value=test_tender_pq_short_profile),
)
@patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_tender_category",
    Mock(return_value=test_tender_pq_category),
)
class TenderBidCriteriaTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = criteria_drop_uuids(deepcopy(test_tender_pq_criteria_1))

    test_multiple_criterias = snitch(requirement_response_validation_multiple_criterias)
    test_expected_values_format = snitch(requirement_response_value_validation_for_expected_values)


class TenderBidCriteriaGroupTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = criteria_drop_uuids(deepcopy(test_tender_pq_criteria_2))

    test_multiple_groups = snitch(requirement_response_validation_multiple_groups)


class TenderBidCriteriaMultipleGroupTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = criteria_drop_uuids(deepcopy(test_tender_pq_criteria_3))

    test_multiple_groups_multiple_requirements = snitch(
        requirement_response_validation_multiple_groups_multiple_requirements
    )


class TenderBidCriteriaOneGroupMultipleRequirementsTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = criteria_drop_uuids(deepcopy(test_tender_pq_criteria_4))

    test_multiple_groups_multiple_requirements = snitch(requirement_response_validation_one_group_multiple_requirements)


class TenderBidDocumentResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = test_tender_pq_criteria

    def setUp(self):
        super().setUp()
        # Create bid
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {
                "data": {
                    "tenderers": [test_tender_pq_organization],
                    "value": {"amount": 500},
                    "requirementResponses": test_tender_pq_requirement_response,
                }
            },
        )
        bid = response.json["data"]
        self.bid = bid
        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]

    test_not_found = snitch(not_found)
    test_patch_tender_bid_document = snitch(patch_tender_bid_document)

    test_create_tender_bid_document_json = snitch(create_tender_bid_document_json)
    test_create_tender_bid_document_json_bulk = snitch(create_tender_bid_document_json_bulk)
    test_put_tender_bid_document_json = snitch(put_tender_bid_document_json)


class TenderBidBatchDocumentResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = test_tender_pq_criteria

    bid_data_wo_docs = {
        "tenderers": [test_tender_pq_organization],
        "value": {"amount": 500},
        "documents": [],
        "requirementResponses": test_tender_pq_requirement_response,
    }

    test_create_tender_bid_with_document_invalid = snitch(create_tender_bid_with_document_invalid)
    test_create_tender_bid_with_document = snitch(create_tender_bid_with_document)
    test_create_tender_bid_with_documents = snitch(create_tender_bid_with_documents)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidBatchDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
