from freezegun import freeze_time
from openprocurement.tender.core.utils import get_now
from datetime import timedelta


# TenderAuctionPeriodStartDateResourceTest
def tender_collection_put_auction_period_in_active_tendering(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    with freeze_time("2021-12-23"):
        start_date = (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
        self.set_status("active.tendering", {
            "auctionPeriod": {"startDate": start_date}})
    response = self.app.put_json(
        f"/tenders/{self.tender_id}/auctionPeriod",
        {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}},
        status=200
    )
    self.assertEqual(response.json, {'startDate': '2022-01-25T14:06:17.298024+02:00'})


def tender_collection_put_auction_period_in_active_auction(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    self.set_status("active.auction")
    response = self.app.put_json(
        f"/tenders/{self.tender_id}/auctionPeriod",
        {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}},
        status=200
    )
    self.assertEqual(response.json, {'startDate': '2022-01-25T14:06:17.298024+02:00'})


def tender_put_auction_period_permission_error(self):
    response = self.app.put_json(f"/tenders/{self.tender_id}/auctionPeriod", status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["name"], "permission")


def tender_collection_put_auction_period_for_not_allowed_tender_status(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    self.set_status("active.qualification")
    response = self.app.put_json(f"/tenders/{self.tender_id}/auctionPeriod", status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Can't update auctionPeriod in current (active.qualification) tender status")


# TenderLotAuctionPeriodStartDateResourceTest
def tender_lot_put_auction_period_for_not_allowed_tender_status(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    self.set_status("active.qualification")
    lot_id = self.initial_lots[0]["id"]
    response = self.app.put_json(f"/tenders/{self.tender_id}/lots/{lot_id}/auctionPeriod", status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Can't update auctionPeriod in current (active.qualification) tender status")


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


def tender_lot_put_auction_period_in_active_auction(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    self.set_status("active.auction")
    lot_id = self.initial_lots[0]["id"]
    response = self.app.put_json(
                f"/tenders/{self.tender_id}/lots/{lot_id}/auctionPeriod",
                {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}},
                status=200
            )
    self.assertEqual({'startDate': '2022-01-25T14:06:17.298024+02:00'},
                     response.json)


# TenderMultipleLotAuctionPeriodStartDateResourceTest
def tender_multe_lot_put_auction_period_for_not_allowed_tender_status(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    self.set_status("active.qualification")
    lot_id1 = self.initial_lots[0]["id"]
    response = self.app.put_json(f"/tenders/{self.tender_id}/lots/{lot_id1}/auctionPeriod",
        {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Can't update auctionPeriod in current (active.qualification) tender status")


def tender_multe_lot_put_auction_period_in_active_tendering(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    lot_id1 = self.initial_lots[0]["id"]
    with freeze_time("2021-12-23"):
        start_date = (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()
        self.set_status("active.tendering", {"lots": [
            {"auctionPeriod": {"startDate": start_date}}
            for i in self.initial_lots
        ]})
    response = self.app.put_json(
                f"/tenders/{self.tender_id}/lots/{lot_id1}/auctionPeriod",
                {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}},
                status=200
            )
    self.assertEqual({'startDate': '2022-01-25T14:06:17.298024+02:00'}, response.json)


def tender_multe_lot_put_auction_period_in_active_auction(self):
    self.app.authorization = ("Basic", ("administrator", ""))
    self.initial_lots[0]["id"]
    lot_id2 = self.initial_lots[1]["id"]
    self.set_status("active.auction")

    self.set_status("active.auction")
    response = self.app.put_json(
                f"/tenders/{self.tender_id}/lots/{lot_id2}/auctionPeriod",
                {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}},
                status=200
            )
    self.assertEqual({'startDate': '2022-01-25T14:06:17.298024+02:00'}, response.json)
