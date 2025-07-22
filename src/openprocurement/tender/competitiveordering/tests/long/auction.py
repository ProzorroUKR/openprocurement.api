import unittest
from copy import deepcopy

from openprocurement.api.context import set_request_now
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
from openprocurement.tender.competitiveordering.tests.long.base import (
    BaseTenderCOLongContentWebTest,
    test_tender_co_long_bids,
    test_tender_co_long_features_data,
)


class TenderMultipleLotAuctionResourceTest(TenderMultipleLotAuctionResourceTestMixin, BaseTenderCOLongContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_co_long_bids
    initial_lots = 2 * test_tender_below_lots

    test_patch_tender_auction = snitch(patch_tender_lots_auction)


class TenderFeaturesMultilotAuctionResourceTest(
    TenderMultipleLotAuctionResourceTestMixin,
    BaseTenderCOLongContentWebTest,
):
    initial_data = test_tender_co_long_features_data
    initial_status = "active.tendering"
    initial_lots = test_tender_below_lots * 2

    test_get_tender_auction = snitch(get_tender_lots_auction_features)
    test_post_tender_auction = snitch(post_tender_lots_auction_features)

    def setUp(self):
        set_request_now()

        self.initial_bids = deepcopy(test_tender_co_long_bids[:2])
        self.initial_bids[1]["tenderers"][0]["identifier"]["id"] = "00037257"

        identifier_0 = self.initial_bids[0]["tenderers"][0]["identifier"]["id"]
        parameters_0 = [{"code": i["code"], "value": 0.1} for i in test_tender_below_features_data["features"]]
        self.initial_bids[0]["parameters"] = parameters_0
        self.initial_agreement_data["contracts"][0]["parameters"] = parameters_0
        self.initial_agreement_data["contracts"][0]["suppliers"][0]["identifier"]["id"] = identifier_0

        identifier_1 = self.initial_bids[1]["tenderers"][0]["identifier"]["id"]
        parameters_1 = [{"code": i["code"], "value": 0.15} for i in test_tender_below_features_data["features"]]
        self.initial_bids[1]["parameters"] = parameters_1
        self.initial_agreement_data["contracts"][1]["parameters"] = parameters_1
        self.initial_agreement_data["contracts"][1]["suppliers"][0]["identifier"]["id"] = identifier_1

        super().setUp()


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderMultipleLotAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderFeaturesMultilotAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
