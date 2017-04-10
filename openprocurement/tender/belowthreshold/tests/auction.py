# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_tender_data,
    test_features_tender_data,
    test_bids,
    test_lots,
    test_organization
)
from openprocurement.tender.belowthreshold.tests.auction_blanks import (
    # TenderAuctionResourceTest
    get_tender_auction_not_found,
    get_tender_auction,
    post_tender_auction,
    patch_tender_auction,
    post_tender_auction_document,
    # TenderSameValueAuctionResourceTest
    post_tender_auction_not_changed,
    post_tender_auction_reversed,
    # TenderLotAuctionResourceTest
    get_tender_lot_auction,
    post_tender_lot_auction,
    patch_tender_lot_auction,
    post_tender_lot_auction_document,
    # TenderMultipleLotAuctionResourceTest
    get_tender_lots_auction,
    post_tender_lots_auction,
    patch_tender_lots_auction,
    post_tender_lots_auction_document,
    # TenderFeaturesAuctionResourceTest
    get_tender_auction_feature,
)


auction_test_tender_data = test_tender_data.copy()
auction_test_tender_data['submissionMethodDetails'] = 'test submissionMethodDetails'


class TenderAuctionResourceTest(TenderContentWebTest):
    initial_data = auction_test_tender_data
    initial_status = 'active.tendering'
    initial_bids = deepcopy(test_bids)
    initial_auth = ('Basic', ('broker', ''))
    test_status_that_denies_get_post_patch_auction = 'active.tendering'
    test_status_that_denies_get_post_patch_auction_document = 'active.tendering'

    test_get_tender_auction_not_found = snitch(get_tender_auction_not_found)
    test_get_tender_auction = snitch(get_tender_auction)
    test_post_tender_auction = snitch(post_tender_auction)
    test_patch_tender_auction = snitch(patch_tender_auction)
    test_post_tender_auction_document = snitch(post_tender_auction_document)


class TenderSameValueAuctionResourceTest(TenderContentWebTest):
    initial_status = 'active.auction'
    initial_bids = [
        {
            "tenderers": [
                test_organization
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            }
        }
        for i in range(3)
    ]

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderLotAuctionResourceTest(TenderContentWebTest):
    initial_lots = test_lots
    initial_data = auction_test_tender_data
    initial_status = 'active.tendering'
    initial_bids = deepcopy(test_bids)
    initial_auth = ('Basic', ('broker', ''))
    test_status_that_denies_get_post_patch_auction = 'active.tendering'
    test_status_that_denies_get_post_patch_auction_document = 'active.tendering'

    def setUp(self):
        super(TenderLotAuctionResourceTest, self).setUp()

    test_get_tender_lot_auction = snitch(get_tender_lot_auction)
    test_post_tender_lot_auction = snitch(post_tender_lot_auction)
    test_patch_tender_lot_auction = snitch(patch_tender_lot_auction)
    test_post_tender_lot_auction_document = snitch(post_tender_lot_auction_document)


class TenderMultipleLotAuctionResourceTest(TenderContentWebTest):
    initial_lots = 2 * test_lots
    initial_data = auction_test_tender_data
    initial_status = 'active.tendering'
    initial_bids = deepcopy(test_bids)
    initial_auth = ('Basic', ('broker', ''))
    test_status_that_denies_get_post_patch_auction = 'active.tendering'
    test_status_that_denies_get_post_patch_auction_document = 'active.tendering'

    test_get_tender_lots_auction = snitch(get_tender_lots_auction)
    test_post_tender_lots_auction = snitch(post_tender_lots_auction)
    test_patch_tender_lots_auction = snitch(patch_tender_lots_auction)
    test_post_tender_lots_auction_document = snitch(post_tender_lots_auction_document)


class TenderFeaturesAuctionResourceTest(TenderContentWebTest):
    initial_data = test_features_tender_data
    initial_status = 'active.auction'
    initial_bids = [
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.1,
                }
                for i in test_features_tender_data['features']
            ],
            "tenderers": [
                test_organization
            ],
            "value": {
                "amount": 469,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            }
        },
        {
            "parameters": [
                {
                    "code": i["code"],
                    "value": 0.15,
                }
                for i in test_features_tender_data['features']
            ],
            "tenderers": [
                test_organization
            ],
            "value": {
                "amount": 479,
                "currency": "UAH",
                "valueAddedTaxIncluded": True
            }
        }
    ]

    test_get_tender_auction_feature = snitch(get_tender_auction_feature)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSameValueAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderFeaturesAuctionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
