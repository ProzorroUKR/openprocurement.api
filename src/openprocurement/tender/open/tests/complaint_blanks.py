from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

from openprocurement.api.constants import RELEASE_2020_04_19, REQUESTED_REMEDIES_TYPES
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_author,
    test_tender_below_cancellation,
    test_tender_below_claim,
    test_tender_below_complaint,
    test_tender_below_draft_claim,
    test_tender_below_draft_complaint,
    test_tender_below_organization,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.open.tests.base import test_tender_open_complaint_objection


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
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update complaint from draft to cancelled status"
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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "complaint_id"}])

    response = self.app.patch_json(
        "/tenders/some_id/complaints/some_id",
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

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
        status=403,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update complaint from draft to claim status",
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


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def bot_patch_tender_complaint(self):
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
    objection_data = deepcopy(test_tender_open_complaint_objection)
    objection_data["relatesTo"] = "tender"
    objection_data["relatedItem"] = self.tender_id
    complaint_data["objections"] = [objection_data, objection_data]
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
    self.assertEqual(response.json["data"]["objections"][0]["sequenceNumber"], 1)
    self.assertEqual(response.json["data"]["objections"][1]["sequenceNumber"], 2)


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def bot_patch_tender_complaint_mistaken(self):
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
    objection_data = deepcopy(test_tender_open_complaint_objection)
    objection_data["relatesTo"] = "tender"
    objection_data["relatedItem"] = self.tender_id
    complaint_data["objections"] = [objection_data, objection_data]
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
        self.assertEqual(response.json["data"]["objections"][0]["sequenceNumber"], 1)
        self.assertEqual(response.json["data"]["objections"][1]["sequenceNumber"], 2)


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() + timedelta(days=1))
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
            {"data": complaint_data},
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
                data.update(
                    {
                        "reviewDate": now.isoformat(),
                        "reviewPlace": "some",
                    }
                )
            response = self.app.patch_json(
                "/tenders/{}/complaints/{}".format(self.tender_id, complaint["id"]), {"data": data}
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
                data.update(
                    {
                        "reviewDate": now.isoformat(),
                        "reviewPlace": "some",
                    }
                )

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
                data.update({"rejectReason": "tenderCancelled", "rejectReasonDescription": "reject reason description"})

        response = self.app.patch_json(
            "/tenders/{}/complaints/{}".format(self.tender_id, complaint["id"]), {"data": data}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], status)


@patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
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
        self.assertEqual(
            response.json["errors"][0]["description"],
            f"Can't update complaint from mistaken to {status_data['status']} status",
        )

    bad_statuses = [
        {"status": "claim"},
        {"status": "answered", "resolutionType": "invalid"},
    ]

    for status_data in bad_statuses:
        self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint_id, owner_token),
            {"data": status_data},
            status=403,
        )

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
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update complaint from pending to mistaken status"
    )


def review_tender_stopping_complaint(self):
    if get_now() < RELEASE_2020_04_19:
        for status in ["satisfied", "stopped", "declined", "mistaken", "invalid"]:
            self.app.authorization = ("Basic", ("broker", ""))

            complaint_data = deepcopy(test_tender_below_complaint)
            complaint_data["author"] = getattr(self, "test_author", test_tender_below_author)
            response = self.app.post_json(
                "/tenders/{}/complaints".format(self.tender_id),
                {"data": complaint_data},
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
                data.update({"rejectReason": "tenderCancelled", "rejectReasonDescription": "reject reason description"})
            response = self.app.patch_json(url_patch_complaint, {"data": data})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], status)
            self.assertEqual(response.json["data"]["decision"], "decision")
    else:
        pass
        # This test exist in patch_tender_complaint method


