# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now
from datetime import timedelta
from copy import deepcopy
from mock import patch
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_claim,
    test_tender_below_claim,
    test_tender_below_author
)


def create_tender_complaint_invalid(self):
    response = self.app.post_json(
        "/tenders/some_id/complaints",
        {"data": test_tender_below_draft_claim},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )
    request_path = "/tenders/{}/complaints".format(self.tender_id)

    response = self.app.post(request_path, {"data": test_tender_below_draft_claim}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Expecting value: line 1 column 1 (char 0)", "location": "body", "name": "data"}],
    )

    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Expecting value: line 1 column 1 (char 0)", "location": "body", "name": "data"}],
    )

    response = self.app.post_json(request_path, "data", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"not_data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {"description": ["This field is required."], "location": "body", "name": "author"},
            {"description": ["This field is required."], "location": "body", "name": "title"},
        ],
    )

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"author": {"identifier": "invalid_value"}}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {
                    "identifier": ["Please use a mapping for this field or Identifier instance instead of str."]
                },
                "location": "body",
                "name": "author",
            }
        ],
    )

    claim_data = deepcopy(test_tender_below_draft_claim)
    claim_data["author"] = {"identifier": {}}
    response = self.app.post_json(
        request_path,
        {"data": claim_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {
                    "contactPoint": ["This field is required."],
                    "identifier": {"scheme": ["This field is required."], "id": ["This field is required."]},
                    "name": ["This field is required."],
                    "address": ["This field is required."],
                },
                "location": "body",
                "name": "author",
            }
        ],
    )
    claim_data["author"] = {"name": "name", "identifier": {"uri": "invalid_value"}}
    response = self.app.post_json(
        request_path,
        {
            "data": claim_data
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {
                    "contactPoint": ["This field is required."],
                    "identifier": {
                        "scheme": ["This field is required."],
                        "id": ["This field is required."],
                        "uri": ["Not a well formed URL."],
                    },
                    "address": ["This field is required."],
                },
                "location": "body",
                "name": "author",
            }
        ],
    )

    claim_data = deepcopy(test_tender_below_draft_claim)
    claim_data["relatedLot"] = "0" * 32
    response = self.app.post_json(
        request_path,
        {
            "data": claim_data
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["relatedLot should be one of lots"], "location": "body", "name": "relatedLot"}],
    )

    claim_data = deepcopy(test_tender_below_draft_claim)
    del claim_data["type"]
    with patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1)):
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": claim_data
            },
            status=422
        )
        self.assertEqual(
            response.json,
            {'status': 'error',
             'errors': [{'description': ['This field is required'],
                          'location': 'body', 'name': 'type'}]}
        )

    response = self.app.get("/tenders/{}".format(self.tender_id))
    if response.json["data"]["procurementMethodType"] == "belowThreshold":
        claim_data["type"] = "complaint"
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": claim_data
            },
            status=404
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "text/plain")


def create_tender_complaint(self):
    with patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() - timedelta(days=1)):
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": test_tender_below_claim
            },
        )

        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    with patch("openprocurement.tender.core.models.RELEASE_2020_04_19", get_now() + timedelta(days=1)):
        claim_data = deepcopy(test_tender_below_claim)
        del claim_data["type"]
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": claim_data
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    complaint = response.json["data"]
    status_date = response.json["data"]["date"]
    owner_token = response.json["access"]["token"]
    self.assertEqual(complaint["author"]["name"], self.test_author["name"])
    self.assertIn("id", complaint)
    self.assertIn(complaint["id"], response.headers["Location"])

    self.assertIn("transfer", response.json["access"])
    self.assertNotIn("transfer_token", response.json["data"])

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["status"] = "active.awarded"
    tender["awardPeriod"] = {"endDate": "2014-01-01"}
    self.mongodb.tenders.save(tender)

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
    self.assertNotEqual(response.json["data"]["date"], status_date)
    status_date = response.json["data"]["date"]
    self.assertEqual(response.json["data"]["resolutionType"], "invalid")
    self.assertEqual(response.json["data"]["resolution"], "spam 100% " * 3)

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"satisfied": True, "status": "resolved"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "resolved")
    self.assertNotEqual(response.json["data"]["date"], status_date)

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"status": "cancelled", "cancellationReason": "reason"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update complaint in current (resolved) status")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    self.set_status("active.tendering")

    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": test_tender_below_claim},
        status=403,
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint in current (active.tendering) tender status"
    )

    self.set_status("active.tendering", extra={"status": "active.enquiries"})

    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": test_tender_below_claim},
        status=403,
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can submit complaint only in enquiryPeriod"
    )

    self.set_status("unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": test_tender_below_claim},
        status=403,
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint in current (unsuccessful) tender status"
    )


