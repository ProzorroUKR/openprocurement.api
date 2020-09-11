# -*- coding: utf-8 -*-
import unittest
from copy import deepcopy

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.auction import (
    TenderAuctionResourceTestMixin,
    TenderLotAuctionResourceTestMixin,
    TenderMultipleLotAuctionResourceTestMixin,
)

from openprocurement.tender.openeu.tests.auction_blanks import (
    # TenderMultipleLotAuctionResourceTest
    patch_tender_2lot_auction,
)

from openprocurement.tender.esco.tests.base import (
    BaseESCOContentWebTest,
    test_features_tender_data,
    test_bids,
    test_lots,
)

from openprocurement.tender.esco.tests.auction_blanks import (
    # TenderAuctionResourceTest
    get_tender_auction,
    post_tender_auction,
    # TenderLotAuctionResourceTest
    get_tender_lot_auction,
    post_tender_lot_auction,
    # TenderMultipleLotAuctionResourceTest
    get_tender_lots_auction,
    post_tender_lots_auction,
    # TenderAuctionFieldsTest
    auction_check_NBUdiscountRate,
    auction_check_noticePublicationDate,
    # TenderFeaturesAuctionResourceTest
    get_tender_auction_feature,
    post_tender_auction_feature,
    # TenderFeaturesLotAuctionResourceTest
    get_tender_lot_auction_feature,
    post_tender_lot_auction_feature,
    # TenderFeaturesMultipleLotAuctionResourceTest,
    get_tender_lots_auction_feature,
    post_tender_lots_auction_feature,
    # TenderSameValueAuctionResourceTest
    post_tender_auction_not_changed,
    post_tender_auction_reversed,
)


def prepare_for_auction(self):
    """
    Qualify bids and switch to pre-qualification.stand-still (before auction status)
    """

    # switch to active.pre-qualification
    self.time_shift("active.pre-qualification")
    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    for qualific in response.json["data"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualific["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    # switch to active.pre-qualification.stand-still
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")


class TenderAuctionResourceTest(BaseESCOContentWebTest, TenderAuctionResourceTestMixin):
    # initial_data = tender_data
    initial_auth = ("Basic", ("broker", ""))
    initial_bids = test_bids
    initial_bids[1]["value"] = {
        "yearlyPaymentsPercentage": 0.9,
        "annualCostsReduction": [100] * 21,
        "contractDuration": {"years": 10, "days": 10},
    }

    def setUp(self):
        super(TenderAuctionResourceTest, self).setUp()
        prepare_for_auction(self)

    test_get_tender_auction = snitch(get_tender_auction)
    test_post_tender_auction = snitch(post_tender_auction)


class TenderSameValueAuctionResourceTest(BaseESCOContentWebTest):
    initial_status = "active.auction"
    tenderer_info = deepcopy(test_bids[0]["tenderers"])

    def setUp(self):
        bid_data = deepcopy(test_bids[0])
        bid_data["value"] = {
            "yearlyPaymentsPercentage": 0.9,
            "annualCostsReduction": [751.5] * 21,
            "contractDuration": {"years": 10, "days": 10},
        }
        self.initial_bids = [bid_data for i in range(3)]

        super(TenderSameValueAuctionResourceTest, self).setUp()
        # switch to active.pre-qualification
        self.set_status("active.pre-qualification", {"status": "active.tendering"})
        self.app.authorization = ("Basic", ("chronograph", ""))
        response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification")

        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
        for qualific in response.json["data"]:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}".format(self.tender_id, qualific["id"]),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

        # switch to active.pre-qualification.stand-still
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

        # switch to active.auction
        self.set_status("active.auction", {"status": "active.pre-qualification.stand-still"})
        self.app.authorization = ("Basic", ("chronograph", ""))
        response = self.app.patch_json("/tenders/{}".format(self.tender_id), {"data": {"id": self.tender_id}})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active.auction")
        # self.app.authorization = ('Basic', ('token', ''))

    test_post_tender_auction_not_changed = snitch(post_tender_auction_not_changed)
    test_post_tender_auction_reversed = snitch(post_tender_auction_reversed)


class TenderAuctionFieldsTest(BaseESCOContentWebTest):
    # initial_data = tender_data
    initial_auth = ("Basic", ("broker", ""))
    initial_bids = test_bids

    def setUp(self):
        super(TenderAuctionFieldsTest, self).setUp()
        prepare_for_auction(self)

    test_auction_check_NBUdiscountRate = snitch(auction_check_NBUdiscountRate)
    test_auction_check_noticePublicationDate = snitch(auction_check_noticePublicationDate)


class TenderLotAuctionResourceTest(TenderLotAuctionResourceTestMixin, TenderAuctionResourceTest):
    initial_lots = test_lots
    # initial_data = test_tender_data
    test_get_tender_auction = snitch(get_tender_lot_auction)
    test_post_tender_auction = snitch(post_tender_lot_auction)


class TenderMultipleLotAuctionResourceTest(TenderMultipleLotAuctionResourceTestMixin, TenderAuctionResourceTest):
    initial_lots = 2 * test_lots

    test_get_tender_auction = snitch(get_tender_lots_auction)
    test_patch_tender_auction = snitch(patch_tender_2lot_auction)
    test_post_tender_auction = snitch(post_tender_lots_auction)


class TenderFeaturesAuctionResourceTest(BaseESCOContentWebTest):
    initial_data = test_features_tender_data
    tenderer_info = deepcopy(test_bids[0]["tenderers"])

    def setUp(self):
        bid_data_1 = deepcopy(test_bids[0])
        bid_data_1["value"] = {
            "yearlyPaymentsPercentage": 0.9,
            "annualCostsReduction": [100] * 21,
            "contractDuration": {"years": 10},
        }
        bid_data_1["parameters"] = [{"code": i["code"], "value": 0.03} for i in test_features_tender_data["features"]]

        bid_data_2 = deepcopy(bid_data_1)
        bid_data_2["parameters"] = [{"code": i["code"], "value": 0.07} for i in test_features_tender_data["features"]]

        self.initial_bids = [bid_data_1, bid_data_2]
        super(TenderFeaturesAuctionResourceTest, self).setUp()
        prepare_for_auction(self)

    test_get_tender_auction = snitch(get_tender_auction_feature)
    test_post_tender_auction = snitch(post_tender_auction_feature)


class TenderFeaturesLotAuctionResourceTest(TenderLotAuctionResourceTestMixin, TenderFeaturesAuctionResourceTest):
    initial_data = test_features_tender_data
    initial_lots = test_lots

    test_get_tender_auction = snitch(get_tender_lot_auction_feature)
    test_post_tender_auction = snitch(post_tender_lot_auction_feature)


class TenderFeaturesMultipleLotAuctionResourceTest(
    TenderMultipleLotAuctionResourceTestMixin, TenderFeaturesAuctionResourceTest
):
    initial_data = test_features_tender_data
    initial_lots = 2 * test_lots

    test_get_tender_auction = snitch(get_tender_lots_auction_feature)
    test_post_tender_auction = snitch(post_tender_lots_auction_feature)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSameValueAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderAuctionFieldsTest))
    suite.addTest(unittest.makeSuite(TenderLotAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderMultipleLotAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderFeaturesAuctionResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
