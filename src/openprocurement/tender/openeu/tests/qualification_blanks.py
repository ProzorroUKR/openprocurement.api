# -*- coding: utf-8 -*-
from copy import deepcopy

from datetime import timedelta

from mock import patch
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_cancellation, test_draft_claim, test_complaint, test_claim,
    test_draft_complaint,
)
from openprocurement.tender.core.tests.base import change_auth


# TenderQualificationResourceTest


def post_tender_qualifications(self):
    response = self.app.post_json("/tenders/{}/qualifications".format(self.tender_id), {"data": {}}, status=405)
    self.assertEqual(response.status, "405 Method Not Allowed")

    data = {"bidID": "some_id", "status": "pending"}
    response = self.app.post_json("/tenders/{}/qualifications".format(self.tender_id), {"data": data}, status=405)
    self.assertEqual(response.status, "405 Method Not Allowed")

    data = {"bidID": "1234" * 8, "status": "pending", "id": "12345678123456781234567812345678"}
    response = self.app.post_json("/tenders/{}/qualifications".format(self.tender_id), {"data": data}, status=405)
    self.assertEqual(response.status, "405 Method Not Allowed")

    data = {"bidID": "1234" * 8, "status": "pending", "id": "12345678123456781234567812345678"}
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}".format(self.tender_id, data["id"]), {"data": data}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")

    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    qualifications = response.json["data"]
    data = {"bidID": "1234" * 8, "status": "pending", "id": qualifications[0]["id"]}
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}".format(self.tender_id, qualifications[0]["id"]), {"data": data}, status=405
    )
    self.assertEqual(response.status, "405 Method Not Allowed")


def get_tender_qualifications_collection(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), self.min_bids_number)

    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualification_bid_ids = [q["bidID"] for q in qualifications]
    for bid in response.json["data"]:
        self.assertIn(bid["id"], qualification_bid_ids)
        qualification_bid_ids.remove(bid["id"])


def patch_tender_qualifications(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), self.min_bids_number)

    q1_id = qualifications[0]["id"]
    q2_id = qualifications[1]["id"]

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q1_id, self.tender_token),
        {"data": {"title": "title", "description": "description", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "title")
    self.assertEqual(response.json["data"]["description"], "description")
    self.assertEqual(response.json["data"]["qualified"], True)
    self.assertEqual(response.json["data"]["eligible"], True)
    self.assertEqual(response.json["data"]["date"], qualifications[0]["date"])

    # first qualification manipulations
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q1_id, self.tender_token),
        {
            "data": {
                "title": "title",
                "description": "description",
                "status": "active",
                "qualified": True,
                "eligible": True,
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotEqual(response.json["data"]["date"], qualifications[0]["date"])
    self.assertEqual(response.json["data"]["title"], "title")
    self.assertEqual(response.json["data"]["description"], "description")

    for status in ["pending", "unsuccessful"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q1_id, self.tender_token),
            {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json["errors"][0]["description"], "Can't update qualification status")

    ## activequalification can be cancelled
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q1_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    ## cancelled status is terminated
    for status in ["pending", "active", "unsuccessful"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q1_id, self.tender_token),
            {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update qualification in current cancelled qualification status",
        )

    # second qualification manipulations
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q2_id, self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    for status in ["pending", "active"]:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q2_id, self.tender_token),
            {"data": {"status": status, "qualified": True, "eligible": True}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json["errors"][0]["description"], "Can't update qualification status")

    ## unsuccessful qualification can be cancelled
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q2_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # list for new qualification
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), self.min_bids_number + 2)
    q1 = qualifications[0]
    q3 = qualifications[self.min_bids_number]
    self.assertEqual(q1["bidID"], q3["bidID"])
    q2 = qualifications[1]
    q4 = qualifications[self.min_bids_number + 1]
    self.assertEqual(q2["bidID"], q4["bidID"])

    self.assertEqual(q3["status"], "pending")

    # cancel pending qualification
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q3["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # one more qualification should be generated
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), self.min_bids_number + 3)
    self.assertEqual(q3["bidID"], qualifications[self.min_bids_number]["bidID"])
    # activate rest qualifications
    for q_id in (qualifications[self.min_bids_number + 1]["id"], qualifications[self.min_bids_number + 2]["id"]):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, q_id, self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active")


def get_tender_qualifications(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json["data"]
    for qualification in qualifications:
        response = self.app.get(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token)
        )
        self.assertEqual(response.status, "200 OK")


def patch_tender_qualifications_after_status_change(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "200 OK")
    qualifications = response.json["data"]
    for qualification in qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": u"Can't update qualification in current (active.pre-qualification.stand-still) tender status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )


# Tender2LotQualificationResourceTest


def lot_patch_tender_qualifications(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualifications[2]["id"], self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualifications[1]["id"], self.tender_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualifications[0]["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")


def lot_patch_tender_qualifications_lots_none(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"lots": [None]}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")

    errors = {error["name"]: error["description"] for error in response.json["errors"]}
    self.assertEqual(errors["lots"][0], ["This field is required."])
    self.assertEqual(errors["qualifications"][0], {"lotID": ["lotID should be one of lots"]})


def lot_get_tender_qualifications_collection(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), self.min_bids_number * 2)

    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualification_lots_ids = [q["lotID"] for q in qualifications]
    for bid in response.json["data"]:
        response = self.app.get(
            "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid["id"], self.initial_bids_tokens[bid["id"]])
        )
        for lotV in response.json["data"]["lotValues"]:
            lot_id = lotV["relatedLot"]
            self.assertIn(lot_id, qualification_lots_ids)
            qualification_lots_ids.remove(lot_id)


