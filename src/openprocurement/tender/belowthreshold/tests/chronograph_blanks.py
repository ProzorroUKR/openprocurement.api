from datetime import timedelta

from freezegun import freeze_time

from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_bids,
    test_tender_below_claim,
)
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.tests.utils import activate_contract, change_auth

# TenderSwitchTenderingResourceTest


def switch_to_tendering_by_tender_period_start_date(self):
    self.set_status("active.enquiries")

    response = self.check_chronograph()
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "active.enquiries")  # not changed

    self.set_status(
        "active.tendering",
        extra={"status": "active.enquiries"},
    )

    response = self.check_chronograph()
    self.assertEqual((response.status, response.content_type), ("200 OK", "application/json"))
    self.assertEqual(response.json["data"]["status"], "active.tendering")  # now changed


# TenderSwitchQualificationResourceTest


def switch_to_qualification(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.assertEqual(len(response.json["data"]["awards"]), 1)


def switch_to_qualification_one_bid(self):
    # # switch to tendering
    self.set_status(
        "active.tendering", {"status": "active.enquiries", "tenderPeriod": {"startDate": get_now().isoformat()}}
    )
    response = self.check_chronograph(data={"data": {"auctionPeriod": {"startDate": get_now().isoformat()}}})
    self.assertEqual(response.json["data"]["status"], "active.tendering")

    self.create_bid(self.tender_id, test_tender_below_bids[0])

    # switch to auction
    self.set_status("active.auction", {"status": "active.tendering"})
    response = self.check_chronograph()

    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.assertNotIn("auctionPeriod", response.json["data"])
    self.assertEqual(len(response.json["data"]["awards"]), 1)


# TenderSwitchAuctionResourceTest


def switch_to_auction(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")


def switch_to_auction_with_non_auction_lot(self):
    """
    Test lot tender with non lot items (item.relatedLot is missed)
    """
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    lots = response.json["data"]["lots"]
    self.assertIn("auctionPeriod", lots[0])
    self.assertIn("auctionPeriod", lots[1])

    # move to auction
    with freeze_time(response.json["data"]["tenderPeriod"]["endDate"]):
        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["status"], "active.auction")

    # check that auction doesn't see auctionPeriod in lots
    # where less than two bidders
    with change_auth(self.app, ("Basic", ("auction", ""))):
        response = self.app.get(f"/tenders/{self.tender_id}/auction")
    lots = response.json["data"]["lots"]
    self.assertEqual("active", lots[0]["status"])
    self.assertIn("auctionPeriod", lots[0])
    self.assertEqual("active", lots[1]["status"])
    self.assertNotIn("auctionPeriod", lots[1])


# TenderSwitchUnsuccessfulResourceTest


def switch_to_unsuccessful(self):
    self.set_status("active.auction", {"status": self.initial_status})

    response = self.app.get(f"/tenders/{self.tender_id}")
    if self.initial_lots:
        lot_date = response.json["data"]["lots"][0]["date"]

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    if self.initial_lots:
        self.assertEqual({i["status"] for i in response.json["data"]["lots"]}, {"unsuccessful"})

        response = self.app.get(f"/tenders/{self.tender_id}")
        self.assertGreater(response.json["data"]["lots"][0]["date"], lot_date)


# TenderAuctionPeriodResourceTest


def set_auction_period(self):
    def check_chronograph(auction_period_data=None):
        if self.initial_lots:
            data = {"data": {"lots": [{"auctionPeriod": auction_period_data}]}} if auction_period_data else None
            ch_response = self.check_chronograph(data)
            ch_response_item = ch_response.json["data"]["lots"][0]
        else:
            data = {"data": {"auctionPeriod": auction_period_data}} if auction_period_data else None
            ch_response = self.check_chronograph(data)
            ch_response_item = ch_response.json["data"]
        return ch_response, ch_response_item

    self.set_status("active.tendering", {"status": "active.enquiries"})

    response, item = check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    self.assertIn("auctionPeriod", item)
    self.assertIn("shouldStartAfter", item["auctionPeriod"])
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertIn("T00:00:00+", item["auctionPeriod"]["shouldStartAfter"])
    self.assertEqual(
        parse_date(response.json["data"]["next_check"]), parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )

    response, item = check_chronograph(auction_period_data={"startDate": "9999-01-01T00:00:00"})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(item["auctionPeriod"]["startDate"], "9999-01-01T00:00:00+02:00")


def set_auction_period_lot_separately(self):
    self.set_status("active.tendering", {"status": "active.enquiries"})
    response = self.check_chronograph()
    data = response.json["data"]

    self.assertEqual(data["status"], "active.tendering")

    should_after_dates = []
    start_dates = []
    for lot in data["lots"]:
        self.assertIn("auctionPeriod", lot)
        self.assertIn("shouldStartAfter", lot["auctionPeriod"])
        should_after_dates.append(lot["auctionPeriod"]["shouldStartAfter"])

        self.assertIn("startDate", lot["auctionPeriod"])
        start_dates.append(lot["auctionPeriod"]["startDate"])

    # chronograph planner still can update auctionPeriod.startDate
    # I don't expect it will though
    # we will remove this possibility as an additional step
    valid_start_date = (dt_from_iso(should_after_dates[0]) + timedelta(days=1)).isoformat()
    invalid_start_date = (dt_from_iso(should_after_dates[1]) - timedelta(days=1)).isoformat()
    response = self.check_chronograph(
        {
            "data": {
                "auctionPeriod": None,
                "lots": [
                    {"auctionPeriod": {"startDate": valid_start_date}},
                    {"auctionPeriod": {"startDate": invalid_start_date}},
                ],
            }
        }
    )

    lot = response.json["data"]["lots"][0]
    self.assertIn("auctionPeriod", lot)
    self.assertIn("shouldStartAfter", lot["auctionPeriod"])
    self.assertNotEqual(lot["auctionPeriod"]["startDate"], start_dates[0])  # automatically set value replaced
    self.assertEqual(lot["auctionPeriod"]["startDate"], valid_start_date)  # by chronograph

    lot = response.json["data"]["lots"][1]
    self.assertIn("auctionPeriod", lot)
    self.assertIn("shouldStartAfter", lot["auctionPeriod"])
    self.assertNotEqual(lot["auctionPeriod"]["startDate"], start_dates[1])  # this one is replaced by invalid
    self.assertNotEqual(lot["auctionPeriod"]["startDate"], invalid_start_date)  # invalid is also updated
    self.assertGreater(lot["auctionPeriod"]["startDate"], lot["auctionPeriod"]["shouldStartAfter"])


def reset_auction_period(self):
    def check_chronograph():
        if self.initial_lots:
            ch_response = self.check_chronograph()
            ch_response_item = ch_response.json["data"]["lots"][0]
        else:
            ch_response = self.check_chronograph()
            ch_response_item = ch_response.json["data"]
        return ch_response, ch_response_item

    self.set_status("active.tendering", {"status": "active.enquiries"})

    response, item = check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    self.assertIn("auctionPeriod", item)
    self.assertIn("shouldStartAfter", item["auctionPeriod"])
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertGreater(item["auctionPeriod"]["startDate"], item["auctionPeriod"]["shouldStartAfter"])
    self.assertEqual(
        parse_date(response.json["data"]["next_check"]), parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )

    self.set_status("active.auction", {"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")
    item = response.json["data"]["lots"][0] if self.initial_lots else response.json["data"]
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertGreater(item["auctionPeriod"]["startDate"], item["auctionPeriod"]["shouldStartAfter"])

    if self.initial_lots:
        for l in response.json["data"]["lots"]:
            if l.get("status", "active") == "active":
                self.assertIn("auctionPeriod", l)
            elif l.get("status", "active") == "unsuccessful":
                self.assertNotIn("auctionPeriod", l)

    self.time_shift("active.auction", shift=-timedelta(days=2))

    response, item = check_chronograph()
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertIn("next_check", response.json["data"])
    self.assertGreater(item["auctionPeriod"]["startDate"], item["auctionPeriod"]["shouldStartAfter"])


# TenderAwardComplaintSwitchResourceTest


def award_switch_to_ignored_on_complete(self):
    token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
        {"data": test_tender_below_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract_id = response.json["data"]["contracts"][-1]["id"]

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    activate_contract(self, self.tender_id, contract_id, self.tender_token, token)

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["awards"][0]["complaints"][0]["status"], "ignored")


# TODO we keep pending status for claims for now: to check if we can depreciate it
def award_switch_from_pending_to_ignored(self):
    token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
        {"data": test_tender_below_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["awards"][0]["complaints"][0]["status"] = "pending"
    self.mongodb.tenders.save(tender)

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["awards"][0]["complaints"][0]["status"], "ignored")


# TODO we keep pending status for claims for now: to check if we can depreciate it
def award_switch_from_pending(self):
    token = list(self.initial_bids_tokens.values())[0]
    for status in ["invalid", "resolved", "declined"]:
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
            {"data": test_tender_below_claim},
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.json["data"]["status"], "claim")

    tender = self.mongodb.tenders.get(self.tender_id)
    for index, status in enumerate(["invalid", "resolved", "declined"]):
        tender["awards"][0]["complaints"][index]["status"] = "pending"
        tender["awards"][0]["complaints"][index]["resolutionType"] = status
        tender["awards"][0]["complaints"][index]["dateEscalated"] = "2017-06-01"
    self.mongodb.tenders.save(tender)

    response = self.check_chronograph()
    for index, status in enumerate(["invalid", "resolved", "declined"]):
        self.assertEqual(response.json["data"]["awards"][0]["complaints"][index]["status"], status)


def award_switch_to_complaint(self):
    token = list(self.initial_bids_tokens.values())[0]
    for status in ["invalid", "resolved", "declined"]:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
            {"data": test_tender_below_claim},
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.json["data"]["status"], "claim")
        complaint = response.json["data"]

        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], self.tender_token
            ),
            {"data": {"status": "answered", "resolution": status * 4, "resolutionType": status}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "answered")
        self.assertEqual(response.json["data"]["resolutionType"], status)

        tender = self.mongodb.tenders.get(self.tender_id)
        tender["awards"][0]["complaints"][-1]["dateAnswered"] = (
            get_now() - timedelta(days=1 if "procurementMethodDetails" in tender else 4)
        ).isoformat()
        self.mongodb.tenders.save(tender)

        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["awards"][0]["complaints"][-1]["status"], status)
