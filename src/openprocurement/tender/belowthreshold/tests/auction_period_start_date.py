from freezegun import freeze_time
from openprocurement.api.tests.base import snitch
from openprocurement.tender.belowthreshold.tests.base import (
    TenderContentWebTest, test_lots
)
from openprocurement.tender.core.utils import get_now
from datetime import timedelta


class TestPutAuctionStartDate(TenderContentWebTest):
    days_till_auction_starts = 10

    @freeze_time("2021-12-23")
    def tender_put_auction_period(self):
        response = self.app.put_json(f"/tenders/{self.tender_id}/auctionPeriod", status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["name"], "permission")

        self.app.authorization = ("Basic", ("administrator", ""))
        response = self.app.put_json(f"/tenders/{self.tender_id}/auctionPeriod", status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json["errors"][0]["description"],
                         "Can't update auctionPeriod in current (active.enquiries) tender status")

        self.set_status("active.tendering", {
            "auctionPeriod": {"startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()}})
        response = self.app.put_json(
            f"/tenders/{self.tender_id}/auctionPeriod",
            {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}},
            status=200
        )
        self.assertEqual(response.json, {'startDate': '2022-01-25T14:06:17.298024+02:00'})

        self.set_status("active.auction")
        response = self.app.put_json(
            f"/tenders/{self.tender_id}/auctionPeriod",
            {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}},
            status=200
        )
        self.assertEqual(response.json, {'startDate': '2022-01-25T14:06:17.298024+02:00'})

    test_tender_put_auction_period = snitch(tender_put_auction_period)


class TestPutAuctionStartDateForLotId(TenderContentWebTest):
    initial_lots = test_lots
    days_till_auction_starts = 10

    @freeze_time("2021-12-23")
    def tender_lot_put_auction_period(self):
        self.app.authorization = ("Basic", ("administrator", ""))
        lot_id = self.initial_lots[0]["id"]

        response = self.app.put_json(f"/tenders/{self.tender_id}/lots/{lot_id}/auctionPeriod",
            {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}}, status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json["errors"][0]["description"],
                         "Can't update auctionPeriod in current (active.enquiries) tender status")

        self.set_status("active.tendering", {"lots": [
            {"auctionPeriod": {"startDate": (get_now() + timedelta(days=self.days_till_auction_starts)).isoformat()}}
            for i in self.initial_lots]}, )
        response = self.app.put_json(
                    f"/tenders/{self.tender_id}/lots/{lot_id}/auctionPeriod",
                    {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}},
                    status=200
                )
        self.assertEqual({'startDate': '2022-01-25T14:06:17.298024+02:00'}, response.json)

        self.set_status("active.auction")
        response = self.app.put_json(
                    f"/tenders/{self.tender_id}/lots/{lot_id}/auctionPeriod",
                    {"data": {"startDate": '2022-01-25T14:06:17.298024+02:00'}},
                    status=200
                )
        self.assertEqual({'startDate': '2022-01-25T14:06:17.298024+02:00'}, response.json)

    test_tender_lot_put_auction_period = snitch(tender_lot_put_auction_period)
