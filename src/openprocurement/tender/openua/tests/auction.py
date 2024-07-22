import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.auction import (
    TenderAuctionResourceTestMixin,
    TenderMultipleLotAuctionResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.auction_blanks import (  # TenderSameValueAuctionResourceTest; TenderMultipleLotAuctionResourceTest; TenderFeaturesAuctionResourceTest; TenderFeaturesMultilotAuctionResourceTest
    get_tender_auction_feature,
    get_tender_lots_auction_features,
    patch_tender_lots_auction,
    post_tender_auction_feature,
    post_tender_auction_not_changed,
    post_tender_auction_reversed,
    post_tender_lots_auction_features,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_features_data,
    test_tender_below_lots,
)
from openprocurement.tender.openua.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_openua_bids,
    test_tender_openua_features_data,
)


class TenderAuctionResourceTest(BaseTenderUAContentWebTest, TenderAuctionResourceTestMixin):
    initial_status = "active.tendering"
    initial_bids = test_tender_openua_bids
    initial_lots = test_tender_below_lots


class TenderSameValueAuctionResourceTest(BaseTenderUAContentWebTest):
    initial_status = "active.auction"
    initial_bids = [test_tender_openua_bids[0] for i in range(3)]
    initial_lots = test_tender_below_lots

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderMultipleLotAuctionResourceTest(TenderMultipleLotAuctionResourceTestMixin, TenderAuctionResourceTest):
    initial_lots = 2 * test_tender_below_lots

    test_patch_tender_auction = snitch(patch_tender_lots_auction)


class TenderFeaturesAuctionResourceTest(BaseTenderUAContentWebTest):
    initial_data = test_tender_openua_features_data
    initial_status = "active.tendering"

    test_get_tender_auction = snitch(get_tender_auction_feature)
    test_post_tender_auction = snitch(post_tender_auction_feature)

    def setUp(self):
        self.initial_bids = deepcopy(test_tender_openua_bids[:2])
        self.initial_bids[0]["parameters"] = [
            {"code": i["code"], "value": 0.1} for i in test_tender_below_features_data["features"]
        ]
        self.initial_bids[1]["parameters"] = [
            {"code": i["code"], "value": 0.15} for i in test_tender_below_features_data["features"]
        ]
        super().setUp()


class TenderFeaturesMultilotAuctionResourceTest(
    TenderMultipleLotAuctionResourceTestMixin, TenderFeaturesAuctionResourceTest
):
    initial_lots = test_tender_below_lots * 2

    test_get_tender_auction = snitch(get_tender_lots_auction_features)
    test_post_tender_auction = snitch(post_tender_lots_auction_features)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderSameValueAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderFeaturesAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderFeaturesMultilotAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
