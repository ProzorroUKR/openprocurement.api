import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_lots,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.bid_blanks import (  # Tender2LotBidResourceTest
    create_tender_bid_with_document,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_documents,
    not_found,
    patch_tender_bid_with_exceeded_lot_values,
    post_tender_bid_with_exceeded_lot_values,
)
from openprocurement.tender.belowthreshold.tests.utils import set_bid_lotvalues
from openprocurement.tender.openua.tests.bid import (
    TenderBidDocumentWithDSResourceTestMixin,
    TenderBidRequirementResponseEvidenceTestMixin,
    TenderBidRequirementResponseTestMixin,
    TenderBidResourceTestMixin,
    patch_tender_with_bids_lots_none,
)
from openprocurement.tender.openua.tests.bid_blanks import features_bidder
from openprocurement.tender.simpledefense.tests.base import (
    BaseSimpleDefContentWebTest,
    test_tender_simpledefense_bids,
    test_tender_simpledefense_features_data,
)


class CreateBidMixin:
    base_bid_status = "draft"

    def setUp(self):
        super().setUp()
        bid_data = deepcopy(test_tender_simpledefense_bids[0])
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
    docservice = True
    initial_status = "active.tendering"
    test_bids_data = test_tender_simpledefense_bids  # TODO: change attribute identifier
    author_data = test_tender_below_author
    initial_lots = test_tender_below_lots

    def setUp(self):
        super().setUp()
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.tender_lots = response.json["data"]["lots"]
        self.test_bids_data = []
        for bid in test_tender_simpledefense_bids:
            bid_data = deepcopy(bid)
            set_bid_lotvalues(bid_data, self.tender_lots)
            self.test_bids_data.append(bid_data)


class Tender2LotBidResourceTest(BaseSimpleDefContentWebTest):
    test_bids_data = test_tender_simpledefense_bids
    initial_lots = 2 * test_tender_below_lots
    initial_status = "active.tendering"

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)
    test_post_tender_bid_with_exceeded_lot_values = snitch(post_tender_bid_with_exceeded_lot_values)
    test_patch_tender_bid_with_exceeded_lot_values = snitch(patch_tender_bid_with_exceeded_lot_values)


class TenderBidFeaturesResourceTest(BaseSimpleDefContentWebTest):
    initial_data = test_tender_simpledefense_features_data
    initial_status = "active.tendering"
    test_bids_data = test_tender_simpledefense_bids

    test_features_bidder = snitch(features_bidder)
    # TODO: uncomment when bid activation will be removed
    # test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderBidDocumentResourceTest(BaseSimpleDefContentWebTest, TenderBidDocumentWithDSResourceTestMixin):
    initial_status = "active.tendering"
    test_bids_data = test_tender_simpledefense_bids
    author_data = test_tender_below_author
    docservice = True

    def setUp(self):
        super().setUp()

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

        response = self.app.post_json(
            "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, bid_token),
            {
                "data": {
                    "title": "name_3.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
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
            "Can't update document because award of bid is not in one of statuses ('active',)",
        )

        response = self.app.put_json(
            "/tenders/{}/bids/{}/documents/{}?acc_token={}".format(self.tender_id, bid_id, doc_id, bid_token),
            {
                "data": {
                    "title": "name_3.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update document because award of bid is not in one of statuses ('active',)",
        )

        response = self.app.post_json(
            "/tenders/{}/bids/{}/documents?acc_token={}".format(self.tender_id, bid_id, bid_token),
            {
                "data": {
                    "title": "name_3.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't add document because award of bid is not in one of statuses ('active',)",
        )


class TenderBidderBatchDocumentsWithDSResourceTest(BaseSimpleDefContentWebTest):
    docservice = True
    initial_status = "active.tendering"
    test_bids_data = test_tender_simpledefense_bids
    bid_data_wo_docs = {
        "tenderers": [test_tender_below_organization],
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
    test_bids_data = test_tender_simpledefense_bids
    initial_status = "active.tendering"


class TenderBidRequirementResponseEvidenceResourceTest(
    TenderBidRequirementResponseEvidenceTestMixin,
    CreateBidMixin,
    BaseSimpleDefContentWebTest,
):
    test_bids_data = test_tender_simpledefense_bids
    initial_status = "active.tendering"
    guarantee_criterion = False


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidDocumentWithDSResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidRequirementResponseResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidRequirementResponseEvidenceResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