def tender_qualification_cancelled(self):
    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    qualification_id = qualifications[0]["id"]
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": u"Can't update qualification in current cancelled qualification status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )

    response = self.app.get("/tenders/{}/qualifications".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")

    new_qualifications = response.json["data"]
    self.assertEqual(len(new_qualifications), self.min_bids_number * 2 + 1)


# TenderQualificationDocumentResourceTest


def not_found(self):
    self.app.authorization = ("Basic", ("bot", "bot"))
    response = self.app.post(
        "/tenders/some_id/qualifications/some_id/documents", status=404, upload_files=[("file", "name.doc", "content")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.post(
        "/tenders/{}/qualifications/some_id/documents".format(self.tender_id),
        status=404,
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.post(
        "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
        status=404,
        upload_files=[("invalid_value", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])

    response = self.app.get("/tenders/some_id/qualifications/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.get("/tenders/{}/qualifications/some_id/documents".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.get(
        "/tenders/some_id/qualifications/some_id/documents/some_id".format(self.tender_token), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.get(
        "/tenders/{}/qualifications/some_id/documents/some_id".format(self.tender_id, self.tender_token), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/some_id".format(self.tender_id, self.qualifications[0]["id"]),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )

    response = self.app.put(
        "/tenders/some_id/qualifications/some_id/documents/some_id",
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.put(
        "/tenders/{}/qualifications/some_id/documents/some_id".format(self.tender_id),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.put(
        "/tenders/{}/qualifications/{}/documents/some_id".format(self.tender_id, self.qualifications[0]["id"]),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )

    self.app.authorization = ("Basic", ("invalid", ""))
    response = self.app.put(
        "/tenders/{}/qualifications/{}/documents/some_id?acc_token={}".format(
            self.tender_id, self.qualifications[0]["id"], self.tender_token
        ),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )


def tender_owner_create_qualification_document(self):
    response = self.app.post(
        "/tenders/{}/qualifications/{}/documents?acc_token={}".format(
            self.tender_id, self.qualifications[0]["id"], self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])


def create_qualification_document(self):
    self.app.authorization = ("Basic", ("bot", "bot"))
    response = self.app.post(
        "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = response.json["data"]["url"].split("?")[-1]

    # qualifications are public
    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"])
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents?all=true".format(self.tender_id, self.qualifications[0]["id"])
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}?download=some_id".format(
            self.tender_id, self.qualifications[0]["id"], doc_id
        ),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
    )

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}?{}".format(
            self.tender_id, self.qualifications[0]["id"], doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, "content")

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])


def put_qualification_document(self):
    self.app.authorization = ("Basic", ("bot", "bot"))

    response = self.app.post(
        "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        status=404,
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])

    response = self.app.put(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}?{}".format(
            self.tender_id, self.qualifications[0]["id"], doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, "content2")

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        "content3",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}?{}".format(
            self.tender_id, self.qualifications[0]["id"], doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, "content3")

    with change_auth(self.app, ("Basic", ("broker", "broker"))):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(
                self.tender_id, self.qualifications[0]["id"], self.tender_token
            ),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        upload_files=[("file", "name.doc", "content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can't update document in current qualification status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )


def patch_qualification_document(self):
    self.app.authorization = ("Basic", ("bot", "bot"))

    response = self.app.post(
        "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        {"data": {"documentOf": "lot"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"relatedItem"}],
    )

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        {"data": {"documentOf": "lot", "relatedItem": "0" * 32}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"relatedItem should be one of lots"], u"location": u"body", u"name": u"relatedItem"}],
    )

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    with change_auth(self.app, ("Basic", ("broker", "broker"))):
        for qualification in self.qualifications:
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}?acc_token={}".format(
                    self.tender_id, qualification["id"], self.tender_token
                ),
                {"data": {"status": "active", "qualified": True, "eligible": True}},
            )
            self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualifications[0]["id"], doc_id, self.tender_token
        ),
        {"data": {"description": "document description2"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't update document in current qualification status"}],
    )

    with change_auth(self.app, ("Basic", ("broker", "broker"))):
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"status": "active.pre-qualification.stand-still"}},
        )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
        {"data": {"description": "document description2"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update document in current (active.pre-qualification.stand-still) tender status",
            }
        ],
    )


def create_qualification_document_after_status_change(self):
    for i in range(self.min_bids_number - 1):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(
                self.tender_id, self.qualifications[i]["id"], self.tender_token
            ),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")

    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.post(
            "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
            upload_files=[("file", "name.doc", "content")],
            status=403,
        )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can't add document in current qualification status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(
            self.tender_id, self.qualifications[-1]["id"], self.tender_token
        ),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")

    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.post(
            "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[-1]["id"]),
            upload_files=[("file", "name.doc", "content")],
            status=403,
        )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can't add document in current qualification status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(
            self.tender_id, self.qualifications[-1]["id"], self.tender_token
        ),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.post(
            "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[-1]["id"]),
            upload_files=[("file", "name.doc", "content")],
            status=403,
        )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can't add document in current qualification status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.status, "200 OK")
    self.qualifications = response.json["data"]
    self.assertEqual(len(self.qualifications), self.min_bids_number + 1)

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(
            self.tender_id, self.qualifications[self.min_bids_number]["id"], self.tender_token
        ),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")

    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.post(
            "/tenders/{}/qualifications/{}/documents".format(
                self.tender_id, self.qualifications[self.min_bids_number]["id"]
            ),
            upload_files=[("file", "name.doc", "content")],
            status=403,
        )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": u"Can't add document in current (active.pre-qualification.stand-still) tender status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )


