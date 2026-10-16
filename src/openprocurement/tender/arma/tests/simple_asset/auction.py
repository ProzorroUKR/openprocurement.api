import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch
from openprocurement.tender.arma.tests.complex_asset.auction_blanks import (
    get_tender_auction,
    post_tender_auction,
    post_tender_auction_not_changed,
    post_tender_auction_reversed,
)
from openprocurement.tender.arma.tests.simple_asset.base import (
    BaseTenderSimpleAssetContentWebTest,
    test_tender_arma_simple_bids,
    test_tender_arma_simple_lots,
)
from openprocurement.tender.esco.tests.auction_blanks import patch_tender_auction
from openprocurement.tender.open.tests.below_threshold.auction import (
    TenderAuctionResourceTestMixin,
)
from openprocurement.tender.open.tests.below_threshold.base import test_tender_below_supplier


class TenderAuctionResourceTest(BaseTenderSimpleAssetContentWebTest, TenderAuctionResourceTestMixin):
    initial_status = "active.tendering"
    initial_auth = ("Basic", ("broker", ""))
    initial_bids = test_tender_arma_simple_bids
    initial_lots = test_lots_data = test_tender_arma_simple_lots

    test_get_tender_auction = snitch(get_tender_auction)
    test_post_tender_auction = snitch(post_tender_auction)
    test_patch_tender_auction = snitch(patch_tender_auction)


class TenderSameValueAuctionResourceTest(BaseTenderSimpleAssetContentWebTest):
    initial_status = "active.auction"
    tenderer_info = deepcopy(test_tender_below_supplier)
    initial_bids = test_bids_data = [test_tender_arma_simple_bids[0] for i in range(3)]
    initial_lots = test_tender_arma_simple_lots

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderAuctionResourceTest))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TenderSameValueAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
