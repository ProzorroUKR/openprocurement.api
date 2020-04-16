# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.pricequotation.tests.base import (
    TenderContentWebTest,
    test_organization,
    test_bids,
    test_requirement_response,
)
from openprocurement.tender.pricequotation.tests.bid_blanks import (
    # TenderBidResourceTest
    create_tender_bid_invalid,
    create_tender_bid,
    patch_tender_bid,
    get_tender_bid,
    delete_tender_bid,
    get_tender_tenderers,
    bid_Administrator_change,
    create_tender_bid_no_scale_invalid,
    create_tender_bid_with_scale_not_required,
    create_tender_bid_no_scale,
    # TenderBidDocumentResourceTest
    not_found,
    create_tender_bid_document,
    put_tender_bid_document,
    patch_tender_bid_document,
    create_tender_bid_document_nopending,
    # TenderBidDocumentWithDSResourceTest
    create_tender_bid_document_json,
    put_tender_bid_document_json,
    # TenderBidBatchDocumentWithDSResourceTest
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
    create_tender_bid_with_documents,
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
    test_create_tender_bid_no_scale_invalid = snitch(create_tender_bid_no_scale_invalid)
    test_create_tender_bid_with_scale_not_required = snitch(create_tender_bid_with_scale_not_required)
    test_create_tender_bid_no_scale = snitch(create_tender_bid_no_scale)


class TenderBidDocumentResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"

    def setUp(self):
        super(TenderBidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": {"tenderers": [test_organization], "value": {"amount": 500}, "requirementResponses": [test_requirement_response]}},
        )
        bid = response.json["data"]
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


class TenderBidBatchDocumentWithDSResourceTest(TenderContentWebTest):
    docservice = True
    initial_status = "active.tendering"
    bid_data_wo_docs = {"tenderers": [test_organization], "value": {"amount": 500}, "documents": [], "requirementResponses": [test_requirement_response]}

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
