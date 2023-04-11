# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.cfaselectionua.tests.base import (
    TenderContentWebTest,
    test_tender_cfaselectionua_data,
    test_tender_cfaselectionua_agreement_features,
    test_tender_cfaselectionua_bids,
    test_tender_cfaselectionua_lots,
    test_tender_cfaselectionua_organization,
)
from openprocurement.tender.cfaselectionua.tests.auction_blanks import (
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
    post_tender_auction_feature,
    # TenderFeaturesLotAuctionResourceTest
    get_tender_lot_auction_features,
    post_tender_lot_auction_features,
    # TenderFeaturesMultilotAuctionResourceTest
    get_tender_lots_auction_features,
    post_tender_lots_auction_features,
)


skip_multi_lots = True
auction_test_tender_data = test_tender_cfaselectionua_data.copy()
auction_test_tender_data["submissionMethodDetails"] = "test submissionMethodDetails"


class TenderAuctionResourceTestMixin(object):
    test_get_tender_auction_not_found = snitch(get_tender_auction_not_found)
    test_get_tender_auction = snitch(get_tender_auction)
    test_post_tender_auction = snitch(post_tender_auction)
    test_patch_tender_auction = snitch(patch_tender_auction)
    test_post_tender_auction_document = snitch(post_tender_auction_document)


class TenderLotAuctionResourceTestMixin(object):
    test_get_tender_auction = snitch(get_tender_lot_auction)
    test_post_tender_auction = snitch(post_tender_lot_auction)
    test_patch_tender_auction = snitch(patch_tender_lot_auction)
    test_post_tender_auction_document = snitch(post_tender_lot_auction_document)


class TenderMultipleLotAuctionResourceTestMixin(object):
    test_get_tender_auction = snitch(get_tender_lots_auction)
    test_post_tender_auction = snitch(post_tender_lots_auction)
    test_post_tender_auction_document = snitch(post_tender_lots_auction_document)


class TenderLotAuctionResourceTest(TenderContentWebTest, TenderLotAuctionResourceTestMixin):
    docservice = True
    initial_lots = test_tender_cfaselectionua_lots
    initial_data = auction_test_tender_data
    initial_status = "active.tendering"
    initial_bids = deepcopy(test_tender_cfaselectionua_bids)
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super(TenderLotAuctionResourceTest, self).setUp()


@unittest.skipIf(skip_multi_lots, "Skip multi-lots tests")
class TenderMultipleLotAuctionResourceTest(TenderContentWebTest, TenderMultipleLotAuctionResourceTestMixin):
    docservice = True
    initial_lots = 2 * test_tender_cfaselectionua_lots
    initial_data = auction_test_tender_data
    initial_status = "active.tendering"
    initial_bids = deepcopy(test_tender_cfaselectionua_bids)
    initial_auth = ("Basic", ("broker", ""))

    test_patch_tender_auction = snitch(patch_tender_lots_auction)


class TenderFeaturesAuctionResourceTest(TenderContentWebTest):
    docservice = True
    initial_agreement = deepcopy(test_tender_cfaselectionua_agreement_features)
    initial_status = "active.tendering"
    initial_lots = deepcopy(test_tender_cfaselectionua_lots)
    initial_bids = [
        {
            "parameters": [{"code": i["code"], "value": 0.1} for i in test_tender_cfaselectionua_agreement_features["features"]],
            "tenderers": [test_tender_cfaselectionua_organization],
            "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
        },
        {
            "parameters": [{"code": i["code"], "value": 0.15} for i in test_tender_cfaselectionua_agreement_features["features"]],
            "tenderers": [test_tender_cfaselectionua_organization],
            "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True},
        },
    ]

    # test_get_tender_auction = snitch(get_tender_auction_feature)
    # test_post_tender_auction = snitch(post_tender_auction_feature)


class TenderFeaturesLotAuctionResourceTest(TenderLotAuctionResourceTestMixin, TenderFeaturesAuctionResourceTest):
    docservice = True
    initial_lots = test_tender_cfaselectionua_lots
    test_get_tender_auction = snitch(get_tender_lot_auction_features)
    test_post_tender_auction = snitch(post_tender_lot_auction_features)


@unittest.skip("Skip multi-lots tests")
class TenderFeaturesMultilotAuctionResourceTest(
    TenderMultipleLotAuctionResourceTestMixin, TenderFeaturesAuctionResourceTest
):
    docservice = True
    initial_lots = test_tender_cfaselectionua_lots * 2
    test_get_tender_auction = snitch(get_tender_lots_auction_features)
    test_post_tender_auction = snitch(post_tender_lots_auction_features)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderFeaturesLotAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderFeaturesMultilotAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
