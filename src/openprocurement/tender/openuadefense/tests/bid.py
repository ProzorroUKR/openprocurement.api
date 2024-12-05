import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_lots,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    create_tender_bid_with_document,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_documents,
)
from openprocurement.tender.core.tests.utils import set_bid_lotvalues
from openprocurement.tender.openua.tests.bid import (
    TenderBidDocumentResourceTestMixin,
    TenderBidResourceTestMixin,
)
from openprocurement.tender.openua.tests.bid_blanks import (
    features_bidder,
    patch_tender_with_bids_lots_none,
)
from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_openuadefense_bids,
    test_tender_openuadefense_features_data,
)


class TenderBidResourceTest(BaseTenderUAContentWebTest, TenderBidResourceTestMixin):
    initial_status = "active.tendering"
    test_bids_data = test_tender_openuadefense_bids  # TODO: change attribute identifier
    author_data = test_tender_below_author
    initial_lots = test_tender_below_lots

    def setUp(self):
        super().setUp()
        response = self.app.get(f"/tenders/{self.tender_id}")
        self.tender_lots = response.json["data"]["lots"]
        self.test_bids_data = []
        for bid in test_tender_openuadefense_bids:
            bid_data = deepcopy(bid)
            set_bid_lotvalues(bid_data, self.tender_lots)
            self.test_bids_data.append(bid_data)


class Tender2LotBidResourceTest(BaseTenderUAContentWebTest):
    test_bids_data = test_tender_openuadefense_bids
    initial_lots = 2 * test_tender_below_lots
    initial_status = "active.tendering"

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)


class TenderBidFeaturesResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_openuadefense_features_data
    initial_status = "active.tendering"
    test_bids_data = test_tender_openuadefense_bids

    test_features_bidder = snitch(features_bidder)
    # TODO: uncomment when bid activation will be removed
    # test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderBidDocumentResourceTest(TenderBidDocumentResourceTestMixin):
    test_bids_data = test_tender_openuadefense_bids


class TenderBidderBatchDocumentsResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.tendering"
    test_bids_data = test_tender_openuadefense_bids
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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidDocumentResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidderBatchDocumentsResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderBidResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
