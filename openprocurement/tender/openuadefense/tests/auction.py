# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_features_tender_data,
    test_lots,
    test_organization
)
from openprocurement.tender.belowthreshold.tests.auction import (
    TenderAuctionResourceTestMixin,
    TenderLotAuctionResourceTestMixin,
    TenderMultipleLotAuctionResourceTestMixin
)
from openprocurement.tender.belowthreshold.tests.auction_blanks import (
    # TenderSameValueAuctionResourceTest
    post_tender_auction_not_changed,
    post_tender_auction_reversed,
    # TenderMultipleLotAuctionResourceTest
    patch_tender_lots_auction,
    # TenderFeaturesAuctionResourceTest
    get_tender_auction_feature,
)

from openprocurement.tender.openua.tests.base import test_bids

from openprocurement.tender.openuadefense.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_data,
    test_features_tender_ua_data
)


class TenderAuctionResourceTest(BaseTenderUAContentWebTest, TenderAuctionResourceTestMixin):
    initial_status = 'active.tendering'
    initial_bids = test_bids

    test_status_that_denies_get_post_patch_auction = 'active.tendering'
    test_status_that_denies_get_post_patch_auction_document = 'active.tendering'


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


class TenderLotAuctionResourceTest(TenderLotAuctionResourceTestMixin, TenderAuctionResourceTest):
    initial_lots = test_lots
    initial_data = test_tender_data


class TenderMultipleLotAuctionResourceTest(TenderMultipleLotAuctionResourceTestMixin, TenderAuctionResourceTest):
    initial_lots = 2 * test_lots

    test_patch_tender_auction = snitch(patch_tender_lots_auction)


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
