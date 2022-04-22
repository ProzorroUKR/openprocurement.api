# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.core.tests.base import change_auth

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

    response = self.app.put(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        status=404,
        upload_files=[("invalid_name", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "body", "name": "file"}])

    response = self.app.put(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", b"content2")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")

    response = self.app.put(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", b"content2")],
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

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/complaints/{}?acc_token={}".format(self.tender_id, self.complaint_id, self.complaint_owner_token),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/complaints/{}".format(self.tender_id, self.complaint_id),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.put(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        "content4",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/complaints/{}/documents/{}?download={}".format(self.tender_id, self.complaint_id, doc_id, key)
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    self.set_status("complete")

    response = self.app.put(
        "/tenders/{}/complaints/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.complaint_id, doc_id, self.complaint_owner_token
        ),
        upload_files=[("file", "name.doc", b"content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
    )
