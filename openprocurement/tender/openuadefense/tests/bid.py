# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import test_organization
from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    # TenderBidDocumentResourceTest
    not_found,
)

from openprocurement.tender.openua.tests.base import test_bids
from openprocurement.tender.openua.tests.bid_blanks import (
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
    # TenderBidFeaturesResourceTest
    features_bidder,
    features_bidder_invalid,
    # TenderBidDocumentResourceTest
    create_tender_bidder_document,
    put_tender_bidder_document,
    patch_tender_bidder_document,
    create_tender_bidder_document_nopending,
    # TenderBidDocumentWithDSResourceTest
    create_tender_bidder_document_json,
    put_tender_bidder_document_json,
)

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_features_tender_ua_data
)


class TenderBidResourceTest(BaseTenderUAContentWebTest):
    initial_status = 'active.tendering'
    test_bids_data = test_bids  # TODO: change attribute identifier

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


class TenderBidFeaturesResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_features_tender_ua_data
    initial_status = 'active.tendering'

    test_features_bidder = snitch(features_bidder)

    test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderBidDocumentResourceTest(BaseTenderUAContentWebTest):
    initial_status = 'active.tendering'

    def setUp(self):
        super(TenderBidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json('/tenders/{}/bids'.format(
            self.tender_id), {'data': {'tenderers': [test_organization], "value": {"amount": 500}, 'selfEligible': True, 'selfQualified': True}})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']

    test_not_found = snitch(not_found)

    test_create_tender_bidder_document = snitch(create_tender_bidder_document)

    test_put_tender_bidder_document = snitch(put_tender_bidder_document)

    test_patch_tender_bidder_document = snitch(patch_tender_bidder_document)

    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending)


class TenderBidDocumentWithDSResourceTest(TenderBidDocumentResourceTest):
    docservice = True

    test_create_tender_bidder_document_json = snitch(create_tender_bidder_document_json)

    test_put_tender_bidder_document_json = snitch(put_tender_bidder_document_json)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderBidDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidDocumentWithDSResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(TenderBidResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
