# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.bid_blanks import (
    # TenderStage2UABidDocumentResourceTest
    not_found as not_found_ua,
)

from openprocurement.tender.openua.tests.bid import (
    TenderBidDocumentResourceTestMixin as TenderUABidDocumentResourceTestMixin,
)
from openprocurement.tender.openua.tests.bid_blanks import (
    # TenderStage2UABidResourceTest
    patch_tender_bidder as patch_tender_bidder_ua,
    get_tender_bidder as get_tender_bidder_ua,
    delete_tender_bidder as delete_tender_bidder_ua,
    deleted_bid_do_not_locks_tender_in_state as deleted_bid_do_not_locks_tender_in_state_ua,
    get_tender_tenderers as get_tender_tenderers_ua,
    bid_Administrator_change as bid_Administrator_change_ua,
    draft1_bid as one_draft_bid,
    draft2_bids as two_draft_bids,
)

from openprocurement.tender.openeu.tests.bid import (
    TenderBidResourceTestMixin,
    Tender2BidResourceTestMixin,
    TenderBidDocumentResourceTestMixin,
)

from openprocurement.tender.competitivedialogue.tests.base import (
    BaseCompetitiveDialogEUStage2ContentWebTest,
    BaseCompetitiveDialogUAStage2ContentWebTest,
    test_bids,
    test_shortlistedFirms,
    test_tender_stage2_data_eu,
    test_tender_stage2_data_ua
)
from openprocurement.tender.competitivedialogue.tests.stage2.bid_blanks import (
    # TenderStage2BidResourceTest
    deleted_bid_is_not_restorable,
    # TenderStage2BidFeaturesResourceTest
    features_bidder_invalid,
    # TenderStage2EUBidResourceTest
    create_tender_bidder_firm,
    delete_tender_bidder_eu,
    bids_invalidation_on_tender_change_eu,
    ukrainian_author_id,
    # TenderStage2EUBidFeaturesResourceTest
    features_bidder_eu,
    # TenderStage2EUBidDocumentResourceTest
    create_tender_bidder_document_nopending_eu,
    # TenderStage2UABidResourceTest
    create_tender_biddder_invalid_ua,
    create_tender_bidder_ua,
    bids_invalidation_on_tender_change_ua,
    bids_activation_on_tender_documents_ua,
    # TenderStage2UABidFeaturesResourceTest
    features_bidder_ua,
    # TenderStage2UABidDocumentResourceTest
    put_tender_bidder_document_ua,
)

author = deepcopy(test_bids[0]["tenderers"][0])
author['identifier']['id'] = test_shortlistedFirms[0]['identifier']['id']
author['identifier']['scheme'] = test_shortlistedFirms[0]['identifier']['scheme']


class TenderStage2EUBidResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest,
                                    TenderBidResourceTestMixin,
                                    Tender2BidResourceTestMixin):

    initial_status = 'active.tendering'
    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_stage2_data_eu
    author_data = author
    test_bids_data = test_bids

    test_create_tender_bidder_firm = snitch(create_tender_bidder_firm)
    test_delete_tender_bidder = snitch(delete_tender_bidder_eu)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change_eu)
    test_ukrainian_author_id = snitch(ukrainian_author_id)


class TenderStage2EUBidFeaturesResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest):
    initial_status = 'active.tendering'
    initial_auth = ('Basic', ('broker', ''))
    initial_data = test_tender_stage2_data_eu
    author_data = author
    test_bids_data = test_bids

    def setUp(self):
        self.app.authorization = ('Basic', ('broker', ''))

    test_features_bidder = snitch(features_bidder_eu)
    test_features_bidder_invalid = snitch(features_bidder_invalid)


class TenderStage2EUBidDocumentResourceTest(BaseCompetitiveDialogEUStage2ContentWebTest, TenderBidDocumentResourceTestMixin):
    initial_auth = ('Basic', ('broker', ''))
    initial_status = 'active.tendering'
    author_data = author
    test_bids_data = test_bids

    def setUp(self):
        super(TenderStage2EUBidDocumentResourceTest, self).setUp()
        # Create bid
        test_bid_1 = deepcopy(test_bids[0])
        test_bid_1['tenderers'] = [author]
        test_bid_2 = deepcopy(test_bids[1])
        test_bid_2['tenderers'] = [author]
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': test_bid_1})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']
        # create second bid
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id), {'data': test_bid_2})
        bid2 = response.json['data']
        self.bid2_id = bid2['id']
        self.bid2_token = response.json['access']['token']

    test_create_tender_bidder_document_nopending = snitch(create_tender_bidder_document_nopending_eu)


class TenderStage2UABidResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):
    initial_status = 'active.tendering'
    initial_data = test_tender_stage2_data_ua
    author_data = author
    test_bids_data = test_bids

    test_create_tender_biddder_invalid = snitch(create_tender_biddder_invalid_ua)
    test_create_tender_bidder = snitch(create_tender_bidder_ua)
    test_patch_tender_bidder = snitch(patch_tender_bidder_ua)
    test_get_tender_bidder = snitch(get_tender_bidder_ua)
    test_delete_tender_bidder = snitch(delete_tender_bidder_ua)
    test_deleted_bid_is_not_restorable = snitch(deleted_bid_is_not_restorable)
    test_deleted_bid_do_not_locks_tender_in_state = snitch(deleted_bid_do_not_locks_tender_in_state_ua)
    test_get_tender_tenderers = snitch(get_tender_tenderers_ua)
    test_bid_Administrator_change = snitch(bid_Administrator_change_ua)
    test_1_draft_bid = snitch(one_draft_bid)
    test_2_draft_bids = snitch(two_draft_bids)
    test_bids_invalidation_on_tender_change = snitch(bids_invalidation_on_tender_change_ua)
    test_bids_activation_on_tender_documents = snitch(bids_activation_on_tender_documents_ua)


class TenderStage2UABidFeaturesResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest):

    initial_status = 'active.tendering'
    initial_data = test_tender_stage2_data_ua
    author_data = author
    test_bids_data = test_bids

    def setUp(self):
        self.app.authorization = ('Basic', ('broker', ''))

    test_features_bidder_ua = snitch(features_bidder_ua)
    test_features_bidder_invalid_ua = snitch(features_bidder_invalid)


class TenderStage2UABidDocumentResourceTest(BaseCompetitiveDialogUAStage2ContentWebTest, TenderUABidDocumentResourceTestMixin):
    initial_status = 'active.tendering'
    author_data = author

    def setUp(self):
        super(TenderStage2UABidDocumentResourceTest, self).setUp()
        # Create bid
        response = self.app.post_json('/tenders/{}/bids'.format(self.tender_id),
                                      {'data': {'selfEligible': True, 'selfQualified': True,
                                       'tenderers': [author], "value": {"amount": 500}}})
        bid = response.json['data']
        self.bid_id = bid['id']
        self.bid_token = response.json['access']['token']

    test_not_found = snitch(not_found_ua)
    test_put_tender_bidder_document = snitch(put_tender_bidder_document_ua)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderStage2EUBidDocumentResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUBidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2EUBidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UABidResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UABidFeaturesResourceTest))
    suite.addTest(unittest.makeSuite(TenderStage2UABidDocumentResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
