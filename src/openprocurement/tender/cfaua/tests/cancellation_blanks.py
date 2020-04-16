# -*- coding: utf-8 -*-
from datetime import timedelta
from mock import patch

from openprocurement.tender.core.tests.base import change_auth
from openprocurement.tender.belowthreshold.tests.base import test_complaint, test_claim
import jmespath

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.cfaua.tests.base import test_cancellation


def assert_statuses(self, rules={}):
    data = self.get_tender(role="broker").json
    for rule in rules:
        value = jmespath.search(rule, data)
        self.assertEqual(value, rules[rule])


def add_tender_complaints(self, statuses):
    # ['satisfied', 'stopped', 'declined', 'mistaken', 'invalid']
    for status in statuses:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": test_complaint
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        complaint = response.json["data"]
        owner_token = response.json["access"]["token"]
        url_patch_complaint = "/tenders/{}/complaints/{}".format(self.tender_id, complaint["id"])

        if RELEASE_2020_04_19 < get_now():
            with change_auth(self.app, ("Basic", ("bot", ""))):
                response = self.app.patch_json(
                    url_patch_complaint,
                    {"data": {"status": "pending"}},
                )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], "pending")

        response = self.app.patch_json(
            "{}?acc_token={}".format(url_patch_complaint, owner_token),
            {"data": {"status": "stopping", "cancellationReason": "reason"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "stopping")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")

        self.app.authorization = ("Basic", ("reviewer", ""))
        now = get_now()
        data = {"decision": "decision", "status": status}
        if RELEASE_2020_04_19 < now:
            if status in ["invalid", "stopped"]:
                data.update({
                    "rejectReason": "tenderCancelled",
                    "rejectReasonDescription": "reject reason description"
                })
        response = self.app.patch_json(url_patch_complaint, {"data": data})
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], status)
        self.assertEqual(response.json["data"]["decision"], "decision")
        self.app.authorization = ("Basic", ("broker", ""))


def cancellation_tender_active_tendering(self):
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": test_claim
        },
    )
    self.assertEqual(response.status, "201 Created")

    if RELEASE_2020_04_19 < get_now():
        self.set_complaint_period_end()

    self.cancel_tender()
    assert_statuses(
        self,
        rules={
            "data.status": "cancelled",
            "data.lots[*].status": ["active"],
            "data.bids[*].status": None,
            "data.qualifications[*].status": None,
            "data.awards[*].status": None,
            "data.agreements[*].status": None,
            "data.complaints[*].status": ["claim"],
        },
    )


def cancellation_tender_active_pre_qualification(self):
    now = get_now()
    statuses = ["invalid", "stopped", "mistaken"] if RELEASE_2020_04_19 > now else ["invalid"]
    add_tender_complaints(self, statuses)
    self.set_status("active.tendering", "end")
    self.check_chronograph()
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")
    self.cancel_tender()
    assert_statuses(
        self,
        rules={
            "data.status": "cancelled",
            "data.lots[*].status": ["active"],
            "data.bids[*].status": [
                "invalid.pre-qualification",
                "invalid.pre-qualification",
                "invalid.pre-qualification",
            ],
            "data.qualifications[*].status": ["pending", "pending", "pending"],
            "data.awards[*].status": None,
            "data.agreements[*].status": None,
            "data.complaints[*].status": statuses,
        },
    )


def cancellation_tender_active_pre_qualification_stand_still(self):
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": test_complaint
        },
    )
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]
    complaint_token = response.json["access"]["token"]

    if RELEASE_2020_04_19 < get_now():
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                 "/tenders/{}/complaints/{}".format(
                     self.tender_id, complaint_id),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    self.set_status("active.tendering", "end")
    self.app.authorization = ("Basic", ("reviewer", ""))
    now = get_now()
    data = {"status": "invalid"}
    if RELEASE_2020_04_19 < now:
        data.update({
            "rejectReason": "tenderCancelled",
            "rejectReasonDescription": "reject reason description"
        })
    response = self.app.patch_json(
        "/tenders/{}/complaints/{}".format(self.tender_id, complaint_id), {"data": data}
    )
    self.assertEqual(response.status, "200 OK")
    self.check_chronograph()
    self.set_status("active.pre-qualification.stand-still")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")

    self.app.authorization = ("Basic", ("broker", ""))

    if RELEASE_2020_04_19 > get_now():
        # Test for old rules
        # In new rules there will be 403 error
        self.cancel_tender()
        assert_statuses(
            self,
            rules={
                "data.status": "cancelled",
                "data.lots[*].status": ["active"],
                "data.bids[*].status": [
                    "invalid.pre-qualification",
                    "invalid.pre-qualification",
                    "invalid.pre-qualification",
                ],
                "data.qualifications[*].status": ["active", "active", "active"],
                "data.awards[*].status": None,
                "data.agreements[*].status": None,
                "data.complaints[*].status": ["invalid"],
            },
        )


