# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.auction_blanks import (
    get_tender_lot_auction_features,
    post_tender_lot_auction_features,
    get_tender_auction_not_found,
    get_tender_lot_auction,
    patch_tender_lot_auction,
    post_tender_lot_auction_document,
)


from openprocurement.tender.cfaua.tests.base import (
    BaseTenderContentWebTest,
    test_features_tender_data,
    test_features_bids,
    test_features_bids_same_amount,
    test_bids,
)
from openprocurement.tender.cfaua.tests.auction_blanks import (
    post_tender_1lot_auction_not_changed,
    post_tender_1lot_auction_reversed,
    post_tender_auction_all_awards_pending,
    post_tender_lot_auction,
    tender_go_to_awarded_with_one_lot,
)


class AuctionViewTests(BaseTenderContentWebTest):
    initial_bids = test_bids
    initial_status = "active.pre-qualification.stand-still"

    test_get_tender_auction_not_found = snitch(get_tender_auction_not_found)
    test_get_tender_lot_auction = snitch(get_tender_lot_auction)
    test_post_tender_lot_auction = snitch(post_tender_lot_auction)
    test_patch_tender_lot_auction = snitch(patch_tender_lot_auction)
    test_post_tender_lot_auction_document = snitch(post_tender_lot_auction_document)
    test_tender_go_to_awarded_with_one_lot = snitch(tender_go_to_awarded_with_one_lot)


class AuctionWithBidsOverMaxAwardsTests(BaseTenderContentWebTest):
    """Testing auction with bids over max awards"""

    initial_bids = test_bids + deepcopy(test_bids)
    initial_status = "active.pre-qualification.stand-still"

    test_post_tender_auction_all_awards_pending = snitch(post_tender_auction_all_awards_pending)


class AuctionFeaturesOnPreQualificationStandStillTests(BaseTenderContentWebTest):
    initial_status = "active.pre-qualification.stand-still"
    initial_data = test_features_tender_data
    initial_bids = test_features_bids

    test_get_tender_lot_auction_features = snitch(get_tender_lot_auction_features)
    test_post_tender_lot_auction_features = snitch(post_tender_lot_auction_features)


class AuctionFeaturesOnActiveAuctionTests(BaseTenderContentWebTest):
    initial_status = "active.auction"
    initial_data = test_features_tender_data
    initial_bids = test_features_bids_same_amount

    test_post_tender_1lot_auction_not_changed = snitch(post_tender_1lot_auction_not_changed)
    test_post_tender_1lot_auction_reversed = snitch(post_tender_1lot_auction_reversed)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(AuctionFeaturesOnActiveAuctionTests)
    suite.addTest(AuctionFeaturesOnPreQualificationStandStillTests)
    suite.addTest(AuctionViewTests)
    suite.addTest(AuctionWithBidsOverMaxAwardsTests)
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
