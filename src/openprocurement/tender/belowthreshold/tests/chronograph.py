import unittest

from openprocurement.api.tests.base import snitch

from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest,
    test_tender_below_lots,
    test_tender_below_bids,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.chronograph_blanks import (
    switch_to_tendering_by_tender_period_start_date,
    switch_to_qualification,
    switch_to_qualification_one_bid,
    switch_to_auction,
    switch_to_auction_lot_items,
    switch_to_unsuccessful,
    set_auction_period,
    reset_auction_period,
    set_auction_period_lot_separately,
    switch_to_auction_with_non_auction_lot,
    switch_to_ignored_on_complete,
    switch_from_pending_to_ignored,
    switch_from_pending,
    switch_to_complaint,
    award_switch_to_ignored_on_complete,
    award_switch_from_pending_to_ignored,
    award_switch_from_pending,
    award_switch_to_complaint,
)
from openprocurement.tender.core.tests.utils import change_auth


class TenderSwitchTenderingResourceTest(TenderContentWebTest):
    initial_status = "active.enquires"
    test_switch_to_tendering_by_tenderPeriod_startDate = snitch(switch_to_tendering_by_tender_period_start_date)


class TenderSwitchQualificationResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_below_bids[:1]

    test_switch_to_qualification = snitch(switch_to_qualification)


class TenderSwitchQualificationOneBidResourceTest(TenderContentWebTest):
    initial_status = "active.enquires"
    test_switch_to_qualification = snitch(switch_to_qualification_one_bid)


class TenderSwitchAuctionResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"
    initial_bids = test_tender_below_bids

    test_switch_to_auction = snitch(switch_to_auction)


class TenderSwitchUnsuccessfulResourceTest(TenderContentWebTest):
    initial_status = "active.tendering"

    test_switch_to_unsuccessful = snitch(switch_to_unsuccessful)


class TenderLotSwitchQualificationResourceTest(TenderSwitchQualificationResourceTest):
    initial_lots = test_tender_below_lots


class TenderLotSwitchAuctionResourceTest(TenderSwitchAuctionResourceTest):
    initial_lots = test_tender_below_lots


class TenderLotItemsSwitchAuctionResourceTest(TenderContentWebTest):
    initial_status = "active.enquiries"
    initial_lots = test_tender_below_lots
    initial_bids = test_tender_below_bids
    test_switch_to_auction_lot_items = snitch(switch_to_auction_lot_items)


class TenderLotSwitchUnsuccessfulResourceTest(TenderSwitchUnsuccessfulResourceTest):
    initial_lots = test_tender_below_lots


class TenderAuctionPeriodResourceTest(TenderContentWebTest):
    initial_bids = test_tender_below_bids

    test_set_auction_period = snitch(set_auction_period)
    test_reset_auction_period = snitch(reset_auction_period)


class TenderLotAuctionPeriodResourceTest(TenderAuctionPeriodResourceTest):
    initial_lots = test_tender_below_lots


class TenderLotsAuctionPeriodResourceTest(TenderContentWebTest):
    initial_bids = test_tender_below_bids
    initial_lots = test_tender_below_lots * 2
    test_set_auction_period_lot_separately = snitch(set_auction_period_lot_separately)


class TenderUnsuccessfulLotAuctionPeriodResourceTest(TenderAuctionPeriodResourceTest):
    initial_lots = test_tender_below_lots * 2
    initial_status = "active.tendering"

    def setUp(self):
        super(TenderUnsuccessfulLotAuctionPeriodResourceTest, self).setUp()
        # Create award with an unsuccessful lot
        for bid in self.initial_bids:
            bid_id = bid["id"]
            lot_values = bid["lotValues"][:1]
            del lot_values[0]["date"]
            response = self.app.patch_json(
                f"/tenders/{self.tender_id}/bids/{bid['id']}?acc_token={self.initial_bids_tokens[bid_id]}",
                {"data": {"lotValues": bid["lotValues"][:1]}}
            )
            self.assertEqual(response.status, "200 OK")


class TenderLotNoAuctionResourceTest(TenderContentWebTest):
    initial_lots = test_tender_below_lots * 2
    initial_bids = test_tender_below_bids
    initial_status = "active.tendering"

    def setUp(self):
        super().setUp()
        # 2 lots: with 2 bids and with only one
        bid = self.initial_bids[0]
        bid_id = bid["id"]
        lot_values = bid["lotValues"][:1]
        del lot_values[0]["date"]
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/bids/{bid['id']}?acc_token={self.initial_bids_tokens[bid_id]}",
            {"data": {"lotValues": bid["lotValues"][:1]}}
        )
        self.assertEqual(response.status, "200 OK")

    test_switch_to_auction_with_non_auction_lot = snitch(switch_to_auction_with_non_auction_lot)


class TenderComplaintSwitchResourceTest(TenderContentWebTest):
    initial_status = "active.enquiries"
    test_switch_to_ignored_on_complete = snitch(switch_to_ignored_on_complete)
    test_switch_from_pending_to_ignored = snitch(switch_from_pending_to_ignored)
    test_switch_from_pending = snitch(switch_from_pending)
    test_switch_to_complaint = snitch(switch_to_complaint)


class TenderLotComplaintSwitchResourceTest(TenderComplaintSwitchResourceTest):
    initial_lots = test_tender_below_lots


class TenderAwardComplaintSwitchResourceTest(TenderContentWebTest):
    initial_status = "active.qualification"
    initial_bids = test_tender_below_bids

    def setUp(self):
        super(TenderAwardComplaintSwitchResourceTest, self).setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {"data": {"suppliers": [test_tender_below_organization], "status": "pending", "bid_id": self.initial_bids[0]["id"]}},
            )
            award = response.json["data"]
            self.award_id = award["id"]

        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "active")

    test_award_switch_to_ignored_on_complete = snitch(award_switch_to_ignored_on_complete)
    test_award_switch_from_pending_to_ignored = snitch(award_switch_from_pending_to_ignored)
    test_award_switch_from_pending = snitch(award_switch_from_pending)
    test_award_switch_to_complaint = snitch(award_switch_to_complaint)


class TenderLotAwardComplaintSwitchResourceTest(TenderAwardComplaintSwitchResourceTest):
    initial_lots = test_tender_below_lots

    def setUp(self):
        super(TenderAwardComplaintSwitchResourceTest, self).setUp()
        # Create award
        with change_auth(self.app, ("Basic", ("token", ""))):
            response = self.app.post_json(
                "/tenders/{}/awards".format(self.tender_id),
                {
                    "data": {
                        "suppliers": [test_tender_below_organization],
                        "status": "pending",
                        "bid_id": self.initial_bids[0]["id"],
                        "lotID": self.initial_bids[0]["lotValues"][0]["relatedLot"],
                    }
                },
            )
            award = response.json["data"]
            self.award_id = award["id"]

        response = self.app.patch_json(
            "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "active")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TenderAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotAwardComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotComplaintSwitchResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderLotSwitchUnsuccessfulResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchAuctionResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchQualificationResourceTest))
    suite.addTest(unittest.makeSuite(TenderSwitchUnsuccessfulResourceTest))
    return suite


if __name__ == "__main__":
    unittest.main(defaultTest="suite")
