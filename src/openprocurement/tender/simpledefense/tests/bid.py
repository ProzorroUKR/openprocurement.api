# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_author, test_organization, test_lots
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    # TenderBidDocumentResourceTest
    not_found,
    # TenderBidderBatchDocumentWithDSResourceTest
    create_tender_bid_with_documents,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
    # Tender2LotBidResourceTest
    patch_tender_with_bids_lots_none,
)
from openprocurement.tender.openua.tests.bid import (
    TenderBidResourceTestMixin,
    TenderBidDocumentResourceTestMixin,
    TenderBidRequirementResponseTestMixin,
    TenderBidRequirementResponseEvidenceTestMixin,
)
from openprocurement.tender.openua.tests.bid_blanks import (
    # TenderBidFeaturesResourceTest
    features_bidder,
    features_bidder_invalid,
    # TenderBidDocumentWithDSResourceTest
    create_tender_bidder_document_json,
    put_tender_bidder_document_json,
    tender_bidder_confidential_document,
)
from openprocurement.tender.simpledefense.tests.base import (
    BaseSimpleDefContentWebTest,
    test_features_tender_ua_data,
    test_bids,
)


class CreateBidMixin(object):
    base_bid_status = "draft"

    def setUp(self):
        super(CreateBidMixin, self).setUp()
        bid_data = deepcopy(test_bids[0])
        bid_data["status"] = self.base_bid_status

        # Create bid
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )
        bid = response.json["data"]
        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]


class TenderBidResourceTest(BaseSimpleDefContentWebTest, TenderBidResourceTestMixin):
    initial_status = "active.tendering"
    test_bids_data = test_bids  # TODO: change attribute identifier
    author_data = test_author


class Tender2LotBidResourceTest(BaseSimpleDefContentWebTest):
    test_bids_data = test_bids
    initial_lots = 2 * test_lots
    initial_status = "active.tendering"

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)


class TenderBidFeaturesResourceTest(BaseSimpleDefContentWebTest):
    initial_data = test_features_tender_ua_data
    initial_status = "active.tendering"
    test_bids_data = test_bids

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderBidDocumentResourceTest(BaseSimpleDefContentWebTest, TenderBidDocumentResourceTestMixin):
    initial_status = "active.tendering"
    test_bids_data = test_bids
    author_data = test_author

    def setUp(self):
        super(TenderBidDocumentResourceTest, self).setUp()

        bid_data = deepcopy(self.test_bids_data[0])
        bid_data["value"] = {"amount": 500}
        # Create bid
        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )
        bid = response.json["data"]
        self.bid_id = bid["id"]
        self.bid_token = response.json["access"]["token"]

    test_not_found = snitch(not_found)

    def test_create_tender_bidder_document_nopending(self):
        bid_data = deepcopy(self.test_bids_data[0])
        bid_data["value"] = {"amount": 500}

        response = self.app.post_json(
            "/tenders/{}/bids".format(self.tender_id),
            {"data": bid_data},
        )
        bid = response.json["data"]
        bid_id = bid["id"]
        bid_token = response.json["access"]["token"]

        response = self.app.post(
            "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, bid_token),
            upload_files=[("file", "name.doc", b"content")],
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        doc_id = response.json["data"]["id"]
        self.assertIn(doc_id, response.headers["Location"])

        self.set_status("active.qualification")

        response = self.app.patch_json(
            "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, bid_token),
            {"data": {"description": "document description"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document because award of bid is not in pending or active state",
        )

        response = self.app.put(
            "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, bid_token),
            "content3",
            content_type="application/msword",
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document because award of bid is not in pending or active state",
        )

        response = self.app.post(
            "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, bid_token),
            upload_files=[("file", "name.doc", b"content")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't add document because award of bid is not in pending or active state",
        )


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True
    test_bids_data = test_bids

    test_create_tender_bidder_document_json = snitch(create_tender_bidder_document_json)
    test_put_tender_bidder_document_json = snitch(put_tender_bidder_document_json)
    test_tender_bidder_confidential_document = snitch(tender_bidder_confidential_document)


class TenderBidderBatchDocumentsWithDSResourceTest(BaseSimpleDefContentWebTest):
    docservice = True
    initial_status = "active.tendering"
    test_bids_data = test_bids
    bid_data_wo_docs = {
        "tenderers": [test_organization],
        "value": {"amount": 500},
        "selfEligible": True,
        "selfQualified": True,
        "documents": [],
    }

    create_tender_bid_with_document_invalid = snitch(create_tender_bid_with_document_invalid)
    create_tender_bid_with_document = snitch(create_tender_bid_with_document)
    create_tender_bid_with_documents = snitch(create_tender_bid_with_documents)


class TenderBidRequirementResponseResourceTest(
    TenderBidRequirementResponseTestMixin,
    CreateBidMixin,
    BaseSimpleDefContentWebTest,
):
    test_bids_data = test_bids
    initial_status = "active.tendering"


class TenderBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseSimpleDefContentWebTest,
):
    test_bids_data = test_bids
    initial_status = "active.tendering"
    tender_auth = ("Basic", ("token", ""))
    guarantee_criterion = False


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderBidDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidRequirementResponseResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidRequirementResponseEvidenceResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
