# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_claim,
    test_tender_below_draft_claim,
    test_tender_below_complaint,
    test_tender_below_author,
    test_tender_below_draft_complaint,
)
from mock import patch
from copy import deepcopy
from datetime import timedelta


def create_tender_complaint(self):
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": complaint_data,
        },
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    self.assertEqual(complaint["status"], "draft")

    claim_data = deepcopy(test_tender_below_claim)
    claim_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": claim_data
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.assertEqual(complaint["author"]["name"], self.test_author["name"])
    self.assertIn("id", complaint)
    self.assertIn(complaint["id"], response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
        {"data": {"status": "answered"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "resolutionType"}],
    )

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
        {"data": {"status": "answered", "resolutionType": "invalid", "resolution": "spam 100% " * 3}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "answered")
    self.assertEqual(response.json["data"]["resolutionType"], "invalid")
    self.assertEqual(response.json["data"]["resolution"], "spam 100% " * 3)

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"satisfied": True, "status": "resolved"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "resolved")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"status": "cancelled", "cancellationReason": "reason"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update complaint in current (resolved) status")

    self.set_status("unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": claim_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint in current (unsuccessful) tender status"
    )


def patch_tender_complaint(self):
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
            {"data": {"status": "cancelled", "cancellationReason": "reason"}},
            status=200,
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "cancelled")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")
    else:
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
            {"data": {"status": "cancelled", "cancellationReason": "reason"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"],
                         "Can't update complaint from draft to cancelled status")

    claim_data = deepcopy(test_tender_below_draft_claim)
    claim_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": claim_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
        {"data": {"status": "cancelled", "cancellationReason": "reason"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"title": "claim title"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "claim title")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"status": "claim"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "claim")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
        {"data": {"resolution": "changing rules"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["resolution"], "changing rules")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
        {"data": {"status": "answered", "resolutionType": "resolved", "resolution": "resolution text" * 2}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "answered")
    self.assertEqual(response.json["data"]["resolutionType"], "resolved")
    self.assertEqual(response.json["data"]["resolution"], "resolution text" * 2)

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"satisfied": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["satisfied"], False)

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"status": "resolved"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update complaint from answered to resolved status")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"status": "pending"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update complaint from answered to pending status"
    )

    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/complaints/{}".format(self.tender_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    with change_auth(self.app, ("Basic", ("administrator", ""))):  # test value update
        request_data = {
            "status": "draft",
            "value": {
                "amount": 103,
                "currency": "USD",
            }
        }
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}".format(self.tender_id, complaint["id"]),
            {"data": request_data},
        )
        data = response.json["data"]
        self.assertEqual(data["value"], request_data["value"])
        self.assertEqual(data["status"], "pending")

        tender = self.mongodb.tenders.get(self.tender_id)
        for c in tender["complaints"]:
            if c["id"] == complaint["id"]:
                self.assertEqual(c["value"], request_data["value"])
                self.assertEqual(c["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/complaints/some_id".format(self.tender_id),
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "complaint_id"}]
    )

    response = self.app.patch_json(
        "/tenders/some_id/complaints/some_id",
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
            {"data": {"status": "stopping"}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{"description": ["This field is required."], "location": "body", "name": "cancellationReason"}],
        )

        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
            {"data": {"status": "stopping", "cancellationReason": "reason"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "stopping")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")
    else:
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
            {"data": {"status": "stopping", "cancellationReason": "reason"}},
            status=403,
        )

        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update complaint from pending to stopping status"
        )

    claim_data = deepcopy(test_tender_below_draft_claim)
    claim_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": claim_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    # create complaint
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"status": "claim"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Value must be one of ['draft', 'pending', 'accepted', 'invalid', 'resolved', 'declined', 'cancelled', 'satisfied', 'stopping', 'stopped', 'mistaken']."]
    )

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"status": "cancelled", "cancellationReason": "test string"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update complaint in current (complete) tender status"
    )


@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def bot_patch_tender_complaint(self):
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")