def put_tender_complaint_document(self):
    response = self.app.post_json(
        "/tenders/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.complaint_id, self.complaint_owner_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put_json(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")

    response = self.app.put_json(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
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

    response = self.app.put_json(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
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

    with patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1)):
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.complaint_id, self.complaint_owner_token
            ),
            {"data": {"status": "pending"}},
            status=403,
        )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Can't update complaint from draft to pending status",
                }
            ],
        },
    )

    with patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() + timedelta(days=1)):
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.complaint_id, self.complaint_owner_token
            ),
            {"data": {"status": "pending"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.put_json(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.set_status("complete")

    response = self.app.put_json(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
    )


def patch_tender_complaint_document(self):
    response = self.app.post_json(
        "/tenders/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.complaint_id, self.complaint_owner_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
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

    with patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() + timedelta(days=1)):
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.complaint_id, self.complaint_owner_token
            ),
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


def create_complaint_objection_validation(self):
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["objections"] = []
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Please provide at least 1 item."],
    )

    complaint_data["objections"] = [{}]
    response = self.create_complaint(complaint_data, status=422)
    required_fields = response.json["errors"][0]["description"][0].keys()
    self.assertIn("title", required_fields)
    self.assertIn("relatesTo", required_fields)
    self.assertIn("relatedItem", required_fields)
    self.assertIn("classification", required_fields)
    self.assertIn("requestedRemedies", required_fields)
    self.assertIn("arguments", required_fields)

    invalid_objection_data = deepcopy(test_tender_open_complaint_objection)
    invalid_objection_data["relatesTo"] = "test"
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    values = "['tender', 'lot']" if self.complaint_on == "tender" else f"['{self.complaint_on}']"

    self.assertEqual(response.json["errors"][0]["description"][0]["relatesTo"], [f"Value must be one of {values}."])

    invalid_objection_data["relatesTo"] = "cancellation" if self.complaint_on != "cancellation" else "award"
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    values = "['tender', 'lot']" if self.complaint_on == "tender" else f"['{self.complaint_on}']"

    self.assertEqual(response.json["errors"][0]["description"][0]["relatesTo"], [f"Value must be one of {values}."])

    if self.complaint_on != "tender":
        invalid_objection_data["relatesTo"] = self.complaint_on
        invalid_objection_data["relatedItem"] = self.tender_id
        complaint_data["objections"] = [invalid_objection_data]
        response = self.create_complaint(complaint_data, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"][0]["description"][0]["relatedItem"],
            [f"Invalid {self.complaint_on} id"],
        )
    else:
        invalid_objection_data["relatesTo"] = self.complaint_on
        invalid_objection_data["relatedItem"] = "121"
        complaint_data["objections"] = [invalid_objection_data]
        response = self.create_complaint(complaint_data, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"][0]["description"][0]["relatedItem"],
            ["Invalid tender id"],
        )

    invalid_objection_data = deepcopy(test_tender_open_complaint_objection)
    invalid_objection_data["classification"] = {}
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"][0]["classification"],
        {
            "scheme": ["This field is required."],
            "id": ["This field is required."],
            "description": ["This field is required."],
        },
    )

    invalid_objection_data = deepcopy(test_tender_open_complaint_objection)
    invalid_objection_data["requestedRemedies"] = []
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"][0]["requestedRemedies"],
        ["Please provide at least 1 item."],
    )

    invalid_objection_data = deepcopy(test_tender_open_complaint_objection)
    invalid_objection_data["requestedRemedies"][0]["type"] = "test"
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"][0]["requestedRemedies"],
        [{"type": [f"Value must be one of {REQUESTED_REMEDIES_TYPES}"]}],
    )

    invalid_objection_data = deepcopy(test_tender_open_complaint_objection)
    invalid_objection_data["arguments"] = []
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"][0]["arguments"],
        ["Please provide at least 1 item."],
    )

    invalid_objection_data["arguments"] = [
        test_tender_open_complaint_objection["arguments"][0],
        test_tender_open_complaint_objection["arguments"][0],
    ]
    invalid_objection_data["relatesTo"] = self.complaint_on
    invalid_objection_data["relatedItem"] = self.tender_id
    if self.complaint_on != "tender":
        obj_id = getattr(self, f"{self.complaint_on}_id")
        invalid_objection_data["relatedItem"] = obj_id
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertIn(
        "Can't add more than 1 argument for objection",
        response.json["errors"][0]["description"],
    )

    invalid_objection_data["arguments"] = [{}]
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    required_fields = response.json["errors"][0]["description"][0]["arguments"][0].keys()
    self.assertIn("description", required_fields)

    invalid_objection_data = deepcopy(test_tender_open_complaint_objection)
    invalid_objection_data["classification"]["scheme"] = "test"
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"][0]["classification"]["scheme"],
        ["Value must be one of ['article_16', 'article_17', 'other', 'violation_amcu', 'amcu', 'amcu_24']."],
    )

    invalid_objection_data["classification"]["scheme"] = "article_16"
    invalid_objection_data["classification"]["id"] = "test"
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"][0]["classification"]["id"],
        ["Value must be one of article_16 reasons"],
    )


