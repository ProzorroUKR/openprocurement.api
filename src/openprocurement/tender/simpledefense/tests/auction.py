# -*- coding: utf-8 -*-
import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_features_data,
    test_tender_below_lots,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.auction import (
    TenderAuctionResourceTestMixin,
    TenderMultipleLotAuctionResourceTestMixin,
)
from openprocurement.tender.belowthreshold.tests.auction_blanks import (
    # TenderSameValueAuctionResourceTest
    post_tender_auction_not_changed,
    post_tender_auction_reversed,
    # TenderMultipleLotAuctionResourceTest
    patch_tender_lots_auction,
    # TenderFeaturesAuctionResourceTest
    get_tender_auction_feature,
    post_tender_auction_feature,
    # TenderFeaturesMultilotAuctionResourceTest
    get_tender_lots_auction_features,
    post_tender_lots_auction_features,
)

from openprocurement.tender.simpledefense.tests.base import (
    BaseSimpleDefContentWebTest,
    test_tender_simpledefense_data,
    test_tender_simpledefense_bids,
    test_tender_simpledefense_features_data,
)


class TenderAuctionResourceTest(BaseSimpleDefContentWebTest, TenderAuctionResourceTestMixin):
    docservice = True
    initial_status = "active.tendering"
    initial_bids = test_tender_simpledefense_bids

    test_status_that_denies_get_post_patch_auction = "active.tendering"
    test_status_that_denies_get_post_patch_auction_document = "active.tendering"


class TenderSameValueAuctionResourceTest(BaseSimpleDefContentWebTest):
    initial_status = "active.auction"
    initial_bids = [
        {
            "tenderers": [test_tender_below_organization],
            "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
            "selfQualified": True,
        }
        for i in range(3)
    ]
    bid_update_data = {"selfEligible": True}

    for i in initial_bids:
        i.update(bid_update_data)

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)

    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderMultipleLotAuctionResourceTest(TenderMultipleLotAuctionResourceTestMixin, TenderAuctionResourceTest):
    initial_lots = 2 * test_tender_below_lots
    docservice = True
    test_patch_tender_auction = snitch(patch_tender_lots_auction)


class TenderFeaturesAuctionResourceTest(BaseSimpleDefContentWebTest):
    initial_data = test_tender_simpledefense_features_data
    initial_status = "active.tendering"
    initial_bids = [
        {
            "parameters": [{"code": i["code"], "value": 0.1} for i in test_tender_below_features_data["features"]],
            "tenderers": [test_tender_below_organization],
            "value": {"amount": 469, "currency": "UAH", "valueAddedTaxIncluded": True},
            "selfQualified": True,
        },
        {
            "parameters": [{"code": i["code"], "value": 0.15} for i in test_tender_below_features_data["features"]],
            "tenderers": [test_tender_below_organization],
            "value": {"amount": 479, "currency": "UAH", "valueAddedTaxIncluded": True},
            "selfQualified": True,
        },
    ]

    bid_update_data = {"selfEligible": True}

    for i in initial_bids:
        i.update(bid_update_data)

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
