import unittest
from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_organization,
    test_tender_below_lots,
)
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    create_tender_bid_with_documents,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
)


from openprocurement.tender.openua.tests.bid import TenderBidResourceTestMixin, TenderBidDocumentWithDSResourceTestMixin
from openprocurement.tender.openua.tests.bid_blanks import (
    features_bidder,
    patch_tender_with_bids_lots_none,
)

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_openuadefense_features_data,
    test_tender_openuadefense_bids,
)


class TenderBidResourceTest(BaseTenderUAContentWebTest, TenderBidResourceTestMixin):
    docservice = True
    initial_status = "active.tendering"
    test_bids_data = test_tender_openuadefense_bids  # TODO: change attribute identifier
    author_data = test_tender_below_author


class Tender2LotBidResourceTest(BaseTenderUAContentWebTest):
    docservice = True
    test_bids_data = test_tender_openuadefense_bids
    initial_lots = 2 * test_tender_below_lots
    initial_status = "active.tendering"

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)


class TenderBidFeaturesResourceTest(BaseTenderUAContentWebTest):
    docservice = True
    initial_data = test_tender_openuadefense_features_data
    initial_status = "active.tendering"
    test_bids_data = test_tender_openuadefense_bids

    test_features_bidder = snitch(features_bidder)
    # TODO: uncomment when bid activation will be removed
    # test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentWithDSResourceTestMixin):
    docservice = True
    test_bids_data = test_tender_openuadefense_bids


class TenderBidderBatchDocumentsWithDSResourceTest(BaseTenderUAContentWebTest):
    docservice = True
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
    suite.addTest(unittest.makeSuite(TenderBidderBatchDocumentsWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
