from datetime import timedelta
from freezegun import freeze_time
from openprocurement.api.utils import get_now, parse_date
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_claim,
    test_tender_below_bids,
)


# TenderSwitchTenderingResourceTest


def switch_to_tendering_by_tender_period_start_date(self):
    self.set_status("active.tendering", {"status": "active.enquiries", "tenderPeriod": {}})
    response = self.check_chronograph()
    self.assertNotEqual(response.json["data"]["status"], "active.tendering")
    self.set_status("active.tendering", {"enquiryPeriod": {}})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.tendering")


# TenderSwitchQualificationResourceTest


def switch_to_qualification(self):
    self.set_status("active.auction", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.assertEqual(len(response.json["data"]["awards"]), 1)


def switch_to_qualification_one_bid(self):
    # # switch to tendering
    self.set_status(
        "active.tendering",
        {"status": "active.enquiries",
         "tenderPeriod": {"startDate": get_now().isoformat()}}
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


def switch_to_auction_lot_items(self):
    """
    Test lot tender with non lot items (item.relatedLot is missed)
    """
    self.app.patch_json(
        f'/tenders/{self.tender_id}?acc_token={self.tender_token}',
        {'data': {
            "items": self.initial_data["items"] * 2
        }}
    )
    self.set_status("active.auction", {"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(len(response.json["data"]["items"]), 2)  # non lot items are still there for no reason


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
    self.assertGreaterEqual(
        item["auctionPeriod"]["shouldStartAfter"],
        response.json["data"]["tenderPeriod"]["endDate"]
    )
    self.assertIn("T00:00:00+", item["auctionPeriod"]["shouldStartAfter"])
    self.assertEqual(
        parse_date(response.json["data"]["next_check"]),
        parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )

    response, item = check_chronograph(auction_period_data={"startDate": "9999-01-01T00:00:00"})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(item["auctionPeriod"]["startDate"], "9999-01-01T00:00:00+02:00")


def set_auction_period_lot_separately(self):

    self.set_status("active.tendering", {"status": "active.enquiries"})
    response = self.check_chronograph()
    data = response.json["data"]

    self.assertEqual(data["status"], "active.tendering")

    for lot in data["lots"]:
        self.assertIn("auctionPeriod", lot)
        self.assertIn("shouldStartAfter", lot["auctionPeriod"])

    # set startDate for the first lot
    start_date = (get_now() + timedelta(days=1)).isoformat()
    response = self.check_chronograph({"data": {
        "auctionPeriod": None,
        "lots": [
            {"auctionPeriod": {"startDate": start_date}},
            {}
        ]
    }})

    lot = response.json["data"]["lots"][0]
    self.assertIn("auctionPeriod", lot)
    self.assertIn("shouldStartAfter", lot["auctionPeriod"])
    self.assertIn("startDate", lot["auctionPeriod"])

    lot = response.json["data"]["lots"][1]
    self.assertIn("auctionPeriod", lot)
    self.assertIn("shouldStartAfter", lot["auctionPeriod"])
    self.assertNotIn("startDate", lot["auctionPeriod"])

    # set startDate for the second lot
    response = self.check_chronograph({"data": {"lots": [
        {},
        {"auctionPeriod": {"startDate": start_date}},
    ]}})
    for lot in response.json["data"]["lots"]:
        self.assertIn("auctionPeriod", lot)
        self.assertIn("shouldStartAfter", lot["auctionPeriod"])
        self.assertIn("startDate", lot["auctionPeriod"])


def reset_auction_period(self):
    def check_chronograph(auction_period_data=None):
        if self.initial_lots:
            data = None
            if auction_period_data:
                data = {"data": {"lots": [{"auctionPeriod": auction_period_data}]}}
                for _ in range(1, len(self.initial_lots)):
                    data["data"]["lots"].append({})
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
    self.assertEqual(
        parse_date(response.json["data"]["next_check"]),
        parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )

    response, item = check_chronograph(auction_period_data={"startDate": "9999-01-01T00:00:00"})
    self.assertEqual(response.status, "200 OK")
    self.assertGreaterEqual(
        item["auctionPeriod"]["shouldStartAfter"],
        response.json["data"]["tenderPeriod"]["endDate"]
    )
    self.assertIn("9999-01-01T00:00:00", item["auctionPeriod"]["startDate"])

    self.set_status("active.auction", {"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.auction")
    item = response.json["data"]["lots"][0] if self.initial_lots else response.json["data"]
    self.assertGreaterEqual(
        item["auctionPeriod"]["shouldStartAfter"],
        response.json["data"]["tenderPeriod"]["endDate"]
    )

    response, item = check_chronograph(auction_period_data={"startDate": "9999-01-01T00:00:00"})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.auction")
    self.assertGreaterEqual(
        item["auctionPeriod"]["shouldStartAfter"],
        response.json["data"]["tenderPeriod"]["endDate"]
    )
    self.assertIn("9999-01-01T00:00:00", item["auctionPeriod"]["startDate"])
    self.assertIn("9999-01-01T00:00:00", response.json["data"]["next_check"])
    if self.initial_lots:
        for l in response.json["data"]["lots"]:
            if l.get("status", "active") == "active":
                self.assertIn("auctionPeriod", l)
            elif l.get("status", "active") == "unsuccessful":
                self.assertNotIn("auctionPeriod", l)
    now = get_now()
    response, item = check_chronograph(auction_period_data={"startDate": now.isoformat()})
    self.assertEqual(response.json["data"]["status"], "active.auction")
    item = response.json["data"]["lots"][0] if self.initial_lots else response.json["data"]
    self.assertGreaterEqual(
        item["auctionPeriod"]["shouldStartAfter"],
        response.json["data"]["tenderPeriod"]["endDate"]
    )
    self.assertIn(now.isoformat(), item["auctionPeriod"]["startDate"])
    self.assertGreater(
        parse_date(response.json["data"]["next_check"]),
        parse_date(item["auctionPeriod"]["startDate"])
    )
    self.assertEqual(
        response.json["data"]["next_check"],
        self.mongodb.tenders.get(self.tender_id)["next_check"]
    )
    tender_period_end_date = response.json["data"]["tenderPeriod"]["endDate"]
    response, item = check_chronograph(auction_period_data={"startDate": tender_period_end_date})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.auction")
    self.assertGreaterEqual(
        item["auctionPeriod"]["shouldStartAfter"],
        response.json["data"]["tenderPeriod"]["endDate"]
    )
    self.assertIn(tender_period_end_date, item["auctionPeriod"]["startDate"])
    self.assertGreater(
        parse_date(response.json["data"]["next_check"]),
        parse_date(response.json["data"]["tenderPeriod"]["endDate"])
    )

    self.assertGreater(
        self.mongodb.tenders.get(self.tender_id)["next_check"],
        response.json["data"]["tenderPeriod"]["endDate"]
    )

    self.time_shift("active.auction", shift=-timedelta(days=2))

    response, item = check_chronograph()
    self.assertGreaterEqual(
        item["auctionPeriod"]["shouldStartAfter"],
        response.json["data"]["tenderPeriod"]["endDate"]
    )
    self.assertNotIn("next_check", response.json["data"])
    self.assertNotIn("next_check", self.mongodb.tenders.get(self.tender_id))
    shouldStartAfter = item["auctionPeriod"]["shouldStartAfter"]

    response, item = check_chronograph()
    self.assertEqual(item["auctionPeriod"]["shouldStartAfter"], shouldStartAfter)
    self.assertNotIn("next_check", response.json["data"])

    response, item = check_chronograph(auction_period_data={"startDate": "9999-01-01T00:00:00"})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active.auction")
    self.assertGreaterEqual(item["auctionPeriod"]["shouldStartAfter"], response.json["data"]["tenderPeriod"]["endDate"])
    self.assertIn("9999-01-01T00:00:00", item["auctionPeriod"]["startDate"])
    self.assertIn("9999-01-01T00:00:00", response.json["data"]["next_check"])


# TenderComplaintSwitchResourceTest


def switch_to_ignored_on_complete(self):
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": test_tender_below_claim
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")

    self.set_status("active.auction", {"status": self.initial_status})
    self.check_chronograph()
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertEqual(response.json["data"]["complaints"][0]["status"], "ignored")


# TODO we keep pending status for claims for now: to check if we can depreciate it
def switch_from_pending_to_ignored(self):
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": test_tender_below_claim
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["complaints"][0]["status"] = "pending"
    self.mongodb.tenders.save(tender)

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["complaints"][0]["status"], "ignored")


# TODO we keep pending status for claims for now: to check if we can depreciate it
def switch_from_pending(self):
    for status in ["invalid", "resolved", "declined"]:
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": test_tender_below_claim
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.json["data"]["status"], "claim")

    tender = self.mongodb.tenders.get(self.tender_id)
    for index, status in enumerate(["invalid", "resolved", "declined"]):
        tender["complaints"][index]["status"] = "pending"
        tender["complaints"][index]["resolutionType"] = status
        tender["complaints"][index]["dateEscalated"] = "2017-06-01"
    self.mongodb.tenders.save(tender)

    response = self.check_chronograph()
    for index, status in enumerate(["invalid", "resolved", "declined"]):
        self.assertEqual(response.json["data"]["complaints"][index]["status"], status)


def switch_to_complaint(self):
    for status in ["invalid", "resolved", "declined"]:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": test_tender_below_claim
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

        tender = self.mongodb.tenders.get(self.tender_id)
        tender["complaints"][-1]["dateAnswered"] = (
            get_now() - timedelta(days=1 if "procurementMethodDetails" in tender else 4)
        ).isoformat()
        self.mongodb.tenders.save(tender)

        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["complaints"][-1]["status"], status)


# TenderAwardComplaintSwitchResourceTest


def award_switch_to_ignored_on_complete(self):
    token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
        {
            "data": test_tender_below_claim
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract_id = response.json["data"]["contracts"][-1]["id"]

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["awards"][0]["complaints"][0]["status"], "ignored")


# TODO we keep pending status for claims for now: to check if we can depreciate it
def award_switch_from_pending_to_ignored(self):
    token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
        {
            "data": test_tender_below_claim
        },
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
            {
                "data": test_tender_below_claim
            },
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
            {
                "data": test_tender_below_claim
            },
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