def cancellation_tender_active_auction(self):
    now = get_now()
    statuses = ["invalid", "stopped", "mistaken"] if RELEASE_2020_04_19 > now else ["invalid"]
    add_tender_complaints(self, statuses)
    self.set_status("active.auction")
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.auction")
    if get_now() < RELEASE_2020_04_19:
        self.cancel_tender()
        assert_statuses(
            self,
            rules={
                "data.status": "cancelled",
                "data.lots[*].status": ["active"],
                "data.bids[*].status": [
                    "invalid.pre-qualification",
                    "invalid.pre-qualification",
                    "invalid.pre-qualification",
                ],
                "data.qualifications[*].status": ["active", "active", "active"],
                "data.awards[*].status": None,
                "data.agreements[*].status": None,
                "data.complaints[*].status": statuses,
            },
        )


def cancellation_tender_active_qualification(self):
    now = get_now()
    statuses = ["invalid", "stopped", "mistaken"] if RELEASE_2020_04_19 > now else ["invalid"]
    add_tender_complaints(self, statuses)
    self.set_status("active.qualification")
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    self.cancel_tender()
    assert_statuses(
        self,
        rules={
            "data.status": "cancelled",
            "data.lots[*].status": ["active"],
            "data.bids[*].status": ["active", "active", "active"],
            "data.qualifications[*].status": ["active", "active", "active"],
            "data.awards[*].status": ["pending", "pending", "pending"],
            "data.agreements[*].status": None,
            "data.complaints[*].status": statuses,
        },
    )


def cancellation_tender_active_qualification_stand_still(self):
    now = get_now()
    statuses = ["invalid", "stopped", "mistaken"] if RELEASE_2020_04_19 > now else ["invalid"]
    add_tender_complaints(self, statuses)
    self.set_status("active.qualification.stand-still")
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.qualification.stand-still")
    award_id = response.json["data"]["awards"][0]["id"]
    owner_token = self.initial_bids_tokens[response.json["data"]["bids"][0]["id"]]
    response = self.app.post_json(
        "/tenders/{0}/awards/{1}/complaints?acc_token={2}".format(self.tender_id, award_id, owner_token),
        {
            "data": test_complaint
        },
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    complaint_token = response.json["access"]["token"]

    if RELEASE_2020_04_19 < get_now():
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                 "/tenders/{}/awards/{}/complaints/{}".format(
                     self.tender_id, award_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    # set complaint status stopping to be able to cancel the lot
    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, award_id, complaint["id"], complaint_token
        ),
        {"data": {
            "status": "stopping",
            "cancellationReason": "want this test to pass",
        }},
    )
    assert response.status_code == 200

    self.set_status("active.qualification.stand-still", "end")
    self.check_chronograph()
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.qualification.stand-still")
    self.cancel_tender()
    assert_statuses(
        self,
        rules={
            "data.status": "cancelled",
            "data.lots[*].status": ["active"],
            "data.bids[*].status": ["active", "active", "active"],
            "data.qualifications[*].status": ["active", "active", "active"],
            "data.awards[*].status": ["active", "active", "active"],
            "data.agreements[*].status": None,
            "data.complaints[*].status": statuses,
        },
    )


def cancellation_tender_active_awarded(self):
    now = get_now()
    statuses = ["invalid", "stopped", "mistaken"] if RELEASE_2020_04_19 > now else ["invalid"]
    add_tender_complaints(self, statuses)
    self.set_status("active.awarded")
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    self.cancel_tender()
    assert_statuses(
        self,
        rules={
            "data.status": "cancelled",
            "data.lots[*].status": ["active"],
            "data.bids[*].status": ["active", "active", "active"],
            "data.qualifications[*].status": ["active", "active", "active"],
            "data.awards[*].status": ["active", "active", "active"],
            "data.agreements[*].status": ["cancelled"],
            "data.complaints[*].status": statuses,
        },
    )


# Cancellation lot
def cancel_lot_active_tendering(self):
    now = get_now()
    statuses = ["invalid", "stopped", "mistaken"] if RELEASE_2020_04_19 > now else ["invalid"]
    add_tender_complaints(self, statuses)
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    lot_id = response.json["data"]["lots"][0]["id"]
    if RELEASE_2020_04_19 > get_now():
        # Test for old rules
        # In new rules there will be 403 error
        self.cancel_tender(lot_id=lot_id)
        assert_statuses(
            self,
            rules={
                "data.status": "cancelled",
                "data.lots[*].status": ["cancelled"],
                "data.bids[*].status": None,
                "data.qualifications[*].status": None,
                "data.awards[*].status": None,
                "data.agreements[*].status": None,
                "data.complaints[*].status": statuses,
            },
        )