@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def bot_patch_tender_complaint_mistaken(self):
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
            {"data": {"status": "mistaken"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "mistaken")
        self.assertEqual(response.json["data"]["rejectReason"], "incorrectPayment")


@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() + timedelta(days=1))
def bot_patch_tender_complaint_forbidden(self):
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
            {"data": {"status": "pending"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update complaint from draft to pending status"
        )


def review_tender_complaint(self):
    now = get_now()
    for status in ["invalid", "stopped", "satisfied", "declined"]:
        self.app.authorization = ("Basic", ("broker", ""))

        complaint_data = deepcopy(test_tender_below_complaint)
        complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": complaint_data
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        complaint = response.json["data"]

        if RELEASE_2020_04_19 < now:
            self.assertEqual(response.json["data"]["status"], "draft")

            with change_auth(self.app, ("Basic", ("bot", ""))):
                response = self.app.patch_json(
                    "/tenders/{}/complaints/{}".format(self.tender_id, complaint["id"]),
                    {"data": {"status": "pending"}},
                )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], "pending")

        self.app.authorization = ("Basic", ("reviewer", ""))
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}".format(self.tender_id, complaint["id"]),
            {"data": {"decision": "{} complaint".format(status), "rejectReasonDescription": "reject reason"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["decision"], "{} complaint".format(status))
        self.assertEqual(response.json["data"]["rejectReasonDescription"], "reject reason")

        if status in ["satisfied", "declined", "stopped"]:
            data = {"status": "accepted"}
            if RELEASE_2020_04_19 < now:
                data.update({
                    "reviewDate": now.isoformat(),
                    "reviewPlace": "some",
                })
            response = self.app.patch_json(
                "/tenders/{}/complaints/{}".format(self.tender_id, complaint["id"]),
                {"data": data}
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], "accepted")

            if RELEASE_2020_04_19 < now:
                self.assertEqual(response.json["data"]["reviewPlace"], "some")
                self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

            now = get_now()
            data = {"decision": "accepted:{} complaint".format(status)}

            if RELEASE_2020_04_19 > now:
                data.update({
                    "reviewDate": now.isoformat(),
                    "reviewPlace": "some",
                })

            response = self.app.patch_json(
                "/tenders/{}/complaints/{}".format(self.tender_id, complaint["id"]),
                {"data": data},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["decision"], "accepted:{} complaint".format(status))

            if RELEASE_2020_04_19 > now:
                self.assertEqual(response.json["data"]["reviewPlace"], "some")
                self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

        now = get_now()
        data = {"status": status}

        if RELEASE_2020_04_19 < now:
            if status in ["invalid", "stopped"]:
                data.update({
                    "rejectReason": "tenderCancelled",
                    "rejectReasonDescription": "reject reason description"
                })

        response = self.app.patch_json(
            "/tenders/{}/complaints/{}".format(self.tender_id, complaint["id"]), {"data": data}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], status)