def put_qualification_document_after_status_change(self):
    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.post(
            "/tenders/{}/qualifications/{}/documents".format(self.tender_id, self.qualifications[0]["id"]),
            upload_files=[("file", "name.doc", "content")],
        )
    self.assertEqual(response.status, "201 Created")
    doc_id = response.json["data"]["id"]

    for qualification in self.qualifications:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": "active", "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")

    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.put(
            "/tenders/{}/qualifications/{}/documents/{}".format(self.tender_id, self.qualifications[0]["id"], doc_id),
            upload_files=[("file", "name.doc", "content2")],
            status=403,
        )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": u"Can't update document in current (active.pre-qualification.stand-still) tender status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )


# TenderQualificationComplaintResourceTest


def create_tender_qualification_complaint_invalid(self):
    response = self.app.post_json(
        "/tenders/some_id/qualifications/some_id/complaints",
        {"data": test_draft_claim},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    request_path = "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
        self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
    )

    response = self.app.post(request_path, "data", status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Content-Type header should be one of ['application/json']",
                u"location": u"header",
                u"name": u"Content-Type",
            }
        ],
    )

    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"No JSON object could be decoded", u"location": u"body", u"name": u"data"}],
    )

    response = self.app.post_json(request_path, "data", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Data not available", u"location": u"body", u"name": u"data"}]
    )

    response = self.app.post_json(request_path, {"not_data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Data not available", u"location": u"body", u"name": u"data"}]
    )

    response = self.app.post_json(request_path, {"data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {u"description": [u"This field is required."], u"location": u"body", u"name": u"author"},
            {u"description": [u"This field is required."], u"location": u"body", u"name": u"title"},
        ],
    )

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"author": {"identifier": "invalid_value"}}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {
                    u"identifier": [u"Please use a mapping for this field or ComplaintIdentifier instance instead of unicode."]
                },
                u"location": u"body",
                u"name": u"author",
            }
        ],
    )


def create_tender_qualification_complaint(self):
    complaint_data = deepcopy(test_draft_complaint)
    complaint_data['status'] = "claim"
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {
            "data": complaint_data
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["status"], "draft")

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {
            "data": test_complaint
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    complaint_token = response.json["access"]["token"]
    self.assertIn("id", complaint)
    self.assertIn(complaint["id"], response.headers["Location"])
    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(complaint["author"]["name"], self.author_data["name"])

    else:
        self.assertEqual(response.json["data"]["status"], "draft")

        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                    self.tender_id, self.qualification_id, complaint["id"], complaint_token),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], "pending")

    self.set_status("unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": test_draft_claim},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint in current (unsuccessful) tender status"
    )


def patch_tender_qualification_complaint(self):
    complaint_data = deepcopy(test_draft_complaint)
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], owner_token
            ),
            {"data": {"status": "cancelled", "cancellationReason": "reason"}},
            status=200,
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "cancelled")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")
    else:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], owner_token
            ),
            {"data": {"status": "cancelled", "cancellationReason": "reason"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"],
                         "Can't update complaint from draft to cancelled status")

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": test_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, complaint["id"], self.tender_token
        ),
        {"data": {"status": "cancelled", "cancellationReason": "reason"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, complaint["id"], owner_token
        ),
        {"data": {"title": "claim title"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "claim title")

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}/complaints/{}".format(
                    self.tender_id, self.qualification_id, complaint["id"]
                ),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/some_id/qualifications/some_id/complaints/some_id",
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.patch_json(
        "/tenders/{}/qualifications/some_id/complaints/some_id".format(self.tender_id),
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/some_id".format(self.tender_id, self.qualification_id),
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"complaint_id"}]
    )
    #

    if RELEASE_2020_04_19 > get_now():
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], owner_token
            ),
            {"data": {"status": "stopping", "cancellationReason": "reason"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "stopping")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")

        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], owner_token
            ),
            {"data": {"status": "cancelled", "cancellationReason": "reason"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update complaint from stopping to cancelled status"
        )

        response = self.app.get(
            "/tenders/{}/qualifications/{}/complaints/{}".format(self.tender_id, self.qualification_id, complaint["id"])
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "stopping")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")
    else:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], owner_token
            ),
            {"data": {"status": "stopping", "cancellationReason": "reason"}},
            status=403,
        )

        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update complaint from pending to stopping status"
        )

    # create complaint
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": test_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, complaint["id"], owner_token
        ),
        {"data": {"status": "claim"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Can't update complaint from draft to claim status")

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, complaint["id"], owner_token
        ),
        {"data": {"status": "claim"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update complaint in current (complete) tender status"
    )


@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def bot_patch_tender_qualification_complaint(self):
    complaint_data = deepcopy(test_draft_complaint)
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.get("/tenders/{}".format(self.tender_id, self.tender_token))
    self.assertNotIn("owner_token", response.json["data"]["qualifications"][0]["complaints"][0])


@patch("openprocurement.tender.core.views.complaint.RELEASE_2020_04_19", get_now() + timedelta(days=1))
def bot_patch_tender_qualification_complaint_forbidden(self):
    complaint_data = deepcopy(test_draft_complaint)
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": complaint_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", ""))):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update complaint from draft to pending status"
        )


