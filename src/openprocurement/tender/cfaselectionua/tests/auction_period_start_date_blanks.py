from freezegun import freeze_time
from openprocurement.tender.core.utils import get_now
from datetime import timedelta


# TenderLotAuctionPeriodStartDateResourceTest
def tender_lot_put_auction_period_for_not_allowed_tender_status(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    lot_id = self.initial_lots[0]["id"]
    response = self.app.put_json(f"/tenders/{self.tender_id}/lots/{lot_id}/auctionPeriod",
        {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Can't update auctionPeriod in current (draft) tender status")


def tender_lot_put_auction_period_in_active_tendering(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    lot_id = self.initial_lots[0]["id"]
    with freeze_time("2021-12-23"):
        start_date = (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
        self.set_status("active.tendering", {"lots": [
            {"auctionPeriod": {"startDate": start_date}}
            for i in self.initial_lots
        ]})
    response = self.app.put_json(
                f"/tenders/{self.tender_id}/lots/{lot_id}/auctionPeriod",
                {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}},
                status=200
            )
    self.assertEqual({'startDate': '2022-01-25T14:06:17.298024+02:00'}, response.json)



def tender_lot_put_auction_period_success_in_active_auction_status(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    lot_id = self.initial_lots[0]["id"]
    self.set_status("active.auction")
    response = self.app.put_json(
        f"/tenders/{self.tender_id}/lots/{lot_id}/auctionPeriod",
        {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}},
        status=200
    )
    self.assertEqual({'startDate': '2022-01-25T14:06:17.298024+02:00'}, response.json)


def tender_collection_put_auction_period(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    lot_id = self.initial_lots[0]["id"]
    self.set_status("active.auction")
    response = self.app.put_json(
        f"/tenders/{self.tender_id}/auctionPeriod",
        {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}},
        status=200
    )
    self.assertEqual({'startDate': '2022-01-25T14:06:17.298024+02:00'}, response.json)
