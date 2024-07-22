import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.auction import (
    TenderMultipleLotAuctionResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.auction_blanks import (
    get_tender_lots_auction_features,
    patch_tender_lots_auction,
    post_tender_lots_auction_features,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_features_data,
    test_tender_below_lots,
)
from openprocurement.tender.open.tests.base import (
    BaseTenderUAContentWebTest,
    test_tender_open_bids,
    test_tender_open_features_data,
)

# class TenderAuctionResourceTest(BaseTenderUAContentWebTest, TenderAuctionResourceTestMixin):
# #     initial_status = "active.tendering"
#     initial_bids = test_bids


# class TenderSameValueAuctionResourceTest(BaseTenderUAContentWebTest):
# #     initial_status = "active.auction"
#     initial_bids = [
#         test_bids[0]
#         for i in range(3)
#     ]
#
#     test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
#     test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderMultipleLotAuctionResourceTest(TenderMultipleLotAuctionResourceTestMixin, BaseTenderUAContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_open_bids
    initial_lots = 2 * test_tender_below_lots

    test_patch_tender_auction = snitch(patch_tender_lots_auction)


# class TenderFeaturesAuctionResourceTest(BaseTenderUAContentWebTest):
# #     initial_data = test_features_tender_ua_data
#     initial_status = "active.tendering"
#
#     test_get_tender_auction = snitch(get_tender_auction_feature)
#     test_post_tender_auction = snitch(post_tender_auction_feature)
#
#     def setUp(self):
#         self.initial_bids = deepcopy(test_bids[:2])
#         self.initial_bids[0]["parameters"] = [{"code": i["code"], "value": 0.1} for i in test_features_tender_data["features"]]
#         self.initial_bids[1]["parameters"] = [{"code": i["code"], "value": 0.15} for i in test_features_tender_data["features"]]
#         super(TenderFeaturesAuctionResourceTest, self).setUp()


class TenderFeaturesMultilotAuctionResourceTest(
    TenderMultipleLotAuctionResourceTestMixin,
    BaseTenderUAContentWebTest,
):
    initial_data = test_tender_open_features_data
    initial_status = "active.tendering"
    initial_lots = test_tender_below_lots * 2

    test_get_tender_auction = snitch(get_tender_lots_auction_features)
    test_post_tender_auction = snitch(post_tender_lots_auction_features)

    def setUp(self):
        self.initial_bids = deepcopy(test_tender_open_bids[:2])
        self.initial_bids[0]["parameters"] = [
            {"code": i["code"], "value": 0.1} for i in test_tender_below_features_data["features"]
        ]
        self.initial_bids[1]["parameters"] = [
            {"code": i["code"], "value": 0.15} for i in test_tender_below_features_data["features"]
        ]
        super().setUp()


def suite():
    suite = unittest.TestSuite()
    # suite.addTest(unittest.makeSuite(TenderAuctionResourceTest))
    # suite.addTest(unittest.makeSuite(TenderSameValueAuctionResourceTest))
    # suite.addTest(unittest.makeSuite(TenderFeaturesAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderMultipleLotAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderFeaturesMultilotAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