def review_tender_qualification_complaint(self):
    now = get_now()
    for status in ["invalid", "stopped", "declined", "satisfied"]:
        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.post_json(
            "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
                self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
            ),
            {
                "data": test_complaint
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        complaint = response.json["data"]
        complaint_token = response.json["access"]["token"]

        if RELEASE_2020_04_19 < now:
            self.assertEqual(response.json["data"]["status"], "draft")
            with change_auth(self.app, ("Basic", ("bot", ""))):
                response = self.app.patch_json(
                    "/tenders/{}/qualifications/{}/complaints/{}".format(
                        self.tender_id, self.qualification_id, complaint["id"]),
                    {"data": {"status": "pending"}},
                )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], "pending")

        self.app.authorization = ("Basic", ("reviewer", ""))
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}".format(
                self.tender_id, self.qualification_id, complaint["id"]
            ),
            {"data": {"decision": "{} complaint".format(status), "rejectReasonDescription": "reject reason"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["decision"], "{} complaint".format(status))
        self.assertEqual(response.json["data"]["rejectReasonDescription"], "reject reason")

        if status in ["declined", "satisfied", "stopped"]:
            data = {"status": "accepted"}
            if RELEASE_2020_04_19 < now:
                data.update({
                    "reviewDate": now.isoformat(),
                    "reviewPlace": "some",
                })
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}/complaints/{}".format(
                    self.tender_id, self.qualification_id, complaint["id"]
                ),
                {"data": data},
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
                "/tenders/{}/qualifications/{}/complaints/{}".format(
                    self.tender_id, self.qualification_id, complaint["id"]
                ),
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
            "/tenders/{}/qualifications/{}/complaints/{}".format(
                self.tender_id, self.qualification_id, complaint["id"]
            ),
            {"data": data},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], status)


def review_tender_qualification_stopping_complaint(self):
    if get_now() < RELEASE_2020_04_19:
        for status in ["stopped", "declined", "mistaken", "invalid", "satisfied"]:
            self.app.authorization = ("Basic", ("broker", ""))
            response = self.app.post_json(
                "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
                    self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
                ),
                {
                    "data": test_complaint
                },
            )
            self.assertEqual(response.status, "201 Created")
            self.assertEqual(response.content_type, "application/json")
            complaint = response.json["data"]
            owner_token = response.json["access"]["token"]

            url_patch_complaint = "/tenders/{}/qualifications/{}/complaints/{}".format(
                self.tender_id, self.qualification_id, complaint["id"]
            )

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
            response = self.app.patch_json(url_patch_complaint, {"data": data})
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], status)
            self.assertEqual(response.json["data"]["decision"], "decision")
        else:
            pass
        # This test exist in patch_tender_qualification_complaint method


def review_tender_award_claim(self):
    for status in ["invalid", "resolved", "declined"]:
        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.post_json(
            "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
                self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
            ),
            {
                "data": test_claim
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        complaint = response.json["data"]
        complaint_token = response.json["access"]["token"]

        self.app.authorization = ("Basic", ("broker", ""))
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], self.tender_token
            ),
            {
                "data": {
                    "status": "answered",
                    "resolutionType": status,
                    "resolution": "resolution text for {} status".format(status),
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["resolutionType"], status)

        self.app.authorization = ("Basic", ("token", ""))
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], complaint_token
            ),
            {"data": {"satisfied": "i" in status}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["satisfied"], "i" in status)


def get_tender_qualification_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": test_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}".format(self.tender_id, self.qualification_id, complaint["id"])
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], complaint)

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/some_id".format(self.tender_id, self.qualification_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"complaint_id"}]
    )

    response = self.app.get("/tenders/some_id/qualifications/some_id/complaints/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )


def get_tender_qualification_complaints(self):
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": test_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    response = self.app.get("/tenders/{}/qualifications/{}/complaints".format(self.tender_id, self.qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0], complaint)

    response = self.app.get("/tenders/some_id/qualifications/some_id/complaints", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    tender = self.db.get(self.tender_id)
    tender["qualificationPeriod"]["endDate"] = tender["qualificationPeriod"]["startDate"]
    self.db.save(tender)

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": test_draft_claim},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add complaint only in qualificationPeriod")


def change_status_to_standstill_with_complaint(self):
    auth = self.app.authorization
    now = get_now()
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {
            "data": test_complaint
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    complaint_token = response.json["access"]["token"]

    if RELEASE_2020_04_19 < now:
        self.assertEqual(response.json["data"]["status"], "draft")
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}/complaints/{}".format(
                    self.tender_id, self.qualification_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ("Basic", ("reviewer", ""))
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}".format(self.tender_id, self.qualification_id, complaint["id"]),
        {"data": {"decision": "{} complaint".format("accepted")}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["decision"], "{} complaint".format("accepted"))

    data = {"status": "accepted"}
    if RELEASE_2020_04_19 < now:
        data.update({
            "reviewDate": now.isoformat(),
            "reviewPlace": "some",
        })
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}".format(self.tender_id, self.qualification_id, complaint["id"]),
        {"data": data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "accepted")
    if RELEASE_2020_04_19 < now:
        self.assertEqual(response.json["data"]["reviewPlace"], "some")
        self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

    now = get_now()
    data = {"decision": "accepted:{} complaint".format("accepted")}
    if RELEASE_2020_04_19 > now:
        data.update({
            "reviewDate": now.isoformat(),
            "reviewPlace": "some",
        })
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}".format(self.tender_id, self.qualification_id, complaint["id"]),
        {"data": data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["decision"], "accepted:{} complaint".format("accepted"))
    if RELEASE_2020_04_19 > now:
        self.assertEqual(response.json["data"]["reviewPlace"], "some")
        self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}".format(self.tender_id, self.qualification_id, complaint["id"]),
        {"data": {"status": "satisfied"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "satisfied")

    self.app.authorization = auth

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": u"Can't switch to 'active.pre-qualification.stand-still' before resolve all complaints",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, complaint["id"], self.tender_token
        ),
        {"data": {"status": "resolved", "tendererAction": "Умови виправлено"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "resolved")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active.pre-qualification.stand-still")


# TenderLotQualificationComplaintResourceTest


def create_tender_lot_qualification_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {
            "data": test_complaint
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    complaint_token = response.json["access"]["token"]
    self.assertIn("id", complaint)
    self.assertIn(complaint["id"], response.headers["Location"])

    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(complaint["author"]["name"], self.author_data["name"])

    else:
        self.assertEqual(response.json["data"]["status"], "draft")

        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                    self.tender_id, self.qualification_id, complaint["id"], complaint_token),
                {"data": {"status": "pending"}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["status"], "pending")

    self.set_status("unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": test_draft_claim},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint in current (unsuccessful) tender status"
    )


