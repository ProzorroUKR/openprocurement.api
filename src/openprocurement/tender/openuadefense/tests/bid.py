# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_author, test_organization, test_lots
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    # TenderBidderBatchDocumentWithDSResourceTest
    create_tender_bid_with_documents,
    create_tender_bid_with_document_invalid,
    create_tender_bid_with_document,
    # Tender2LotBidResourceTest
    patch_tender_with_bids_lots_none,
)


from openprocurement.tender.openua.tests.bid import TenderBidResourceTestMixin, TenderBidDocumentWithDSResourceTestMixin
from openprocurement.tender.openua.tests.bid_blanks import (
    # TenderBidFeaturesResourceTest
    features_bidder,
    features_bidder_invalid,
)

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_features_tender_ua_data,
    test_bids,
)


class TenderBidResourceTest(BaseTenderUAContentWebTest, TenderBidResourceTestMixin):
    initial_status = "active.tendering"
    test_bids_data = test_bids  # TODO: change attribute identifier
    author_data = test_author


class Tender2LotBidResourceTest(BaseTenderUAContentWebTest):
    test_bids_data = test_bids
    initial_lots = 2 * test_lots
    initial_status = "active.tendering"

    test_patch_tender_with_bids_lots_none = snitch(patch_tender_with_bids_lots_none)


class TenderBidFeaturesResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_features_tender_ua_data
    initial_status = "active.tendering"
    test_bids_data = test_bids

    test_features_bidder = snitch(features_bidder)
    # TODO: uncomment when bid activation will be removed
    # test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentWithDSResourceTestMixin):
    test_bids_data = test_bids


class TenderBidderBatchDocumentsWithDSResourceTest(BaseTenderUAContentWebTest):
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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderBidderBatchDocumentsWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
