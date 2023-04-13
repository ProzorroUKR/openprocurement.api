import unittest
from unittest.mock import patch
from copy import deepcopy
from datetime import timedelta
from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import snitch
from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest,
    test_tender_pq_organization,
    test_tender_pq_bids,
    test_tender_pq_requirement_response_valid,
    test_tender_pq_criteria,
    test_tender_pq_requirement_response,
)
from openprocurement.tender.pricequotation.tests.utils import (
    criteria_drop_uuids,
    copy_criteria_req_id,
)
from openprocurement.tender.pricequotation.tests.data import (
    test_tender_pq_criteria_1,
    test_tender_pq_criteria_2,
    test_tender_pq_criteria_3,
    test_tender_pq_criteria_4
    )
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
    create_tender_bid_with_documents,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
    create_tender_bid_with_documents,
    create_tender_bid_document_json,
    create_tender_bid_document_json_bulk,
    put_tender_bid_document_json,
    not_found,
)
from openprocurement.tender.pricequotation.tests.bid_blanks import (
    create_tender_bid,
    create_tender_bid_document_nopending,
    create_tender_bid_invalid,
    patch_tender_bid,
    get_tender_bid,
    delete_tender_bid,
    get_tender_tenderers,
    bid_Administrator_change,
    patch_tender_bid_document,
    requirement_response_validation_multiple_criterias,
    requirement_response_validation_multiple_groups,
    requirement_response_validation_multiple_groups_multiple_requirements,
    requirement_response_validation_one_group_multiple_requirements
)


@patch("openprocurement.tender.pricequotation.models.requirement.PQ_CRITERIA_ID_FROM", get_now() + timedelta(days=1))
class TenderBidResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = test_tender_pq_criteria

    test_create_tender_bid_invalid = snitch(create_tender_bid_invalid)
    test_create_tender_bid = snitch(create_tender_bid)
    test_patch_tender_bid = snitch(patch_tender_bid)
    test_get_tender_bid = snitch(get_tender_bid)
    test_delete_tender_bid = snitch(delete_tender_bid)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bid_Administrator_change = snitch(bid_Administrator_change)


class TenderBidCriteriaTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = criteria_drop_uuids(deepcopy(test_tender_pq_criteria_1))

    test_multiple_criterias = snitch(
        requirement_response_validation_multiple_criterias
    )


class TenderBidCriteriaGroupTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = criteria_drop_uuids(deepcopy(test_tender_pq_criteria_2))

    test_multiple_groups = snitch(
        requirement_response_validation_multiple_groups
    )


class TenderBidCriteriaMultipleGroupTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = criteria_drop_uuids(deepcopy(test_tender_pq_criteria_3))

    test_multiple_groups_multiple_requirements = snitch(
        requirement_response_validation_multiple_groups_multiple_requirements
    )


class TenderBidCriteriaOneGroupMultipleRequirementsTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = criteria_drop_uuids(deepcopy(test_tender_pq_criteria_4))

    test_multiple_groups_multiple_requirements = snitch(
        requirement_response_validation_one_group_multiple_requirements
    )


class TenderBidDocumentResourceTest(TenderContentWebTest):
    docservice = True
    initial_status = "active.tendering"
    test_criteria = test_tender_pq_criteria

    def setUp(self):
        super(TenderBidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": {"tenderers": [test_tender_pq_organization], "value": {"amount": 500},
                      "requirementResponses": test_tender_pq_requirement_response}},
        )
        bid = response.json["data"]
        self.bid = bid
        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]

    test_not_found = snitch(not_found)
    test_patch_tender_bid_document = snitch(patch_tender_bid_document)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True

    test_create_tender_bid_document_json = snitch(create_tender_bid_document_json)
    test_create_tender_bid_document_json_bulk = snitch(create_tender_bid_document_json_bulk)
    test_put_tender_bid_document_json = snitch(put_tender_bid_document_json)


class TenderBidBatchDocumentWithDSResourceTest(TenderContentWebTest):
    docservice = True
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
    suite.addTest(unittest.makeSuite(TenderBidDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