def patch_tender_lot_qualification_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": test_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}/complaints/{}".format(
                    self.tender_id, self.qualification_id, complaint["id"]
                ),
                {"data": {"status": "pending"}},
            )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/some_id/qualifications/some_id/complaints/some_id",
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.patch_json(
        "/tenders/{}/qualifications/some_id/complaints/some_id".format(self.tender_id),
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/some_id".format(self.tender_id, self.qualification_id),
        {"data": {"status": "resolved", "resolution": "resolution text"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"complaint_id"}]
    )

    if RELEASE_2020_04_19 > get_now():
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], owner_token
            ),
            {"data": {"status": "stopping", "cancellationReason": "reason"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "stopping")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")

        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], owner_token
            ),
            {"data": {"status": "cancelled", "cancellationReason": "reason"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"],
            "Can't update complaint from stopping to cancelled status"
        )

        response = self.app.get(
            "/tenders/{}/qualifications/{}/complaints/{}".format(self.tender_id, self.qualification_id, complaint["id"])
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "stopping")
        self.assertEqual(response.json["data"]["cancellationReason"], "reason")
    else:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], owner_token
            ),
            {"data": {"status": "stopping", "cancellationReason": "reason"}},
            status=403,
        )

        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Can't update complaint from pending to stopping status"
        )

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": test_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, complaint["id"], owner_token
        ),
        {"data": {"status": "claim"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update complaint in current (complete) tender status"
    )


def get_tender_lot_qualification_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": test_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}".format(self.tender_id, self.qualification_id, complaint["id"])
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], complaint)

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/some_id".format(self.tender_id, self.qualification_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"complaint_id"}]
    )

    response = self.app.get("/tenders/some_id/qualifications/some_id/complaints/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )


def get_tender_lot_qualification_complaints(self):
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": test_draft_claim},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]

    response = self.app.get("/tenders/{}/qualifications/{}/complaints".format(self.tender_id, self.qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][0], complaint)

    response = self.app.get("/tenders/some_id/qualifications/some_id/complaints", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    tender = self.db.get(self.tender_id)
    tender["qualificationPeriod"]["endDate"] = tender["qualificationPeriod"]["startDate"]
    self.db.save(tender)

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {"data": test_draft_claim},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add complaint only in qualificationPeriod")


# Tender2LotQualificationComplaintResourceTest


def create_tender_2lot_qualification_complaint(self):
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
        ),
        {
            "data": test_complaint
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    complaint_token = response.json["access"]["token"]
    self.assertIn("id", complaint)
    self.assertIn(complaint["id"], response.headers["Location"])
    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(complaint["author"]["name"], self.author_data["name"])
    else:
        self.assertEqual(response.json["data"]["status"], "draft")
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                 "/tenders/{}/qualifications/{}/complaints/{}".format(
                     self.tender_id, self.qualification_id, complaint["id"]),
                 {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    # set complaint status invalid to be able to cancel the lot
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, complaint["id"], complaint_token
            ),
            {"data": {
                "status": "invalid",
                "rejectReason": "buyerViolationsCorrected"
            }},
        )
        self.assertEqual(response.status, "200 OK")

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })

    if RELEASE_2020_04_19 < get_now():
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"][0]["description"],
            u"Cancellation can't be add when exists active complaint period"
        )

    else:
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
        )
        self.assertEqual(response.status, "201 Created")

        response = self.app.post_json(
            "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
                self.tender_id, self.qualification_id, self.initial_bids_tokens.values()[0]
            ),
            {"data": test_draft_claim},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Can add complaint only in active lot status")


# Tender2LotQualificationClaimResourceTest


