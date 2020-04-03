# -*- coding: utf-8 -*-
from datetime import timedelta
from iso8601 import parse_date

from openprocurement.api.utils import get_now
from openprocurement.tender.pricequotation.tests.base import test_claim, test_author


# TenderSwitchTenderingResourceTest
from openprocurement.tender.core.utils import calculate_tender_business_date


# TenderSwitchQualificationResourceTest


def switch_to_qualification(self):
    self.set_status("active.qualification", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.assertEqual(len(response.json["data"]["awards"]), 1)


# TenderSwitchUnsuccessfulResourceTest

def switch_to_unsuccessful(self):
    self.set_status("active.qualification", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    if self.initial_lots:
        self.assertEqual(set([i["status"] for i in response.json["data"]["lots"]]), set(["unsuccessful"]))


# TenderAuctionPeriodResourceTest



# TenderComplaintSwitchResourceTest


def switch_to_ignored_on_complete(self):
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": test_claim
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")

    self.set_status("active.qualification", {"status": self.initial_status})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertEqual(response.json["data"]["complaints"][0]["status"], "ignored")


def switch_from_pending_to_ignored(self):
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": test_claim
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")

    tender = self.db.get(self.tender_id)
    tender["complaints"][0]["status"] = "pending"
    self.db.save(tender)

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["complaints"][0]["status"], "ignored")


def switch_from_pending(self):
    for status in ["invalid", "resolved", "declined"]:
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": test_claim
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.json["data"]["status"], "claim")

    tender = self.db.get(self.tender_id)
    for index, status in enumerate(["invalid", "resolved", "declined"]):
        tender["complaints"][index]["status"] = "pending"
        tender["complaints"][index]["resolutionType"] = status
        tender["complaints"][index]["dateEscalated"] = "2017-06-01"
    self.db.save(tender)

    response = self.check_chronograph()
    for index, status in enumerate(["invalid", "resolved", "declined"]):
        self.assertEqual(response.json["data"]["complaints"][index]["status"], status)


def switch_to_complaint(self):
    for status in ["invalid", "resolved", "declined"]:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": test_claim
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

        tender = self.db.get(self.tender_id)
        tender["complaints"][-1]["dateAnswered"] = (
            get_now() - timedelta(days=1 if "procurementMethodDetails" in tender else 4)
        ).isoformat()
        self.db.save(tender)

        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["complaints"][-1]["status"], status)


# TenderAwardComplaintSwitchResourceTest


def award_switch_to_ignored_on_complete(self):
    token = self.initial_bids_tokens.values()[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
        {
            "data": test_claim
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    contract_id = response.json["data"]["contracts"][-1]["id"]

    tender = self.db.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)

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


def award_switch_from_pending_to_ignored(self):
    token = self.initial_bids_tokens.values()[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
        {
            "data": test_claim
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "claim")

    tender = self.db.get(self.tender_id)
    tender["awards"][0]["complaints"][0]["status"] = "pending"
    self.db.save(tender)

    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["awards"][0]["complaints"][0]["status"], "ignored")


def award_switch_from_pending(self):
    token = self.initial_bids_tokens.values()[0]
    for status in ["invalid", "resolved", "declined"]:
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
            {
                "data": test_claim
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.json["data"]["status"], "claim")

    tender = self.db.get(self.tender_id)
    for index, status in enumerate(["invalid", "resolved", "declined"]):
        tender["awards"][0]["complaints"][index]["status"] = "pending"
        tender["awards"][0]["complaints"][index]["resolutionType"] = status
        tender["awards"][0]["complaints"][index]["dateEscalated"] = "2017-06-01"
    self.db.save(tender)

    response = self.check_chronograph()
    for index, status in enumerate(["invalid", "resolved", "declined"]):
        self.assertEqual(response.json["data"]["awards"][0]["complaints"][index]["status"], status)


def award_switch_to_complaint(self):
    token = self.initial_bids_tokens.values()[0]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(self.tender_id, self.award_id, self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    for status in ["invalid", "resolved", "declined"]:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
            {
                "data": test_claim
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

        tender = self.db.get(self.tender_id)
        tender["awards"][0]["complaints"][-1]["dateAnswered"] = (
            get_now() - timedelta(days=1 if "procurementMethodDetails" in tender else 4)
        ).isoformat()
        self.db.save(tender)

        response = self.check_chronograph()
        self.assertEqual(response.json["data"]["awards"][0]["complaints"][-1]["status"], status)
