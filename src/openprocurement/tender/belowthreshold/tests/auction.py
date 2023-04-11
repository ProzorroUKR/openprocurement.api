# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_tender_below_data,
    test_tender_below_features_data,
    test_tender_below_bids,
    test_tender_below_lots,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.auction_blanks import (
    # TenderAuctionResourceTest
    get_tender_auction_not_found,
    get_tender_auction,
    post_tender_auction,
    post_tender_auction_weighted_value,
    patch_tender_auction,
    post_tender_auction_document,
    # TenderSameValueAuctionResourceTest
    post_tender_auction_not_changed,
    post_tender_auction_reversed,
    # TenderLotAuctionResourceTest
    get_tender_lot_auction,
    post_tender_lot_auction_weighted_value,
    post_tender_lot_auction_document,
    # TenderMultipleLotAuctionResourceTest
    get_tender_lots_auction,
    post_tender_lots_auction,
    post_tender_lots_auction_weighted_value,
    patch_tender_lots_auction,
    post_tender_lots_auction_document,
    # TenderFeaturesAuctionResourceTest
    get_tender_auction_feature,
    post_tender_auction_feature,
    # TenderFeaturesMultilotAuctionResourceTest
    get_tender_lots_auction_features,
    post_tender_lots_auction_features,
)


auction_test_tender_data = test_tender_below_data.copy()
auction_test_tender_data["submissionMethodDetails"] = "test submissionMethodDetails"


class TenderAuctionResourceTestMixin(object):
    test_get_tender_auction_not_found = snitch(get_tender_auction_not_found)
    test_get_tender_auction = snitch(get_tender_auction)
    test_post_tender_auction = snitch(post_tender_auction)
    test_post_tender_auction_weighted_value = snitch(post_tender_auction_weighted_value)
    test_patch_tender_auction = snitch(patch_tender_auction)
    test_post_tender_auction_document = snitch(post_tender_auction_document)


class TenderLotAuctionResourceTestMixin(object):
    test_get_tender_auction = snitch(get_tender_lot_auction)
    test_post_tender_auction_weighted_value = snitch(post_tender_lot_auction_weighted_value)
    test_post_tender_auction_document = snitch(post_tender_lot_auction_document)


class TenderMultipleLotAuctionResourceTestMixin(object):
    test_get_tender_auction = snitch(get_tender_lots_auction)
    test_post_tender_auction = snitch(post_tender_lots_auction)
    test_post_tender_auction_weighted_value = snitch(post_tender_lots_auction_weighted_value)
    test_post_tender_auction_document = snitch(post_tender_lots_auction_document)
    test_patch_tender_auction = snitch(patch_tender_lots_auction)


class TenderAuctionResourceTest(TenderContentWebTest, TenderAuctionResourceTestMixin):
    docservice = True
    initial_data = auction_test_tender_data
    initial_status = "active.tendering"
    initial_bids = deepcopy(test_tender_below_bids)
    initial_auth = ("Basic", ("broker", ""))


class TenderSameValueAuctionResourceTest(TenderContentWebTest):
    docservice = True
    initial_status = "active.auction"
    initial_bids = [
        {"tenderers": [test_tender_below_organization], "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True}}
        for i in range(3)
    ]

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderLotAuctionResourceTest(TenderContentWebTest, TenderLotAuctionResourceTestMixin):
    docservice = True
    initial_lots = test_tender_below_lots
    initial_data = auction_test_tender_data
    initial_status = "active.tendering"
    initial_bids = deepcopy(test_tender_below_bids)
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderLotAuctionResourceTest, self).setUp()


class TenderMultipleLotAuctionResourceTest(TenderContentWebTest, TenderMultipleLotAuctionResourceTestMixin):
    docservice = True
    initial_lots = 2 * test_tender_below_lots
    initial_data = auction_test_tender_data
    initial_status = "active.tendering"
    initial_bids = deepcopy(test_tender_below_bids)
    initial_auth = ("Basic", ("broker", ""))


class TenderFeaturesAuctionResourceTest(TenderContentWebTest):
    docservice = True
    initial_data = test_tender_below_features_data
    initial_status = "active.tendering"
    initial_bids = [
        {
            "parameters": [{"code": i["code"], "value": 0.1} for i in test_tender_below_features_data["features"]],
            "tenderers": [test_tender_below_organization],
            "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
        },
        {
            "parameters": [{"code": i["code"], "value": 0.15} for i in test_tender_below_features_data["features"]],
            "tenderers": [test_tender_below_organization],
            "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True},
        },
    ]

    test_get_tender_auction = snitch(get_tender_auction_feature)
    test_post_tender_auction = snitch(post_tender_auction_feature)


class TenderFeaturesMultilotAuctionResourceTest(
    TenderMultipleLotAuctionResourceTestMixin, TenderFeaturesAuctionResourceTest
):
    docservice = True
    initial_lots = test_tender_below_lots * 2
    test_get_tender_auction = snitch(get_tender_lots_auction_features)
    test_post_tender_auction = snitch(post_tender_lots_auction_features)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSameValueAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderFeaturesAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderFeaturesMultilotAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