def create_tender_qualification_claim(self):
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.unsuccessful_qualification_id, self.initial_bids_tokens[self.initial_bids[0]["id"]]
        ),
        {
            "data": test_claim
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can add claim only on unsuccessful qualification of your bid",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(
            self.tender_id, self.unsuccessful_qualification_id, self.initial_bids_tokens[self.initial_bids[0]["id"]]
        ),
        {
            "data": test_draft_claim
        },
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.unsuccessful_qualification_id, complaint["id"], owner_token
        ),
        {"data": {"status": "claim"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can add claim only on unsuccessful qualification of your bid",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )


# TenderQualificationComplaintDocumentResourceTest


def complaint_not_found(self):
    response = self.app.post(
        "/tenders/some_id/qualifications/some_id/complaints/some_id/documents",
        status=404,
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.post(
        "/tenders/{}/qualifications/some_id/complaints/some_id/documents".format(self.tender_id),
        status=404,
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.post(
        "/tenders/{}/qualifications/{}/complaints/some_id/documents".format(self.tender_id, self.qualification_id),
        status=404,
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"complaint_id"}]
    )

    response = self.app.post(
        "/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.complaint_owner_token
        ),
        status=404,
        upload_files=[("invalid_value", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])

    response = self.app.get("/tenders/some_id/qualifications/some_id/complaints/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.get(
        "/tenders/{}/qualifications/some_id/complaints/some_id/documents".format(self.tender_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/some_id/documents".format(self.tender_id, self.qualification_id),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"complaint_id"}]
    )

    response = self.app.get("/tenders/some_id/qualifications/some_id/complaints/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.get(
        "/tenders/{}/qualifications/some_id/complaints/some_id/documents/some_id".format(self.tender_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/some_id/documents/some_id".format(
            self.tender_id, self.qualification_id
        ),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"complaint_id"}]
    )

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/some_id".format(
            self.tender_id, self.qualification_id, self.complaint_id
        ),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )

    response = self.app.put(
        "/tenders/some_id/qualifications/some_id/complaints/some_id/documents/some_id",
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.put(
        "/tenders/{}/qualifications/some_id/complaints/some_id/documents/some_id".format(self.tender_id),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.put(
        "/tenders/{}/qualifications/{}/complaints/some_id/documents/some_id".format(
            self.tender_id, self.qualification_id
        ),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"complaint_id"}]
    )

    response = self.app.put(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/some_id".format(
            self.tender_id, self.qualification_id, self.complaint_id
        ),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )


def create_tender_qualification_complaint_document(self):
    response = self.app.post(
        "/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document in current (draft) complaint status"
    )

    response = self.app.post(
        "/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents".format(
            self.tender_id, self.qualification_id, self.complaint_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents?all=true".format(
            self.tender_id, self.qualification_id, self.complaint_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?download=some_id".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id
        ),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
    )

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, "content")

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    self.set_status("complete")

    response = self.app.post(
        "/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document in current (complete) tender status"
    )


def put_tender_qualification_complaint_document(self):
    response = self.app.post(
        "/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        status=404,
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])

    response = self.app.put(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content2")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")

    response = self.app.put(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, "content2")

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        "content3",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, "content3")

    self.set_status("complete")

    response = self.app.put(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", "content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
    )


def patch_tender_qualification_complaint_document(self):
    response = self.app.post(
        "/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, self.complaint_id, self.complaint_owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}/complaints/{}".format(
                    self.tender_id, self.qualification_id, self.complaint_id
                ),
                {"data": {"status": "pending"}},
            )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.put(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        "content2",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, "content2")

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
    )


# Tender2LotQualificationComplaintDocumentResourceTest


