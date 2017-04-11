# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_features_tender_data,
    test_lots,
    test_organization
)

from openprocurement.tender.openua.tests.base import test_bids

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_data,
    test_features_tender_ua_data
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


class TenderAuctionResourceTest(BaseTenderUAContentWebTest):
    initial_status = 'active.tendering'
    initial_bids = test_bids

    test_status_that_denies_get_post_patch_auction = 'active.tendering'
    test_status_that_denies_get_post_patch_auction_document = 'active.tendering'

    test_get_tender_auction_not_found = snitch(get_tender_auction_not_found)

    test_get_tender_auction = snitch(get_tender_auction)

    test_post_tender_auction = snitch(post_tender_auction)

    test_patch_tender_auction = snitch(patch_tender_auction)

    test_post_tender_auction_document = snitch(post_tender_auction_document)


class TenderSameValueAuctionResourceTest(BaseTenderUAContentWebTest):
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
            },
            'selfEligible': True,
            'selfQualified': True,
        }
        for i in range(3)
    ]

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)

    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderLotAuctionResourceTest(TenderAuctionResourceTest):
    initial_lots = test_lots
    initial_data = test_tender_data

    test_get_tender_auction = snitch(get_tender_lot_auction)

    test_post_tender_auction = snitch(post_tender_lot_auction)

    test_patch_tender_auction = snitch(patch_tender_lot_auction)

    test_post_tender_auction_document = snitch(post_tender_lot_auction_document)


class TenderMultipleLotAuctionResourceTest(TenderAuctionResourceTest):
    initial_lots = 2 * test_lots

    test_get_tender_auction = snitch(get_tender_lots_auction)

    test_post_tender_auction = snitch(post_tender_lots_auction)

    test_patch_tender_auction = snitch(patch_tender_lots_auction)

    test_post_tender_auction_document = snitch(post_tender_lots_auction_document)


class TenderFeaturesAuctionResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_features_tender_ua_data
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
            },
            'selfEligible': True,
            'selfQualified': True,
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
            },
            'selfEligible': True,
            'selfQualified': True,
        }
    ]

    test_get_tender_auction = snitch(get_tender_auction_feature)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSameValueAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderFeaturesAuctionResourceTest))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
