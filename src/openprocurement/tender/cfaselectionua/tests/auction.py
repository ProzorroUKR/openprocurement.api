import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.cfaselectionua.tests.auction_blanks import (  # TenderAuctionResourceTest; TenderSameValueAuctionResourceTest; TenderLotAuctionResourceTest; TenderMultipleLotAuctionResourceTest; TenderFeaturesAuctionResourceTest; TenderFeaturesLotAuctionResourceTest; TenderFeaturesMultilotAuctionResourceTest
    get_tender_auction,
    get_tender_auction_not_found,
    get_tender_lot_auction,
    get_tender_lot_auction_features,
    get_tender_lots_auction,
    get_tender_lots_auction_features,
    patch_tender_auction,
    patch_tender_lot_auction,
    patch_tender_lots_auction,
    post_tender_auction,
    post_tender_auction_document,
    post_tender_lot_auction,
    post_tender_lot_auction_document,
    post_tender_lot_auction_features,
    post_tender_lots_auction,
    post_tender_lots_auction_document,
    post_tender_lots_auction_features,
)
from openprocurement.tender.cfaselectionua.tests.base import (
    TenderContentWebTest,
    test_tender_cfaselectionua_agreement_features,
    test_tender_cfaselectionua_bids,
    test_tender_cfaselectionua_data,
    test_tender_cfaselectionua_lots,
    test_tender_cfaselectionua_organization,
)

skip_multi_lots = True
auction_test_tender_data = test_tender_cfaselectionua_data.copy()
auction_test_tender_data["submissionMethodDetails"] = "test submissionMethodDetails"


class TenderAuctionResourceTestMixin:
    test_get_tender_auction_not_found = snitch(get_tender_auction_not_found)
    test_get_tender_auction = snitch(get_tender_auction)
    test_post_tender_auction = snitch(post_tender_auction)
    test_patch_tender_auction = snitch(patch_tender_auction)
    test_post_tender_auction_document = snitch(post_tender_auction_document)


class TenderLotAuctionResourceTestMixin:
    test_get_tender_auction = snitch(get_tender_lot_auction)
    test_post_tender_auction = snitch(post_tender_lot_auction)
    test_patch_tender_auction = snitch(patch_tender_lot_auction)
    test_post_tender_auction_document = snitch(post_tender_lot_auction_document)


class TenderMultipleLotAuctionResourceTestMixin:
    test_get_tender_auction = snitch(get_tender_lots_auction)
    test_post_tender_auction = snitch(post_tender_lots_auction)
    test_post_tender_auction_document = snitch(post_tender_lots_auction_document)


class TenderLotAuctionResourceTest(TenderContentWebTest, TenderLotAuctionResourceTestMixin):
    initial_lots = test_tender_cfaselectionua_lots
    initial_data = auction_test_tender_data
    initial_status = "active.tendering"
    initial_bids = deepcopy(test_tender_cfaselectionua_bids)
    initial_auth = ("Basic", ("broker", ""))

    def setUp(self):
        super().setUp()


@unittest.skipIf(skip_multi_lots, "Skip multi-lots tests")
class TenderMultipleLotAuctionResourceTest(TenderContentWebTest, TenderMultipleLotAuctionResourceTestMixin):
    initial_lots = 2 * test_tender_cfaselectionua_lots
    initial_data = auction_test_tender_data
    initial_status = "active.tendering"
    initial_bids = deepcopy(test_tender_cfaselectionua_bids)
    initial_auth = ("Basic", ("broker", ""))

    test_patch_tender_auction = snitch(patch_tender_lots_auction)


class TenderFeaturesAuctionResourceTest(TenderContentWebTest):
    initial_agreement = deepcopy(test_tender_cfaselectionua_agreement_features)
    initial_status = "active.tendering"
    initial_lots = deepcopy(test_tender_cfaselectionua_lots)
    initial_bids = [
        {
            "parameters": [
                {"code": i["code"], "value": 0.1} for i in test_tender_cfaselectionua_agreement_features["features"]
            ],
            "tenderers": [test_tender_cfaselectionua_organization],
            "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
        },
        {
            "parameters": [
                {"code": i["code"], "value": 0.15} for i in test_tender_cfaselectionua_agreement_features["features"]
            ],
            "tenderers": [test_tender_cfaselectionua_organization],
            "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True},
        },
    ]

    # test_get_tender_auction = snitch(get_tender_auction_feature)
    # test_post_tender_auction = snitch(post_tender_auction_feature)


class TenderFeaturesLotAuctionResourceTest(TenderLotAuctionResourceTestMixin, TenderFeaturesAuctionResourceTest):
    initial_lots = test_tender_cfaselectionua_lots
    test_get_tender_auction = snitch(get_tender_lot_auction_features)
    test_post_tender_auction = snitch(post_tender_lot_auction_features)


@unittest.skip("Skip multi-lots tests")
class TenderFeaturesMultilotAuctionResourceTest(
    TenderMultipleLotAuctionResourceTestMixin, TenderFeaturesAuctionResourceTest
):
    initial_lots = test_tender_cfaselectionua_lots * 2
    test_get_tender_auction = snitch(get_tender_lots_auction_features)
    test_post_tender_auction = snitch(post_tender_lots_auction_features)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderFeaturesLotAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderFeaturesMultilotAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