def create_tender_2lot_qualification_complaint_document(self):
    response = self.app.post(
        "/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document in current (draft) complaint status"
    )

    response = self.app.post(
        "/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents".format(
            self.tender_id, self.qualification_id, self.complaint_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents?all=true".format(
            self.tender_id, self.qualification_id, self.complaint_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?download=some_id".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id
        ),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
    )

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, "content")

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })

    if RELEASE_2020_04_19 < get_now():
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"][0]["description"],
            u"Cancellation can't be add when exists active complaint period"
        )
    else:
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
        )
        self.assertEqual(response.status, "201 Created")
        cancellation_id = response.json["data"]["id"]

        response = self.app.post(
            "/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}".format(
                self.tender_id, self.qualification_id, self.complaint_id, self.complaint_owner_token
            ),
            upload_files=[("file", "name.doc", "content")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Can add document only in active lot status")


def put_tender_2lot_qualification_complaint_document(self):
    response = self.app.post(
        "/tenders/{}/qualifications/{}/complaints/{}/documents?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        status=404,
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])

    response = self.app.put(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content2")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")

    response = self.app.put(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, "content2")

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        "content3",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, "content3")

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, self.complaint_id, self.complaint_owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/qualifications/{}/complaints/{}".format(
                    self.tender_id, self.qualification_id, self.complaint_id
                ),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.put(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        "content4",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?{}".format(
            self.tender_id, self.qualification_id, self.complaint_id, doc_id, key
        )
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, "content4")

    # set complaint status invalid to be able to cancel the lot
    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, self.complaint_id, self.complaint_owner_token
            ),
            {"data": {
                "status": "invalid",
                "rejectReason": "buyerViolationsCorrected"
            }},
        )
        self.assertEqual(response.status, "200 OK")

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })

    if RELEASE_2020_04_19 < get_now():
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"][0]["description"],
            u"Cancellation can't be add when exists active complaint period"
        )

    else:
        response = self.app.post_json(
            "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": cancellation},
        )
        self.assertEqual(response.status, "201 Created")

        response = self.app.put(
            "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.complaint_owner_token
            ),
            upload_files=[("file", "name.doc", "content3")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Can update document only in active lot status")

        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}/complaints/{}/documents/{}?acc_token={}".format(
                self.tender_id, self.qualification_id, self.complaint_id, doc_id, self.complaint_owner_token
            ),
            {"data": {"description": "document description"}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Can update document only in active lot status")


def switch_bid_status_unsuccessul_to_active(self):
    bid_id, bid_token = self.initial_bids_tokens.items()[0]

    response = self.app.get("/tenders/{}/qualifications?acc_token={}".format(self.tender_id, self.tender_token))
    self.assertEqual(response.content_type, "application/json")
    qualifications = response.json["data"]
    self.assertEqual(len(qualifications), 4)
    qualification_id = ""
    for qualification in qualifications:
        status = "active"
        if qualification["bidID"] == bid_id:
            status = "unsuccessful"
            qualification_id = qualification["id"]
        response = self.app.patch_json(
            "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification["id"], self.tender_token),
            {"data": {"status": status, "qualified": True, "eligible": True}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], status)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.pre-qualification.stand-still"}},
    )
    self.assertEqual(response.status, "200 OK")

    # create complaint
    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/complaints?acc_token={}".format(self.tender_id, qualification_id, bid_token),
        {
            "data": test_complaint
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    complaint = response.json["data"]
    complaint_token = response.json["access"]["token"]

    if RELEASE_2020_04_19 < get_now():
        self.assertEqual(response.json["data"]["status"], "draft")
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                 "/tenders/{}/qualifications/{}/complaints/{}".format(
                     self.tender_id, qualification_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "pending")

    self.app.authorization = ("Basic", ("reviewer", ""))
    now = get_now()
    data = {"status": "accepted"}
    if RELEASE_2020_04_19 < now:
        data.update({
            "reviewDate": now.isoformat(),
            "reviewPlace": "some",
        })
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}".format(self.tender_id, qualification_id, complaint["id"]),
        {"data": data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "accepted")
    if RELEASE_2020_04_19 < now:
        self.assertEqual(response.json["data"]["reviewPlace"], "some")
        self.assertEqual(response.json["data"]["reviewDate"], now.isoformat())

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/complaints/{}".format(self.tender_id, qualification_id, complaint["id"]),
        {"data": {"status": "satisfied"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "satisfied")

    # Cancel qualification
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, qualification_id, self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    new_qualification_id = response.headers["location"].split("/")[-1]
    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}?acc_token={}".format(self.tender_id, new_qualification_id, self.tender_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get("/tenders/{}/bids".format(self.tender_id))
    for b in response.json["data"]:
        self.assertEqual(b["status"], "active")