def patch_complaint_objection(self):
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["objections"] = [test_tender_open_complaint_objection]
    response = self.create_complaint(complaint_data, with_valid_relates_to=True)
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]
    complaint_token = response.json["access"]["token"]
    objection_id = response.json["data"]["objections"][0]["id"]
    objection_data = deepcopy(test_tender_open_complaint_objection)
    objection_data["id"] = objection_id
    objection_data["description"] = "Updated one"
    objection_data["arguments"][0]["evidences"] = []
    objection_data["relatesTo"] = self.complaint_on
    objection_data["relatedItem"] = self.tender_id
    if self.complaint_on != "tender":
        obj_id = getattr(self, f"{self.complaint_on}_id")
        objection_data["relatedItem"] = obj_id
    complaint_data = {"objections": [objection_data]}
    response = self.patch_complaint(complaint_id, complaint_data, complaint_token)
    self.assertEqual(response.status, "200 OK")
    objection = response.json["data"]["objections"][0]
    self.assertEqual(objection["id"], objection_id)
    self.assertEqual(objection["description"], "Updated one")
    self.assertNotIn("evidences", objection["arguments"][0])

    del objection_data["id"]
    objection_data["description"] = None
    complaint_data = {"objections": [objection_data]}
    response = self.patch_complaint(complaint_id, complaint_data, complaint_token)
    self.assertEqual(response.status, "200 OK")
    objection = response.json["data"]["objections"][0]
    self.assertNotEqual(objection["id"], objection_id)
    self.assertNotIn("description", objection)


def objection_related_document_of_evidence(self):
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["objections"] = [test_tender_open_complaint_objection]
    response = self.create_complaint(complaint_data, with_valid_relates_to=True)
    self.assertEqual(response.status, "201 Created")
    complaint_id = response.json["data"]["id"]
    complaint_token = response.json["access"]["token"]
    objection_id = response.json["data"]["objections"][0]["id"]

    # add document to complaint
    response = self.add_complaint_document(complaint_id, complaint_token)
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]

    # patch complaint
    objection_data = deepcopy(test_tender_open_complaint_objection)
    objection_data["id"] = objection_id
    objection_data["arguments"][0]["evidences"] = [
        {
            "title": "test",
            "description": "test",
        }
    ]
    objection_data["relatesTo"] = self.complaint_on
    objection_data["relatedItem"] = self.tender_id
    if self.complaint_on != "tender":
        obj_id = getattr(self, f"{self.complaint_on}_id")
        objection_data["relatedItem"] = obj_id
    complaint_data = {"objections": [objection_data]}
    response = self.patch_complaint(complaint_id, complaint_data, complaint_token, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [{"arguments": [{"evidences": [{"relatedDocument": ["This field is required."]}]}]}],
    )

    objection_data["arguments"][0]["evidences"][0]["relatedDocument"] = "some_id"
    complaint_data = {"objections": [objection_data]}
    response = self.patch_complaint(complaint_id, complaint_data, complaint_token, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [
            {
                "arguments": [
                    {"evidences": [{"relatedDocument": ["relatedDocument should be one of complaint documents"]}]}
                ]
            }
        ],
    )

    objection_data["arguments"][0]["evidences"][0]["relatedDocument"] = doc_id
    complaint_data = {"objections": [objection_data]}
    response = self.patch_complaint(complaint_id, complaint_data, complaint_token)
    self.assertEqual(response.status, "200 OK")
    objection = response.json["data"]["objections"][0]
    self.assertEqual(objection["id"], objection_id)

    # create complaint already with document and indicated relatedDocument in evidences in one POST
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    doc_id = uuid4().hex
    complaint_data["documents"] = [
        {
            "id": doc_id,
            "title": "Evidence_Attachment.pdf",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/pdf",
        }
    ]
    objection = deepcopy(test_tender_open_complaint_objection)
    objection["arguments"][0]["evidences"] = [
        {
            "title": "Evidence",
            "description": "Test evidence",
            "relatedDocument": doc_id,
        }
    ]
    complaint_data["objections"] = [objection]
    response = self.create_complaint(complaint_data, with_valid_relates_to=True)
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(
        response.json["data"]["documents"][0]["id"],
        response.json["data"]["objections"][0]["arguments"][0]["evidences"][0]["relatedDocument"],
    )