def patch_tender_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": test_tender_below_draft_claim},
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

    self.set_status("active.auction")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
        {"data": {"resolution": "changing rules " * 2}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can update claim only before enquiryPeriod.clarificationsUntil"
            }
        ],
    )

    self.set_status("active.tendering")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
        {"data": {"resolution": "changing rules " * 2}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["resolution"], "changing rules " * 2)

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
        {"data": {"status": "answered", "resolutionType": "resolved", "resolution": "resolution text " * 2}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "answered")
    self.assertEqual(response.json["data"]["resolutionType"], "resolved")
    self.assertEqual(response.json["data"]["resolution"], "resolution text " * 2)

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"satisfied": False}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["satisfied"], False)

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"status": "cancelled", "cancellationReason": "reason"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertEqual(response.json["data"]["cancellationReason"], "reason")

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

    response = self.app.get("/tenders/{}/complaints/{}".format(self.tender_id, complaint["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")
    self.assertEqual(response.json["data"]["cancellationReason"], "reason")
    self.assertEqual(response.json["data"]["resolutionType"], "resolved")
    self.assertEqual(response.json["data"]["resolution"], "resolution text " * 2)

    self.set_status("active.enquiries")

    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": test_tender_below_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"status": "claim"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update complaint in current (complete) tender status"
    )


def patch_tender_complaint_without_clarifications_until(self):
    # old tenders doesn't have enquiryPeriod.clarificationsUntil

    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": test_tender_below_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
        {"data": {"status": "claim"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "claim")

    self.set_status("active.auction")

    tender = self.mongodb.tenders.get(self.tender_id)
    clarifications_until = tender["enquiryPeriod"].pop("clarificationsUntil")
    self.mongodb.tenders.save(tender)

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
        {"data": {"resolution": "changing rules " * 2}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


def review_tender_complaint(self):
    complaints = []
    for i in range(3):
        response = self.app.post_json(
            "/tenders/{}/complaints".format(self.tender_id),
            {
                "data": test_tender_below_claim
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        complaint = response.json["data"]
        owner_token = response.json["access"]["token"]
        complaints.append(complaint)

        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], self.tender_token),
            {"data": {"status": "answered", "resolutionType": "resolved", "resolution": "resolution text " * 2}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "answered")
        self.assertEqual(response.json["data"]["resolutionType"], "resolved")
        self.assertEqual(response.json["data"]["resolution"], "resolution text " * 2)

        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, complaint["id"], owner_token),
            {"data": {"satisfied": False, "status": "resolved"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "resolved")


def get_tender_complaint(self):
    claim_data = deepcopy(test_tender_below_draft_claim)
    claim_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": claim_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    del complaint["author"]

    response = self.app.get("/tenders/{}/complaints/{}".format(self.tender_id, complaint["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], complaint)

    self.assertNotIn("transfer_token", response.json["data"])

    response = self.app.get("/tenders/{}/complaints/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "complaint_id"}]
    )

    response = self.app.get("/tenders/some_id/complaints/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def get_tender_complaints(self):
    claim_data = deepcopy(test_tender_below_draft_claim)
    claim_data["author"] = getattr(self, "test_author", test_tender_below_author)
    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": claim_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    del complaint["author"]

    response = self.app.get("/tenders/{}/complaints".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0], complaint)

    response = self.app.get("/tenders/some_id/complaints", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


# TenderLotAwardComplaintResourceTest


def lot_award_create_tender_complaint(self):
    claim_data = deepcopy(test_tender_below_claim)
    claim_data["relatedLot"] = self.initial_lots[0]["id"]
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

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["status"] = "active.awarded"
    tender["awardPeriod"] = {"endDate": "2014-01-01"}
    self.mongodb.tenders.save(tender)

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

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.awarded")

    self.set_status("unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/complaints".format(self.tender_id),
        {"data": test_tender_below_draft_claim},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint in current (unsuccessful) tender status"
    )


# TenderComplaintDocumentResourceTest


def not_found(self):
    response = self.app.post_json(
        "/tenders/some_id/complaints/some_id/documents",
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.post(
        "/tenders/{}/complaints/some_id/documents".format(self.tender_id),
        status=404,
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "complaint_id"}]
    )

    response = self.app.get("/tenders/some_id/complaints/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.get("/tenders/{}/complaints/some_id/documents".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "complaint_id"}]
    )

    response = self.app.get("/tenders/some_id/complaints/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.get("/tenders/{}/complaints/some_id/documents/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "complaint_id"}]
    )

    response = self.app.get(
        "/tenders/{}/complaints/{}/documents/some_id".format(self.tender_id, self.complaint_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
    )


def create_tender_complaint_document(self):
    response = self.app.post(
        "/tenders/{}/complaints/{}/documents?acc_token={}".format(self.tender_id, self.complaint_id, self.tender_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document in current (draft) complaint status"
    )

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
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get("/tenders/{}/complaints/{}/documents".format(self.tender_id, self.complaint_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get("/tenders/{}/complaints/{}/documents?all=true".format(self.tender_id, self.complaint_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/complaints/{}/documents/{}?download=some_id".format(self.tender_id, self.complaint_id, doc_id),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}]
    )

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

    self.set_status("complete")

    response = self.app.post(
        "/tenders/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.complaint_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document in current (complete) tender status"
    )


def put_tender_complaint_document(self):
    response = self.app.post_json(
        "/tenders/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.complaint_id, self.complaint_owner_token
        ),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

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

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, self.complaint_id, self.complaint_owner_token),
        {"data": {"status": "claim"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "claim")

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
        response.json["errors"][0]["description"], "Can't update document in current (claim) complaint status"
    )

    self.set_status("complete")


def patch_tender_complaint_document(self):
    response = self.app.post_json(
        "/tenders/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.complaint_id, self.complaint_owner_token
        ),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
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

    response = self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, self.complaint_id, self.complaint_owner_token),
        {"data": {"status": "claim"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "claim")

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
        response.json["errors"][0]["description"], "Can't update document in current (claim) complaint status"
    )

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
