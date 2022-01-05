from openprocurement.tender.core.utils import get_now
from datetime import timedelta


# TenderLotAuctionPeriodStartDateResourceTest
def tender_lot_put_auction_period_for_not_allowed_tender_status(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    lot_id = self.initial_lots[0]["id"]
    new_start = (get_now() + timedelta(days=self.days_till_auction_starts + 1)).isoformat()
    response = self.app.put_json(f"/tenders/{self.tender_id}/lots/{lot_id}/auctionPeriod",
        {"data": {"startDate": new_start}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Can't update auctionPeriod in current (draft) tender status")


def tender_lot_put_auction_period_in_active_tendering(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    lot_id = self.initial_lots[0]["id"]
    new_start = (get_now() + timedelta(days=self.days_till_auction_starts + 1)).isoformat()
    start_date = (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
    self.set_status("active.tendering", {"lots": [
        {"auctionPeriod": {"startDate": start_date}}
        for i in self.initial_lots
    ]})
    response = self.app.put_json(
                f"/tenders/{self.tender_id}/lots/{lot_id}/auctionPeriod",
                {"data": {"startDate": new_start}},
                status=200
            )
    self.assertIn(new_start, response.json['startDate'])


def tender_lot_put_auction_period_success_in_active_auction_status(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    lot_id = self.initial_lots[0]["id"]
    self.set_status("active.auction")
    new_start = (get_now() + timedelta(days=self.days_till_auction_starts + 1)).isoformat()
    response = self.app.put_json(
        f"/tenders/{self.tender_id}/lots/{lot_id}/auctionPeriod",
        {"data": {"startDate": new_start}},
        status=200
    )
    self.assertIn(new_start, response.json['startDate'])


def tender_collection_put_auction_period(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    self.initial_lots[0]["id"]
    new_start = (get_now() + timedelta(days=self.days_till_auction_starts + 1)).isoformat()
    self.set_status("active.auction")
    response = self.app.put_json(
        f"/tenders/{self.tender_id}/auctionPeriod",
        {"data": {"startDate": new_start}},
        status=200
    )
    self.assertIn(new_start, response.json['startDate'])
