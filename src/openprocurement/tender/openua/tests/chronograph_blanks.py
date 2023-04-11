# -*- coding: utf-8 -*-
from copy import deepcopy

from openprocurement.api.utils import parse_date
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_claim,
    test_tender_below_author,
)
from openprocurement.tender.core.tests.utils import change_auth


# TenderSwitch0BidResourceTest


def set_auction_period_0bid(self):
    start_date = "9999-01-01T00:00:00+00:00"
    response = self.check_chronograph({"data": {"auctionPeriod": {"startDate": start_date}}})
    self.assertEqual(response.json["data"]["auctionPeriod"]["startDate"], start_date)


# TenderSwitch1BidResourceTest


def switch_to_unsuccessful_1bid(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


# TenderSwitchAuctionResourceTest


def switch_to_complaint(self):
    claim_data = deepcopy(test_tender_below_claim)
    claim_data["author"] = getattr(self, "author_data", test_tender_below_author)
    for status in ["invalid", "resolved", "declined"]:
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": claim_data
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.json["data"]["status"], "claim")
        complaint = response.json["data"]

        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
            {"data": {"status": "answered", "resolution": status * 4, "resolutionType": status}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "answered")
        self.assertEqual(response.json["data"]["resolutionType"], status)

    response = self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")
    self.assertEqual(response.json["data"]["complaints"][-1]["status"], status)


def switch_to_unsuccessful(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()

    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(self.tender_id))
    response = self.app.post_json(
        "/tenders/{}/auction".format(self.tender_id),
        {"data": {"bids": [
            {} for b in response.json["data"]["bids"]
        ]}}
    )
    self.assertEqual(response.json["data"]["status"], "active.qualification")

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award_id), {"data": {"status": "unsuccessful"}}
    )

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}".format(self.tender_id, award_id), {"data": {"status": "unsuccessful"}}
    )

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def set_auction_period(self):
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    item = response.json["data"]
    self.assertIn("auctionPeriod", item)
    self.assertIn("shouldStartAfter", item["auctionPeriod"])
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertEqual(
        parse_date(response.json["data"]["next_check"]),
        parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )

    start_date = "9999-01-01T00:00:00+00:00"
    response = self.check_chronograph({"data": {"auctionPeriod": {"startDate": start_date}}})
    item = response.json["data"]
    self.assertEqual(item["auctionPeriod"]["startDate"], start_date)


# TenderLotSwitch0BidResourceTest
# TenderLotSwitchAuctionResourceTest


# TenderLotSwitch0BidResourceTest


def switch_to_unsuccessful_lot_0bid(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertEqual(set([i["status"] for i in response.json["data"]["lots"]]), set(["unsuccessful"]))


def set_auction_period_lot_0bid(self):
    start_date = "9999-01-01T00:00:00+00:00"
    data = {"data": {"lots": [{"auctionPeriod": {"startDate": start_date}} for i in self.initial_lots]}}
    response = self.check_chronograph(data)
    self.assertEqual(response.json["data"]["lots"][0]["auctionPeriod"]["startDate"], start_date)

    response = self.check_chronograph({"data": {"lots": [{"auctionPeriod": None}]}})
    self.assertEqual(response.json["data"]["lots"][0]["auctionPeriod"]["startDate"], start_date)


# TenderLotSwitch1BidResourceTest


def switch_to_unsuccessful_lot_1bid(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


# TnederLotSwitchAuctionResourceTest


def switch_to_auction_lot(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")


def switch_to_unsuccessful_lot(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()

    with change_auth(self.app, ("Basic", ("auction", ""))):
        response = self.app.get("/tenders/{}/auction".format(self.tender_id))
        auction_bids_data = response.json["data"]["bids"]
        for lot in response.json["data"]["lots"]:
            response = self.app.post_json(
                "/tenders/{}/auction/{}".format(self.tender_id, lot["id"]),
                {"data": {"bids": [
                    {"id": b["id"], "lotValues": [{"relatedLot": l["relatedLot"]} for l in b["lotValues"]]}
                    for b in auction_bids_data]}}
            )
            self.assertEqual(response.status, "200 OK")

    self.assertEqual(response.json["data"]["status"], "active.qualification")

    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.get("/tenders/{}/awards".format(self.tender_id))
        while any([i["status"] == "pending" for i in response.json["data"]]):
            award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
            self.app.patch_json(
                "/tenders/{}/awards/{}".format(self.tender_id, award_id), {"data": {"status": "unsuccessful"}}
            )
            response = self.app.get("/tenders/{}/awards".format(self.tender_id))

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def set_auction_period_lot(self):
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    item = response.json["data"]["lots"][0]
    self.assertIn("auctionPeriod", item)
    self.assertIn("shouldStartAfter", item["auctionPeriod"])
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertEqual(
        parse_date(response.json["data"]["next_check"]),
        parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )

    start_date = "9999-01-01T00:00:00+00:00"
    data = {"data": {"lots": [{"auctionPeriod": {"startDate": start_date}} for i in self.initial_lots]}}
    response = self.check_chronograph(data)
    item = response.json["data"]["lots"][0]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(item["auctionPeriod"]["startDate"], start_date)
