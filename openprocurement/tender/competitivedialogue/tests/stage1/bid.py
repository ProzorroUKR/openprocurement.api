# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.openeu.tests.bid import TenderBidResourceTestMixin
from openprocurement.tender.openeu.tests.base import (
    test_bids
)

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUContentWebTest, test_features_tender_eu_data
)
from openprocurement.tender.competitivedialogue.tests.stage1.bid_blanks import (
    # CompetitiveDialogEUBidResourceTest
    create_tender_bidder_invalid,
    status_jumping,
    create_bid_without_parameters,
    patch_tender_bidder,
    get_tender_bidder,
    deleted_bid_do_not_locks_tender_in_state,
    get_tender_tenderers,
    bids_invalidation_on_tender_change,
    # CompetitiveDialogEUBidFeaturesResourceTest
    features_bidder,
    features_bidder_invalid,
    # CompetitiveDialogEUBidDocumentResourceTest
    get_tender_bidder_document,
    create_tender_bidder_document,
    put_tender_bidder_document,
    patch_tender_bidder_document,
    patch_tender_bidder_document_private,
    patch_and_put_document_into_invalid_bid,
    download_tender_bidder_document,
    create_tender_bidder_document_nopending,
    create_tender_bidder_document_description,
    create_tender_bidder_invalid_document_description,
    create_tender_bidder_invalid_confidential_document,
)

test_bids.append(test_bids[0].copy())  # Minimal number of bits is 3


class CompetitiveDialogEUBidResourceTest(BaseCompetitiveDialogEUContentWebTest, TenderBidResourceTestMixin):

    initial_status = 'active.tendering'
    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids
    author_data = test_bids_data[0]['tenderers'][0]

    test_create_tender_bidder_invalid = snitch(create_tender_bidder_invalid)
    test_status_jumping = snitch(status_jumping)
    test_create_bid_without_parameters = snitch(create_bid_without_parameters)
    test_patch_tender_bidder = snitch(patch_tender_bidder)
    test_get_tender_bidder = snitch(get_tender_bidder)
    test_deleted_bid_do_not_locks_tender_in_state = snitch(deleted_bid_do_not_locks_tender_in_state)
    test_get_tender_tenderers = snitch(get_tender_tenderers)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change)


class CompetitiveDialogEUBidFeaturesResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_data = test_features_tender_eu_data
    initial_status = 'active.tendering'
    initial_auth = ('Basic', ('broker', ''))
    test_bids_data = test_bids

    test_features_bidder = snitch(features_bidder)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


class CompetitiveDialogEUBidDocumentResourceTest(BaseCompetitiveDialogEUContentWebTest):
    initial_auth = ('Basic', ('broker', ''))
    initial_status = 'active.tendering'
    test_bids_data = test_bids

    def setUp(self):
        super(CompetitiveDialogEUBidDocumentResourceTest, self).setUp()
        # Create bid
        bidder_data = deepcopy(test_bids[0])
        bidder_data['tenderers'][0]['identifier']['id'] = u"00037256"
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bidder_data})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']
        # create second bid
        bidder_data = deepcopy(test_bids[1])
        bidder_data['tenderers'][0]['identifier']['id'] = u"00037257"
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bidder_data})
        bid2 = response.json['data']
        self.bid2_id = bid2['id']
        self.bid2_token = response.json['access']['token']
        bidder_data = deepcopy(test_bids[1])
        bidder_data['tenderers'][0]['identifier']['id'] = u"00037258"
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': bidder_data})
        bid3 = response.json['data']
        self.bid3_id = bid3['id']
        self.bid3_token = response.json['access']['token']

    test_get_tender_bidder_document = snitch(get_tender_bidder_document)
    test_create_tender_bidder_document = snitch(create_tender_bidder_document)
    test_put_tender_bidder_document = snitch(put_tender_bidder_document)
    test_patch_tender_bidder_document = snitch(patch_tender_bidder_document)
    test_patch_tender_bidder_document_private = snitch(patch_tender_bidder_document_private)
    test_patch_and_put_document_into_invalid_bid = snitch(patch_and_put_document_into_invalid_bid)
    test_download_tender_bidder_document = snitch(download_tender_bidder_document)
    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending)
    test_create_tender_bidder_document_description = snitch(create_tender_bidder_document_description)
    test_create_tender_bidder_invalid_document_description = snitch(create_tender_bidder_invalid_document_description)
    test_create_tender_bidder_invalid_confidential_document = snitch(create_tender_bidder_invalid_confidential_document)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUBidResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(CompetitiveDialogEUBidDocumentResourceTest))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