def objection_related_item_equals_related_lot(self):
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    complaint_data["relatedLot"] = self.initial_data["lots"][0]["id"]
    invalid_objection_data = deepcopy(test_tender_open_complaint_objection)
    invalid_objection_data["relatesTo"] = "lot"
    invalid_objection_data["relatedItem"] = self.initial_data['lots'][1]['id']
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [
            {
                "relatedItem": [
                    "Complaint's objection must relate to the same lot id as mentioned in complaint's relatedLot"
                ]
            }
        ],
    )
    invalid_objection_data["relatedItem"] = self.initial_data['lots'][0]['id']
    response = self.create_complaint(complaint_data)
    self.assertEqual(response.status, "201 Created")

    # relatesTo = tender and relatedLot is mentioned
    invalid_objection_data["relatesTo"] = "tender"
    invalid_objection_data["relatedItem"] = self.tender_id
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [{"relatedItem": ["Complaint's objection must not relate to tender if relatedLot mentioned"]}],
    )

    # relatesTo = tender and relatedLot is not mentioned
    del complaint_data["relatedLot"]
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data)
    self.assertEqual(response.status, "201 Created")

    # relatesTo = lot and relatedLot is not mentioned
    invalid_objection_data["relatesTo"] = "lot"
    invalid_objection_data["relatedItem"] = self.initial_data['lots'][1]['id']
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [
            {
                "relatedItem": [
                    "Complaint's objection must relate to the same lot id as mentioned in complaint's relatedLot"
                ]
            }
        ],
    )


def objection_related_item_equals_related_cancellation(self):
    cancellation_id_1 = self.cancellation_id

    # create second cancellation
    self.create_cancellation(related_lot=self.initial_data["lots"][1]["id"])
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    invalid_objection_data = deepcopy(test_tender_open_complaint_objection)
    invalid_objection_data["relatesTo"] = "cancellation"

    # create complaint for cancellation 2 with cancellation 1 related item
    invalid_objection_data["relatedItem"] = cancellation_id_1
    complaint_data["objections"] = [invalid_objection_data]
    response = self.create_complaint(complaint_data, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Complaint's objection must relate to the same cancellation id as complaint relates to",
    )
    # create complaint for cancellation 2 with cancellation 2 related item
    invalid_objection_data["relatedItem"] = self.cancellation_id
    response = self.create_complaint(complaint_data)
    self.assertEqual(response.status, "201 Created")


def objection_related_award_statuses(self):
    with change_auth(self.app, ("Basic", ("token", ""))):
        self.app.patch_json(f"/tenders/{self.tender_id}/awards/{self.award_id}", {"data": {"status": "cancelled"}})
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    objection_data = deepcopy(test_tender_open_complaint_objection)
    objection_data["relatesTo"] = "award"
    objection_data["relatedItem"] = self.award_id
    complaint_data["objections"] = [objection_data]

    url = (
        f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints"
        f"?acc_token={list(self.initial_bids_tokens.values())[0]}"
    )
    response = self.app.post_json(url, {"data": complaint_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [{"relatedItem": ["Relate objection to award in cancelled is forbidden"]}],
    )

    response = self.app.get(f"/tenders/{self.tender_id}/awards")
    pending_award_id = response.json["data"][-1]["id"]
    objection_data["relatedItem"] = pending_award_id
    complaint_data["objections"] = [objection_data]

    url = (
        f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints"
        f"?acc_token={list(self.initial_bids_tokens.values())[0]}"
    )
    response = self.app.post_json(url, {"data": complaint_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        [{"relatedItem": ["Relate objection to award in pending is forbidden"]}],
    )