@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def mistaken_status_tender_complaint(self):
    complaint_data = deepcopy(test_tender_below_complaint)
    complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
    complaint_data["status"] = "draft"
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    complaint_id = complaint["id"]
    self.assertEqual(complaint["status"], "draft")
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint_id, owner_token),
        {"data": {"status": "mistaken"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    self.assertEqual(complaint["status"], "mistaken")
    self.assertEqual(complaint["rejectReason"], "cancelledByComplainant")

    forbidden_statuses = [
        {"status": "draft"},
        {"status": "pending"},
        {"status": "invalid", "rejectReason": "alreadyExists"},
        {"status": "resolved"},
        {"status": "declined"},
        {"status": "cancelled", "cancellationReason": "reason"},
    ]

    for status_data in forbidden_statuses:
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint_id, owner_token),
            {"data": status_data},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Forbidden")

    bad_statuses = [
        {"status": "claim"},
        {"status": "answered", "resolutionType": "invalid"},
    ]

    for status_data in bad_statuses:
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint_id, owner_token),
            {"data": status_data},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": complaint_data},
    )
    complaint = response.json["data"]
    complaint_id = complaint["id"]
    self.assertEqual(complaint["status"], "draft")
    owner_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint_id, owner_token),
            {"data": {"status": "pending"}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint_id, owner_token),
        {"data": {"status": "mistaken"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")

    claim_data = deepcopy(test_tender_below_draft_claim)
    claim_data["status"] = "claim"
    claim_data["author"] = getattr(self, "test_author", test_tender_below_author)

    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": claim_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    complaint_id = complaint["id"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint_id, owner_token),
        {"data": {"status": "mistaken"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"][0],
        "Value must be one of ['draft', 'claim', 'answered', 'pending', 'invalid', 'resolved', 'declined', 'cancelled']."
    )

    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": claim_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    complaint_id = complaint["id"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint_id, owner_token),
        {"data": {"status": "cancelled", "cancellationReason": "reason"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint_id, owner_token),
        {"data": {"status": "mistaken"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"][0],
        "Value must be one of ['draft', 'claim', 'answered', 'pending', 'invalid', 'resolved', 'declined', 'cancelled']."
    )

    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": claim_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    complaint_id = complaint["id"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint_id, self.tender_token),
        {"data": {"status": "answered", "resolution": "sdaghjg jgjh gjhg gjh", "resolutionType": "invalid"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint_id, owner_token),
        {"data": {"status": "mistaken"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"][0],
        "Value must be one of ['draft', 'claim', 'answered', 'pending', 'invalid', 'resolved', 'declined', 'cancelled']."
    )

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint_id, owner_token),
        {"data": {"status": "resolved", "tendererAction": "sdad sadas da", "satisfied": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint_id, owner_token),
        {"data": {"status": "mistaken"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"][0],
        "Value must be one of ['draft', 'claim', 'answered', 'pending', 'invalid', 'resolved', 'declined', 'cancelled']."
    )


def review_tender_stopping_complaint(self):
    if get_now() < RELEASE_2020_04_19:
        for status in ["satisfied", "stopped", "declined", "mistaken", "invalid"]:
            self.app.authorization = ("Basic", ("broker", ""))

            complaint_data = deepcopy(test_tender_below_complaint)
            complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
            response = self.app.post_json(
                "/tenders/{}/complaints".format(self.tender_id),
                {
                    "data": complaint_data
                },
            )
            self.assertEqual(response.status, "201 Created")
            self.assertEqual(response.content_type, "application/json")
            complaint = response.json["data"]
            owner_token = response.json["access"]["token"]

            url_patch_complaint = "/tenders/{}/complaints/{}".format(self.tender_id, complaint["id"])

            response = self.app.patch_json(
                "{}?acc_token={}".format(url_patch_complaint, owner_token),
                {"data": {"status": "stopping", "cancellationReason": "reason"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], "stopping")
            self.assertEqual(response.json["data"]["cancellationReason"], "reason")

            self.app.authorization = ("Basic", ("reviewer", ""))
            data = {"decision": "decision", "status": status}
            if status in ["invalid", "stopped"]:
                data.update({
                    "rejectReason": "tenderCancelled",
                    "rejectReasonDescription": "reject reason description"
                })
            response = self.app.patch_json(
                url_patch_complaint,
                {"data": data})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], status)
            self.assertEqual(response.json["data"]["decision"], "decision")
    else:
        pass
        # This test exist in patch_tender_complaint method


# TenderLotAwardComplaintResourceTest


def create_tender_lot_complaint(self):
    claim_data = deepcopy(test_tender_below_claim)
    claim_data["relatedLot"] = self.initial_lots[0]["id"]
    claim_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {
            "data": claim_data
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.assertEqual(complaint["author"]["name"], self.test_author["name"])
    self.assertIn("id", complaint)
    self.assertIn(complaint["id"], response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
        {"data": {"status": "answered"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "resolutionType"}],
    )

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
        {"data": {"status": "answered", "resolutionType": "invalid", "resolution": "spam 100% " * 3}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "answered")
    self.assertEqual(response.json["data"]["resolutionType"], "invalid")
    self.assertEqual(response.json["data"]["resolution"], "spam 100% " * 3)

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"satisfied": True, "status": "resolved"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "resolved")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"status": "cancelled", "cancellationReason": "reason"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update complaint in current (resolved) status")

    self.set_status("unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": claim_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint in current (unsuccessful) tender status"
    )


# TenderComplaintDocumentResourceTest


def put_tender_complaint_document(self):
    response = self.app.post(
        "/tenders/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.complaint_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put_json(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.tender_token
        ),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")

    response = self.app.put_json(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/complaints/{}/documents/{}?download={}".format(self.tender_id, self.complaint_id, doc_id, key)
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    response = self.app.get("/tenders/{}/complaints/{}/documents/{}".format(self.tender_id, self.complaint_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        "content3",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/complaints/{}/documents/{}?download={}".format(self.tender_id, self.complaint_id, doc_id, key)
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    with patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1)):
        with patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() - timedelta(days=1)):
            response = self.app.patch_json(
                "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, self.complaint_id,
                                                                self.complaint_owner_token),
                {"data": {"status": "pending"}},
                status=403
            )
    self.assertEqual(
        response.json,
        {"status": "error", "errors": [
            {"location": "body", "name": "data",
             "description": "Can't update complaint from draft to pending status"}]}
    )

    with patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() + timedelta(days=1)):
        with patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() + timedelta(days=1)):
            response = self.app.patch_json(
                "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, self.complaint_id,
                                                                self.complaint_owner_token),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.put(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        "content",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.set_status("complete")

    response = self.app.put_json(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
    )


def patch_tender_complaint_document(self):
    response = self.app.post(
        "/tenders/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.complaint_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get("/tenders/{}/complaints/{}/documents/{}".format(self.tender_id, self.complaint_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    with patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() + timedelta(days=1)):
        with patch("openprocurement.tender.core.validation.RELEASE_2020_04_19", get_now() + timedelta(days=1)):
            response = self.app.patch_json(
                "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, self.complaint_id,
                                                                self.complaint_owner_token),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description2"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["description"], "document description2")

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
    )
