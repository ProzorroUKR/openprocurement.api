# -*- coding: utf-8 -*-
# TenderStage2EUSwitchUnsuccessfulResourceTest


def switch_to_unsuccessful_eu(self):
    self.set_status("active.pre-qualification", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


# TenderStage2UA2LotSwitch0BidResourceTest


def set_auction_period_2_lot_0_bid_ua(self):
    start_date = "9999-01-01T00:00:00+00:00"
    data = {"data": {"lots": [{"auctionPeriod": {"startDate": start_date}} for i in self.lots]}}
    response = self.check_chronograph(data)
    self.assertEqual(response.json["data"]["lots"][0]["auctionPeriod"]["startDate"], start_date)