def create_qualification_requirement_response(self):
    self.app.authorization = ("Basic", ("broker", ""))

    base_request_path = "/tenders/{}/qualifications/{}/requirement_responses".format(
        self.tender_id, self.qualification_id)
    request_path = "{}?acc_token={}".format(base_request_path, self.tender_token)

    valid_data = [{
        "title": "Requirement response",
        "description": "some description",
        "requirement": {
            "id": self.requirement_id,
            "title": self.requirement_title,
        },
        "value": True,
    }]

    response = self.app.post_json(
        base_request_path,
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}]
    )

    response = self.app.post_json(
        "{}?acc_token={}".format(base_request_path, "some_random_token"),
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}]
    )

    response = self.app.post_json(
        request_path,
        {"data": [{"description": "some description"}]},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{u'description': {u'requirement': [u'This field is required.'], u'value': [u'This field is required.']},
          u'location': u'body',
          u'name': 0}]
    )

    response = self.app.post_json(request_path, {"data": valid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rr = response.json["data"]

    for i, rr_data in enumerate(valid_data):
        for k, v in rr_data.items():
            if k == "value":
                self.assertEqual(str(rr[i][k]), str(v))
            else:
                self.assertEqual(rr[i][k], v)


def patch_qualification_requirement_response(self):
    base_request_path = "/tenders/{}/qualifications/{}/requirement_responses".format(
        self.tender_id, self.qualification_id)
    request_path = "{}?acc_token={}".format(base_request_path, self.tender_token)

    valid_data = [{
        "title": "Requirement response",
        "description": "some description",
        "requirement": {
            "id": self.requirement_id,
            "title": self.requirement_title,
        },
        "value": "True"
    }]

    response = self.app.post_json(request_path, {"data": valid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rr_id = response.json["data"][0]["id"]

    base_request_path = "/tenders/{}/qualifications/{}/requirement_responses/{}".format(
        self.tender_id, self.qualification_id, rr_id)
    request_path = "{}?acc_token={}".format(base_request_path, self.tender_token)
    updated_data = {
        "title": "Rquirement response updated",
        "value": 100,
    }

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("broker", ""))

    response = self.app.patch_json(
        base_request_path,
        {"data": updated_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}]
    )

    response = self.app.patch_json(
        "{}?acc_token={}".format(base_request_path, "some_random_token"),
        {"data": updated_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}]
    )

    self.app.authorization = auth
    response = self.app.patch_json(
        request_path,
        {"data": updated_data},
        status=422
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u'description': [u'Must be either true or false.'],
          u'location': u'body',
          u'name': u'value'}]
    )

    updated_data["value"] = "True"
    response = self.app.patch_json(
        request_path,
        {"data": updated_data},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    rr = response.json["data"]
    self.assertEqual(rr["title"], updated_data["title"])
    self.assertEqual(rr["value"], updated_data["value"])
    self.assertNotIn("evidences", rr)


def get_qualification_requirement_response(self):
    base_request_path = "/tenders/{}/qualifications/{}/requirement_responses".format(
        self.tender_id, self.qualification_id)
    request_path = "{}?acc_token={}".format(base_request_path, self.tender_token)

    valid_data = [{
        "title": "Requirement response",
        "description": "some description",
        "requirement": {
            "id": self.requirement_id,
            "title": self.requirement_title,
        },
        "value": 'True'
    }]

    response = self.app.post_json(request_path, {"data": valid_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    rr_id = response.json["data"][0]["id"]

    response = self.app.get("/tenders/{}/qualifications/{}/requirement_responses".format(self.tender_id, self.qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    rrs = response.json["data"]
    self.assertEqual(len(rrs), 1)

    for i, rr_data in enumerate(valid_data):
        for k, v in rr_data.items():
            self.assertIn(k, rrs[i])
            self.assertEqual(v, rrs[i][k])

    response = self.app.get("/tenders/{}/qualifications/{}/requirement_responses/{}".format(
        self.tender_id, self.qualification_id, rr_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    rr = response.json["data"]
    for k, v in valid_data[0].items():
        self.assertIn(k, rr)
        self.assertEqual(v, rr[k])


def create_qualification_requirement_response_evidence(self):
    base_request_path = "/tenders/{}/qualifications/{}/requirement_responses/{}/evidences".format(
        self.tender_id, self.qualification_id, self.rr_id)
    request_path = "{}?acc_token={}".format(base_request_path, self.tender_token)

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("broker", ""))

    valid_data = {
        "title": "Requirement response",
        "relatedDocument": {
            "id": self.doc_id,
            "title": "name.doc",
        },
        "type": "document",
    }

    response = self.app.post_json(
        base_request_path,
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}]
    )

    response = self.app.post_json(
        "{}?acc_token={}".format(base_request_path, "some_random_token"),
        {"data": valid_data},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}]
    )

    self.app.authorization = auth
    response = self.app.post_json(
        request_path,
        {"data": {
            "title": "Some title",
            "description": "some description",
        }},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{u'description': [u'type should be one of eligibleEvidences types'],
          u'location': u'body',
          u'name': u'type'}],
    )

    response = self.app.post_json(
        request_path,
        {"data": {
            "title": "Some title",
            "description": "some description",
            "type": "document",
        }},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{u'description': [u'This field is required.'],
          u'location': u'body',
          u'name': u'relatedDocument'}]
    )

    response = self.app.post_json(
        request_path,
        {"data": {
            "title": "Some title",
            "description": "some description",
            "type": "document",
            "relatedDocument": {
                "id": "0"*32,
                "title": "test.doc",
            }
        }},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{u'description': [u'relatedDocument.id should be one of qualification documents'],
          u'location': u'body',
          u'name': u'relatedDocument'}]
    )

    response = self.app.post_json(
        request_path,
        {"data": valid_data}
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence = response.json["data"]

    for k, v in valid_data.items():
        self.assertIn(k, evidence)
        self.assertEqual(evidence[k], v)


def patch_qualification_requirement_response_evidence(self):
    valid_data = {
        "title": "Requirement response",
        "relatedDocument": {
            "id": self.doc_id,
            "title": "name.doc",
        },
        "type": "document",
    }

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/requirement_responses/{}/evidences?acc_token={}".format(
            self.tender_id, self.qualification_id, self.rr_id, self.tender_token),
        {"data": valid_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    updated_data = {
        "title": "Updated title",
        "description": "Updated description",
    }

    response = self.app.patch_json(
        "/tenders/{}/qualifications/{}/requirement_responses/{}/evidences/{}?acc_token={}".format(
            self.tender_id, self.qualification_id, self.rr_id, evidence_id, self.tender_token),
        {"data": updated_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    evidence = response.json["data"]

    self.assertEqual(evidence["title"], updated_data["title"])
    self.assertEqual(evidence["description"], updated_data["description"])


def get_qualification_requirement_response_evidence(self):

    valid_data = {
        "title": "Requirement response",
        "relatedDocument": {
            "id": self.doc_id,
            "title": "name.doc",
        },
        "type": "document",
    }

    response = self.app.post_json(
        "/tenders/{}/qualifications/{}/requirement_responses/{}/evidences?acc_token={}".format(
            self.tender_id, self.qualification_id, self.rr_id, self.tender_token),
        {"data": valid_data},
    )

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    evidence_id = response.json["data"]["id"]

    response = self.app.get("/tenders/{}/qualifications/{}/requirement_responses/{}/evidences".format(
        self.tender_id, self.qualification_id, self.rr_id
    ))

    evidences = response.json["data"]
    self.assertEqual(len(evidences), 1)

    for k, v in valid_data.items():
        self.assertIn(k, evidences[0])
        self.assertEqual(v, evidences[0][k])

    response = self.app.get("/tenders/{}/qualifications/{}/requirement_responses/{}/evidences/{}".format(
        self.tender_id, self.qualification_id, self.rr_id, evidence_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    rr = response.json["data"]
    for k, v in valid_data.items():
        self.assertIn(k, rr)
        self.assertEqual(v, rr[k])
