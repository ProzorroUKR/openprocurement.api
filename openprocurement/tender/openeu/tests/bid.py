# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch
from openprocurement.tender.openeu.tests.base import (
    BaseTenderContentWebTest,
    test_features_tender_data,
    test_bids
)

from openprocurement.tender.openeu.tests.bid_blanks import (
    # TenderBidDocumentWithDSResourceTest
    patch_tender_bidder_document_private_json,
    put_tender_bidder_document_private_json,
    get_tender_bidder_document_ds,
    # TenderBidDocumentResourceTest
    not_found,
    get_tender_bidder_document,
    create_tender_bidder_document,
    put_tender_bidder_document,
    patch_tender_bidder_document,
    patch_tender_bidder_document_private,
    patch_and_put_document_into_invalid_bid,
    download_tender_bidder_document,
    create_tender_bidder_document_nopending,
    # TenderBidFeaturesResourceTest
    features_bidder,
    features_bidder_invalid,
    # TenderBidResourceTest
    create_tender_biddder_invalid,
    create_tender_bidder,
    patch_tender_bidder,
    get_tender_bidder,
    delete_tender_bidder,
    deleted_bid_is_not_restorable,
    deleted_bid_do_not_locks_tender_in_state,
    get_tender_tenderers,
    bid_Administrator_change,
    bids_invalidation_on_tender_change,
    bids_activation_on_tender_documents,
)


class TenderBidResourceTest(BaseTenderContentWebTest):
    initial_status = 'active.tendering'
    initial_auth = ('Basic', ('broker', ''))
    test_bids = test_bids

    test_create_tender_biddder_invalid = snitch(create_tender_biddder_invalid)
    test_create_tender_bidder = snitch(create_tender_bidder)
    test_patch_tender_bidder = snitch(patch_tender_bidder)
    test_get_tender_bidder = snitch(get_tender_bidder)
    test_delete_tender_bidder = snitch(delete_tender_bidder)
    test_deleted_bid_is_not_restorable = snitch(deleted_bid_is_not_restorable)
    test_deleted_bid_do_not_locks_tender_in_state = snitch(deleted_bid_do_not_locks_tender_in_state)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bid_Administrator_change = snitch(bid_Administrator_change)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents)


class TenderBidFeaturesResourceTest(BaseTenderContentWebTest):
    initial_data = test_features_tender_data
    initial_status = 'active.tendering'
    initial_auth = ('Basic', ('broker', ''))
    test_bids = test_bids

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderBidDocumentResourceTest(BaseTenderContentWebTest):
    initial_auth = ('Basic', ('broker', ''))
    initial_status = 'active.tendering'
    test_bids = test_bids

    def setUp(self):
        super(TenderBidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': test_bids[0]})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']
        # create second bid
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': test_bids[1]})
        bid2 = response.json['data']
        self.bid2_id = bid2['id']
        self.bid2_token = response.json['access']['token']

    test_not_found = snitch(not_found)
    test_get_tender_bidder_document = snitch(get_tender_bidder_document)
    test_create_tender_bidder_document = snitch(create_tender_bidder_document)
    test_put_tender_bidder_document = snitch(put_tender_bidder_document)
    test_patch_tender_bidder_document = snitch(patch_tender_bidder_document)
    test_patch_tender_bidder_document_private = snitch(patch_tender_bidder_document_private)
    test_patch_and_put_document_into_invalid_bid = snitch(patch_and_put_document_into_invalid_bid)
    test_download_tender_bidder_document = snitch(download_tender_bidder_document)
    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True

    test_patch_tender_bidder_document_private_json = snitch(patch_tender_bidder_document_private_json)
    test_put_tender_bidder_document_private_json = snitch(put_tender_bidder_document_private_json)
    test_get_tender_bidder_document_ds = snitch(get_tender_bidder_document_ds)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderBidDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
