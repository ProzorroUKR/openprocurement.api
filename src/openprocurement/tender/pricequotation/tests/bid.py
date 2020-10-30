# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest,
    test_organization,
    test_bids,
    test_requirement_response_valid,
)
from openprocurement.tender.pricequotation.tests.data import (
    test_criteria_1,
    test_criteria_2,
    test_criteria_3,
    test_criteria_4
    )
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
    create_tender_bid_with_documents,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
    create_tender_bid_with_documents,
    create_tender_bid_document_json,
    put_tender_bid_document_json,
    not_found,
    create_tender_bid_document,
    put_tender_bid_document,
    create_tender_bid_contract_data_document_json
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


class TenderBidResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"

    test_create_tender_bid_invalid = snitch(create_tender_bid_invalid)
    test_create_tender_bid = snitch(create_tender_bid)
    test_patch_tender_bid = snitch(patch_tender_bid)
    test_get_tender_bid = snitch(get_tender_bid)
    test_delete_tender_bid = snitch(delete_tender_bid)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bid_Administrator_change = snitch(bid_Administrator_change)


class TenderBidCriteriaTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = test_criteria_1

    test_multiple_criterias = snitch(
        requirement_response_validation_multiple_criterias
    )


class TenderBidCriteriaGroupTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = test_criteria_2

    test_multiple_groups = snitch(
        requirement_response_validation_multiple_groups
    )


class TenderBidCriteriaMultipleGroupTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = test_criteria_3

    test_multiple_groups_multiple_requirements = snitch(
        requirement_response_validation_multiple_groups_multiple_requirements
    )


class TenderBidCriteriaOneGroupMultipleRequirementsTest(TenderContentWebTest):
    initial_status = "active.tendering"
    test_criteria = test_criteria_4

    test_multiple_groups_multiple_requirements = snitch(
        requirement_response_validation_one_group_multiple_requirements
    )


class TenderBidDocumentResourceTest(TenderContentWebTest):

    initial_status = "active.tendering"

    def setUp(self):
        super(TenderBidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": {"tenderers": [test_organization], "value": {"amount": 500},
                      "requirementResponses": test_requirement_response_valid}},
        )
        bid = response.json["data"]
        self.bid = bid
        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]

    test_not_found = snitch(not_found)
    test_create_tender_bid_document = snitch(create_tender_bid_document)
    test_put_tender_bid_document = snitch(put_tender_bid_document)
    test_patch_tender_bid_document = snitch(patch_tender_bid_document)
    test_create_tender_bid_document_nopending = snitch(create_tender_bid_document_nopending)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True

    test_create_tender_bid_document_json = snitch(create_tender_bid_document_json)
    test_put_tender_bid_document_json = snitch(put_tender_bid_document_json)
    test_create_tender_bid_contract_data_document_json = snitch(create_tender_bid_contract_data_document_json)


class TenderBidBatchDocumentWithDSResourceTest(TenderContentWebTest):
    docservice = True
    initial_status = "active.tendering"
    bid_data_wo_docs = {"tenderers": [test_organization], "value": {"amount": 500}, "documents": [], "requirementResponses": test_requirement_response_valid}

    test_create_tender_bid_with_document_invalid = snitch(create_tender_bid_with_document_invalid)
    test_create_tender_bid_with_document = snitch(create_tender_bid_with_document)
    test_create_tender_bid_with_documents = snitch(create_tender_bid_with_documents)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderBidDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