def cancel_lot_active_pre_qualification(self):
    now = get_now()
    statuses = ["invalid", "stopped", "mistaken"] if RELEASE_2020_04_19 > now else ["invalid"]
    add_tender_complaints(self, statuses)
    self.set_status("active.pre-qualification")
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification")
    lot_id = response.json["data"]["lots"][0]["id"]
    self.cancel_tender(lot_id=lot_id)
    assert_statuses(
        self,
        rules={
            "data.status": "cancelled",
            "data.lots[*].status": ["cancelled"],
            "data.bids[*].status": [
                "invalid.pre-qualification",
                "invalid.pre-qualification",
                "invalid.pre-qualification",
            ],
            "data.qualifications[*].status": ["cancelled", "cancelled", "cancelled"],
            "data.awards[*].status": None,
            "data.agreements[*].status": None,
            "data.complaints[*].status": statuses,
        },
    )


def cancel_lot_active_pre_qualification_stand_still(self):
    now = get_now()
    statuses = ["invalid", "stopped", "mistaken"] if RELEASE_2020_04_19 > now else ["invalid"]
    add_tender_complaints(self, statuses)
    self.set_status("active.pre-qualification.stand-still")
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")
    lot_id = response.json["data"]["lots"][0]["id"]
    if RELEASE_2020_04_19 > get_now():
        # Test for old rules
        # In new rules there will be 403 error
        self.cancel_tender(lot_id=lot_id)
        assert_statuses(
            self,
            rules={
                "data.status": "cancelled",
                "data.lots[*].status": ["cancelled"],
                "data.bids[*].status": [
                    "invalid.pre-qualification",
                    "invalid.pre-qualification",
                    "invalid.pre-qualification",
                ],
                "data.qualifications[*].status": ["cancelled", "cancelled", "cancelled"],
                "data.awards[*].status": None,
                "data.agreements[*].status": None,
                "data.complaints[*].status": statuses,
            },
        )


def cancel_lot_active_auction(self):
    now = get_now()
    statuses = ["invalid", "stopped", "mistaken"] if RELEASE_2020_04_19 > now else ["invalid"]
    add_tender_complaints(self, statuses)
    self.set_status("active.auction")
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.auction")
    lot_id = response.json["data"]["lots"][0]["id"]
    if RELEASE_2020_04_19 > get_now():
        self.cancel_tender(lot_id=lot_id)
        assert_statuses(
            self,
            rules={
                "data.status": "cancelled",
                "data.lots[*].status": ["cancelled"],
                "data.bids[*].status": [
                    "invalid.pre-qualification",
                    "invalid.pre-qualification",
                    "invalid.pre-qualification",
                ],
                "data.qualifications[*].status": ["cancelled", "cancelled", "cancelled"],
                "data.awards[*].status": None,
                "data.agreements[*].status": None,
                "data.complaints[*].status": statuses,
            },
        )
    else:
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"reasonType": "noDemand", "reason": "cancellation reason"}},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't create cancellation in current (active.auction) tender status",
        )


def cancel_lot_active_qualification(self):
    self.set_status("active.qualification")
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.qualification")
    lot_id = response.json["data"]["lots"][0]["id"]
    self.cancel_tender(lot_id=lot_id)
    assert_statuses(
        self,
        rules={
            "data.status": "cancelled",
            "data.lots[*].status": ["cancelled"],
            "data.bids[*].status": ["active", "active", "active"],
            "data.qualifications[*].status": ["cancelled", "cancelled", "cancelled"],
            "data.awards[*].status": ["pending", "pending", "pending"],
            "data.agreements[*].status": None,
            "data.complaints[*].status": None,
        },
    )


def cancel_lot_active_qualification_stand_still(self):
    self.set_status("active.qualification.stand-still")
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.qualification.stand-still")
    lot_id = response.json["data"]["lots"][0]["id"]
    if RELEASE_2020_04_19 > get_now():
        # Test for old rules
        # In new rules there will be 403 error
        self.cancel_tender(lot_id=lot_id)
        assert_statuses(
            self,
            rules={
                "data.status": "cancelled",
                "data.lots[*].status": ["cancelled"],
                "data.bids[*].status": ["active", "active", "active"],
                "data.qualifications[*].status": ["cancelled", "cancelled", "cancelled"],
                "data.awards[*].status": ["active", "active", "active"],
                "data.agreements[*].status": None,
                "data.complaints[*].status": None,
            },
        )


def cancel_lot_active_awarded(self):
    self.set_status("active.awarded")
    response = self.get_tender(role="broker")
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    lot_id = response.json["data"]["lots"][0]["id"]
    self.cancel_tender(lot_id=lot_id)
    assert_statuses(
        self,
        rules={
            "data.status": "cancelled",
            "data.lots[*].status": ["cancelled"],
            "data.bids[*].status": ["active", "active", "active"],
            "data.qualifications[*].status": ["cancelled", "cancelled", "cancelled"],
            "data.awards[*].status": ["active", "active", "active"],
            "data.agreements[*].status": ["cancelled"],
            "data.complaints[*].status": None,
        },
    )
