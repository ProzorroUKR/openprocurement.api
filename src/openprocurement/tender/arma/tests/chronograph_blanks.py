# TenderSwitchPreQualificationResourceTest
import unittest
from datetime import timedelta

from openprocurement.api.constants import SANDBOX_MODE
from openprocurement.api.utils import get_now
from openprocurement.tender.core.utils import calculate_tender_full_date


def active_tendering_to_pre_qual(self):
    response = self.set_status("active.pre-qualification", {"status": "active.tendering"})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")


@unittest.skipIf(SANDBOX_MODE, "Skip test with accelerator")
def active_tendering_to_pre_qual_unsuccessful(self):
    response = self.set_status("active.pre-qualification", {"status": "active.tendering"})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")
    self.check_chronograph()

    auction_start_date = calculate_tender_full_date(
        get_now(),
        timedelta(days=30),
        tender=self.tender_document,
    ).isoformat()
    response = self.check_chronograph(
        data={"data": {"lots": [{"auctionPeriod": {"startDate": auction_start_date}}, {}, {}]}}
    )
    lots = response.json["data"]["lots"]
    self.assertEqual(lots[0]["auctionPeriod"]["startDate"], auction_start_date)
    self.assertNotIn("auctionPeriod", lots[1])
    self.assertNotIn("auctionPeriod", lots[2])

    # second update had a bug, and `"auctionPeriod": null` appeared for second and third lots
    auction_start_date_2 = calculate_tender_full_date(
        get_now(),
        timedelta(days=31),
        tender=self.tender_document,
    ).isoformat()
    response = self.check_chronograph(
        data={"data": {"lots": [{"auctionPeriod": {"startDate": auction_start_date_2}}, {}, {}]}}
    )
    lots = response.json["data"]["lots"]
    self.assertEqual(lots[0]["auctionPeriod"]["startDate"], auction_start_date_2)
    self.assertNotIn("auctionPeriod", lots[1])
    self.assertNotIn("auctionPeriod", lots[2])


def active_tendering_to_unsuccessful(self):
    response = self.set_status("active.pre-qualification", {"status": "active.tendering"})
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]
    self.assertNotIn("qualifications", tender)
    for b in tender["bids"]:
        self.assertEqual("unsuccessful", b["status"])
        if response.json["data"].get("lots"):
            self.assertIn("lotValues", b)
            self.assertNotIn("value", b["lotValues"][0])
        else:
            self.assertNotIn("lotValues", b)
            self.assertNotIn("value", b)


def pre_qual_switch_to_auction(self):
    response = self.set_status("active.auction", {"status": "active.pre-qualification"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")


def pre_qual_switch_to_stand_still(self):
    response = self.set_status("active.pre-qualification.stand-still", {"status": "active.pre-qualification"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")


# TenderSwitchAuctionResourceTest


def switch_to_auction(self):
    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]  # it's empty
    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active"}},
        )

    response = self.set_status("active.auction", {"status": "active.pre-qualification.stand-still"})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")
