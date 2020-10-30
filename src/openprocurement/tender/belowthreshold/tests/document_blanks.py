# -*- coding: utf-8 -*-
from email.header import Header

# TenderDocumentResourceTest
import re
import ast
from mock import patch
from copy import deepcopy
from openprocurement.tender.core.tests.base import bad_rs_request, srequest, change_auth
from openprocurement.tender.belowthreshold.tests.base import test_tender_document_data
from openprocurement.api.models import Document as BaseDocument


def not_found(self):
    response = self.app.get("/tenders/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.post("/tenders/some_id/documents", status=404, upload_files=[("file", "name.doc", "content")])
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.post(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        status=404,
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])

    response = self.app.put(
        "/tenders/some_id/documents/some_id", status=404, upload_files=[("file", "name.doc", "content2")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.put(
        "/tenders/{}/documents/some_id?acc_token={}".format(self.tender_id, self.tender_token),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )

    response = self.app.get("/tenders/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.get(
        "/tenders/{}/documents/some_id?acc_token={}".format(self.tender_id, self.tender_token), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )


def create_tender_document(self):
    response = self.app.get("/tenders/{}/documents".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json, {"data": []})

    response = self.app.post(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        upload_files=[("file", u"укр.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual(u"укр.doc", response.json["data"]["title"])
    if self.docservice:
        self.assertIn("Signature=", response.json["data"]["url"])
        self.assertIn("KeyID=", response.json["data"]["url"])
        self.assertNotIn("Expires=", response.json["data"]["url"])
        key = response.json["data"]["url"].split("/")[-1].split("?")[0]
        tender = self.db.get(self.tender_id)
        self.assertIn(key, tender["documents"][-1]["url"])
        self.assertIn("Signature=", tender["documents"][-1]["url"])
        self.assertIn("KeyID=", tender["documents"][-1]["url"])
        self.assertNotIn("Expires=", tender["documents"][-1]["url"])
    else:
        key = response.json["data"]["url"].split("?")[-1].split("=")[-1]

    response = self.app.get("/tenders/{}/documents".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual(u"укр.doc", response.json["data"][0]["title"])

    response = self.app.get("/tenders/{}/documents/{}?download=some_id".format(self.tender_id, doc_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
    )

    if self.docservice:
        response = self.app.get("/tenders/{}/documents/{}?download={}".format(self.tender_id, doc_id, key))
        self.assertEqual(response.status, "302 Moved Temporarily")
        self.assertIn("http://localhost/get/", response.location)
        self.assertIn("Signature=", response.location)
        self.assertIn("KeyID=", response.location)
        self.assertNotIn("Expires=", response.location)
    else:
        response = self.app.get("/tenders/{}/documents/{}?download={}".format(self.tender_id, doc_id, key))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/msword")
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, "content")

    response = self.app.get("/tenders/{}/documents/{}".format(self.tender_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u"укр.doc", response.json["data"]["title"])

    response = self.app.post(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        upload_files=[("file", u"укр.doc".encode("ascii", "xmlcharrefreplace"), "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(u"укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertNotIn("acc_token", response.headers["Location"])


def create_document_active_tendering_status(self):

    self.set_status("active.tendering")

    response = self.app.post(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        upload_files=[("file", u"укр.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document in current (active.tendering) tender status"
    )


def put_tender_document(self):
    from six import BytesIO
    from urllib import quote

    body = u"""--BOUNDARY\nContent-Disposition: form-data; name="file"; filename={}\nContent-Type: application/msword\n\ncontent\n""".format(
        u"\uff07"
    )
    environ = self.app._make_environ()
    environ["CONTENT_TYPE"] = "multipart/form-data; boundary=BOUNDARY"
    environ["REQUEST_METHOD"] = "POST"
    req = self.app.RequestClass.blank(
        self.app._remove_fragment("/tenders/{}/documents".format(self.tender_id)), environ
    )
    req.environ["wsgi.input"] = BytesIO(body.encode("utf8"))
    req.content_length = len(body)
    response = self.app.do_request(req, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "could not decode params")

    body = u"""--BOUNDARY\nContent-Disposition: form-data; name="file"; filename*=utf-8''{}\nContent-Type: application/msword\n\ncontent\n""".format(
        quote("укр.doc")
    )
    environ = self.app._make_environ()
    environ["CONTENT_TYPE"] = "multipart/form-data; boundary=BOUNDARY"
    environ["REQUEST_METHOD"] = "POST"
    req = self.app.RequestClass.blank(
        self.app._remove_fragment("/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token)),
        environ,
    )
    req.environ["wsgi.input"] = BytesIO(body.encode(req.charset or "utf8"))
    req.content_length = len(body)
    response = self.app.do_request(req)
    # response = self.app.post('/tenders/{}/documents'.format(
    # self.tender_id), upload_files=[('file', 'name.doc', 'content')])
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(u"укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    datePublished = response.json["data"]["datePublished"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        upload_files=[("file", "name  name.doc", "content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    if self.docservice:
        self.assertIn("Signature=", response.json["data"]["url"])
        self.assertIn("KeyID=", response.json["data"]["url"])
        self.assertNotIn("Expires=", response.json["data"]["url"])
        key = response.json["data"]["url"].split("/")[-1].split("?")[0]
        tender = self.db.get(self.tender_id)
        self.assertIn(key, tender["documents"][-1]["url"])
        self.assertIn("Signature=", tender["documents"][-1]["url"])
        self.assertIn("KeyID=", tender["documents"][-1]["url"])
        self.assertNotIn("Expires=", tender["documents"][-1]["url"])
    else:
        key = response.json["data"]["url"].split("?")[-1].split("=")[-1]

    if self.docservice:
        response = self.app.get("/tenders/{}/documents/{}?download={}".format(self.tender_id, doc_id, key))
        self.assertEqual(response.status, "302 Moved Temporarily")
        self.assertIn("http://localhost/get/", response.location)
        self.assertIn("Signature=", response.location)
        self.assertIn("KeyID=", response.location)
        self.assertNotIn("Expires=", response.location)
    else:
        response = self.app.get("/tenders/{}/documents/{}?download={}".format(self.tender_id, doc_id, key))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/msword")
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, "content2")

    response = self.app.get("/tenders/{}/documents/{}".format(self.tender_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name name.doc", response.json["data"]["title"])
    dateModified2 = response.json["data"]["dateModified"]
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]["dateModified"])
    self.assertEqual(response.json["data"]["datePublished"], datePublished)

    response = self.app.get("/tenders/{}/documents?all=true".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified2, response.json["data"][1]["dateModified"])

    response = self.app.post(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.get("/tenders/{}/documents".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified2, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified, response.json["data"][1]["dateModified"])

    response = self.app.put(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        status=404,
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])

    response = self.app.put(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        "content3",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    if self.docservice:
        self.assertIn("Signature=", response.json["data"]["url"])
        self.assertIn("KeyID=", response.json["data"]["url"])
        self.assertNotIn("Expires=", response.json["data"]["url"])
        key = response.json["data"]["url"].split("/")[-1].split("?")[0]
        tender = self.db.get(self.tender_id)
        self.assertIn(key, tender["documents"][-1]["url"])
        self.assertIn("Signature=", tender["documents"][-1]["url"])
        self.assertIn("KeyID=", tender["documents"][-1]["url"])
        self.assertNotIn("Expires=", tender["documents"][-1]["url"])
    else:
        key = response.json["data"]["url"].split("?")[-1].split("=")[-1]

    if self.docservice:
        response = self.app.get("/tenders/{}/documents/{}?download={}".format(self.tender_id, doc_id, key))
        self.assertEqual(response.status, "302 Moved Temporarily")
        self.assertIn("http://localhost/get/", response.location)
        self.assertIn("Signature=", response.location)
        self.assertIn("KeyID=", response.location)
        self.assertNotIn("Expires=", response.location)
    else:
        response = self.app.get("/tenders/{}/documents/{}?download={}".format(self.tender_id, doc_id, key))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/msword")
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, "content3")

    self.set_status(self.forbidden_document_modification_actions_status)

    response = self.app.put(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        upload_files=[("file", "name.doc", "content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document in current ({}) tender status".format(
            self.forbidden_document_modification_actions_status
        ),
    )


def patch_tender_document(self):
    response = self.app.post(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        upload_files=[("file", str(Header(u"укр.doc", "utf-8")), "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    # dateModified = response.json["data"]['dateModified']
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual(u"укр.doc", response.json["data"]["title"])
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {"data": {"documentOf": "item", "relatedItem": "0" * 32}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"relatedItem should be one of items"], u"location": u"body", u"name": u"relatedItem"}],
    )

    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {"data": {"description": "document description", "documentType": "tenderNotice"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn("documentType", response.json["data"])
    self.assertEqual(response.json["data"]["documentType"], "tenderNotice")

    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {"data": {"documentType": None}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.get("/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])
    # self.assertTrue(dateModified < response.json["data"]["dateModified"])

    self.set_status(self.forbidden_document_modification_actions_status)

    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document in current ({}) tender status".format(
            self.forbidden_document_modification_actions_status
        ),
    )


# TenderDocumentWithDSResourceTest


def create_tender_document_error(self):
    with patch("openprocurement.api.utils.SESSION", srequest):
        response = self.app.post(
            "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
            upload_files=[("file", u"укр.doc", "content")],
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Can't upload document to document service.")

    with patch("openprocurement.api.utils.SESSION", bad_rs_request):
        response = self.app.post(
            "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
            upload_files=[("file", u"укр.doc", "content")],
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"][0]["description"], "Can't upload document to document service.")


def create_tender_document_json_invalid(self):
    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"title": u"укр.doc", "url": self.generate_docservice_url(), "format": "application/msword"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "This field is required.")

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "0" * 32,
                "format": "application/msword",
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Hash type is not supported."], u"location": u"body", u"name": u"hash"}],
    )

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "sha2048:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Hash type is not supported."], u"location": u"body", u"name": u"hash"}],
    )

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "sha512:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Hash value is wrong length."], u"location": u"body", u"name": u"hash"}],
    )

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "O" * 32,
                "format": "application/msword",
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"Hash value is not hexadecimal."], u"location": u"body", u"name": u"hash"}],
    )

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": "http://invalid.docservice.url/get/uuid",
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add document only from document service.")

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": "/".join(self.generate_docservice_url().split("/")[:4]),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add document only from document service.")

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url().split("?")[0],
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add document only from document service.")

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url().replace(self.app.app.registry.keyring.keys()[-1], "0" * 8),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Document url expired.")

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url().replace("Signature=", "Signature=ABC"),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Document url signature invalid.")

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url().replace("Signature=", "Signature=bw%3D%3D"),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Document url invalid.")


def create_tender_document_json(self):
    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
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
    self.assertEqual(u"укр.doc", response.json["data"]["title"])
    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    tender = self.db.get(self.tender_id)
    self.assertIn(key, tender["documents"][-1]["url"])
    self.assertIn("Signature=", tender["documents"][-1]["url"])
    self.assertIn("KeyID=", tender["documents"][-1]["url"])
    self.assertNotIn("Expires=", tender["documents"][-1]["url"])

    response = self.app.get("/tenders/{}/documents".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual(u"укр.doc", response.json["data"][0]["title"])

    response = self.app.get("/tenders/{}/documents/{}?download=some_id".format(self.tender_id, doc_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
    )

    response = self.app.get("/tenders/{}/documents/{}?download={}".format(self.tender_id, doc_id, key))
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertNotIn("Expires=", response.location)

    response = self.app.get("/tenders/{}/documents/{}".format(self.tender_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u"укр.doc", response.json["data"]["title"])

    self.set_status(self.forbidden_document_modification_actions_status)

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
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
        response.json["errors"][0]["description"],
        "Can't add document in current ({}) tender status".format(self.forbidden_document_modification_actions_status),
    )


def put_tender_document_json(self):
    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(u"укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    datePublished = response.json["data"]["datePublished"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {
            "data": {
                "title": u"name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    tender = self.db.get(self.tender_id)
    self.assertIn(key, tender["documents"][-1]["url"])
    self.assertIn("Signature=", tender["documents"][-1]["url"])
    self.assertIn("KeyID=", tender["documents"][-1]["url"])
    self.assertNotIn("Expires=", tender["documents"][-1]["url"])

    response = self.app.get("/tenders/{}/documents/{}?download={}".format(self.tender_id, doc_id, key))
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertNotIn("Expires=", response.location)

    response = self.app.get("/tenders/{}/documents/{}".format(self.tender_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(u"name.doc", response.json["data"]["title"])
    dateModified2 = response.json["data"]["dateModified"]
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]["dateModified"])
    self.assertEqual(response.json["data"]["datePublished"], datePublished)

    response = self.app.get("/tenders/{}/documents?all=true".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified2, response.json["data"][1]["dateModified"])

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
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
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.get("/tenders/{}/documents".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified2, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified, response.json["data"][1]["dateModified"])

    response = self.app.put_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    tender = self.db.get(self.tender_id)
    self.assertIn(key, tender["documents"][-1]["url"])
    self.assertIn("Signature=", tender["documents"][-1]["url"])
    self.assertIn("KeyID=", tender["documents"][-1]["url"])
    self.assertNotIn("Expires=", tender["documents"][-1]["url"])

    response = self.app.get("/tenders/{}/documents/{}?download={}".format(self.tender_id, doc_id, key))
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertNotIn("Expires=", response.location)

    self.set_status(self.forbidden_document_modification_actions_status)

    response = self.app.put_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
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
        response.json["errors"][0]["description"],
        "Can't update document in current ({}) tender status".format(
            self.forbidden_document_modification_actions_status
        ),
    )


def lot_patch_tender_document_json_lots_none(self):
    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "lot",
                "relatedItem": self.initial_lots[0]["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"lots": [None]}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")

    errors = {error["name"]: error["description"] for error in response.json["errors"]}
    self.assertEqual(errors["lots"][0], ["This field is required."])
    self.assertEqual(errors["documents"][0], {"relatedItem": ["relatedItem should be one of lots"]})


def lot_patch_tender_document_json_items_none(self):
    response = self.app.get("/tenders/{}".format(self.tender_id))

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "item",
                "relatedItem": response.json["data"]["items"][0]["id"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"items": [None]}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")

    errors = {error["name"]: error["description"] for error in response.json["errors"]}
    self.assertEqual(errors["documents"][0], {"relatedItem": ["relatedItem should be one of items"]})


def create_document_with_the_invalid_document_type(self):
    """
    A test checks if errors raise in case of processing document with the invalid document type (documentType field).
    """
    document_data = deepcopy(test_tender_document_data)
    document_data["url"] = self.generate_docservice_url()
    document_data["hash"] = "md5:" + "0" * 32
    document_data["documentType"] = "smth"

    response = self.app.post_json("/tenders/{}/documents?acc_token={}".format(
            self.tender_id, self.tender_token),{"data":document_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    response_doctype_dict = re.findall(r"\[.*\]",response.json["errors"][0]["description"][0])[0]
    response_doctype_dict = ast.literal_eval(response_doctype_dict)
    response_doctype_dict = [n.strip() for n in response_doctype_dict]


def put_tender_json_document_of_document(self):
    document_data = deepcopy(test_tender_document_data)
    document_data["url"] = self.generate_docservice_url()
    document_data["hash"] = "md5:" + "0" * 32
    document_data["documentType"] = "tenderNotice"

    response = self.app.post_json("/tenders/{}/documents?acc_token={}".format(
            self.tender_id, self.tender_token),{"data":document_data}, status=201)

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    document_id = response.json["data"]["id"]

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "document",
                "relatedItem": document_id,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {
                "title": u"укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "document",
                "relatedItem": "0"*32,
            }}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"location": u"body",
                u"name": u"relatedItem",
                u"description": [
                    u'relatedItem should be one of documents'
                ]
            }
        ]
    )


########################################################
# E-Contracting flow tests
########################################################
def _create_contract_proforma_document(self, lots=False):
    """
    Utility for create document with documentType contractProforma
    """

    data = {
        "title": u"paper0000001.pdf",
        "hash": "md5:" + "0" * 32,
        "templateId": "paper00000001",
        "documentType": "contractProforma",
    }
    if lots:
        response = self.app.get("/tenders/{}".format(self.tender_id))
        data["relatedItem"] = response.json["data"]["lots"][0]["id"]
        data["documentOf"] = "lot"

    response = self.app.post_json("/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
                                  {"data": data})
    document_id = response.json["data"]["id"]
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["documentType"], data["documentType"])
    self.assertEqual(response.json["data"]["templateId"], data["templateId"])
    if not lots:
        self.assertEqual(response.json["data"]["documentOf"], "tender")
    else:
        self.assertEqual(response.json["data"]["documentOf"], data["documentOf"])
        self.assertEqual(response.json["data"]["relatedItem"], data["relatedItem"])

    response = self.app.get("/tenders/{}/documents".format(self.tender_id))
    doc_ids = (doc['id'] for doc in response.json["data"])
    self.assertIn(document_id, doc_ids)
    return document_id


def _create_contract_proforma_document_invalid(self, lots=False):
    """
    Utility for unsuccessful create document with documentType contractProforma
    """
    data = {
        "title": u"paper0000001.docx",
        "format": "application/pkcs7-signature",
        "hash": "md5:" + "0" * 32,
        "documentType": "contractProforma"
    }
    resource = "tender"
    if lots:
        response = self.app.get("/tenders/{}".format(self.tender_id))
        data["relatedItem"] = response.json["data"]["lots"][0]["id"]
        data["documentOf"] = "lot"
        resource = "lot"

    response = self.app.post_json("/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
                                  {"data": data},
                                  status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"],
                     [{u'description': [u"templateId is required for documentType 'contractProforma'"],
                       u'location': u'body',
                       u'name': u'templateId'}]
    )

    data["templateId"] = "paper00000001"
    response = self.app.post_json("/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
                                  {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.post_json("/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
                                  {"data": data},
                                  status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u'description': [u"Allow only one document with documentType 'contractProforma' per {}.".format(resource)],
          u'location': u'body',
          u'name': u'documents'}])

    data["documentType"] = "contractTemplate"
    data["url"] = self.generate_docservice_url()
    data["format"] = "application/json"
    response = self.app.post_json("/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
                                  {"data": data},
                                  status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"],
                     [{u'description': [u'Rogue field'], u'location': u'body', u'name': u'templateId'}])


def _create_docs_by_registry_bot(self, document_id):
    """
    Utility allow create documents with documentTypes (contractTemplate, contractSchema, contractForm) also with
    registryBot credentials.
    """
    with change_auth(self.app, ("Basic", ("trBot", ""))):
        doc_types = {
            "contractTemplate": {
                "title": "paper0000001.docx",
                "documentType": "contractTemplate",
                "format": "application/msword"
            },
            "contractForm": {
                "title": "paper0000001-form.json",
                "documentType": "contractForm",
                "format": "application/json"
            },
            "contractSchema": {
                "title": "paper0000001-scheme.json",
                "documentType": "contractSchema",
                "format": "application/json"
            }
        }
        for doc_type in doc_types:
            doc_data = {
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "relatedItem": document_id,
                "documentOf": "document"
            }
            doc_data.update(doc_types[doc_type])
            response = self.app.post_json("/tenders/{}/documents".format(self.tender_id), {"data": doc_data})
            self.assertEqual(response.status, "201 Created")
            self.assertEqual(response.json["data"]["documentType"], doc_data["documentType"])
            self.assertEqual(response.json["data"]["relatedItem"], document_id)
            self.assertEqual(response.json["data"]["documentOf"], "document")

    response = self.app.get("/tenders/{}/documents".format(self.tender_id))
    docs = [doc for doc in response.json["data"] if doc.get("documentType", "") in doc_types]
    self.assertEqual(len(docs), 3)


def _create_docs_by_registry_bot_invalid(self, document_id, res="tender"):
    """
    Utility allow create documents with documentTypes (contractTemplate, contractSchema, contractForm) also with
    registryBot credentials.
    """
    with change_auth(self.app, ("Basic", ("trBot", ""))):
        doc_types = {
            "contractTemplate": {
                "title": "paper0000001.docx",
                "documentType": "contractTemplate",
                "format": "application/msword"
            },
            "contractForm": {
                "title": "paper0000001-form.json",
                "documentType": "contractForm",
                "format": "application/json"
            },
            "contractSchema": {
                "title": "paper0000001-scheme.json",
                "documentType": "contractSchema",
                "format": "application/json"
            }
        }
        for doc_type in doc_types:
            doc_data = {
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "relatedItem": document_id,
                "documentOf": "document"
            }
            doc_data.update(doc_types[doc_type])
            response = self.app.post_json("/tenders/{}/documents".format(self.tender_id),
                                          {"data": doc_data},
                                          status=422)
            self.assertEqual(response.status, "422 Unprocessable Entity")
            self.assertEqual(
                response.json["errors"],
                [{u'description': [u"Allow only one document with documentType '{}' per {}.".format(doc_type, res)],
                  u'location': u'body',
                  u'name': u'documents'}]
            )


def _create_contract_data_document(self, document_id):
    """
    Utility for create document with documentType contractData
    """
    data = {
        "title": u"buyerContractData.json",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/json",
        "documentOf": "document",
        "documentType": "contractData",
        "relatedItem": document_id
    }

    response = self.app.post_json("/tenders/{}/documents?acc_token={}".format(self.tender_id, self.tender_token),
                                  {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["documentType"], data["documentType"])
    self.assertEqual(response.json["data"]["relatedItem"], data["relatedItem"])
    self.assertEqual(response.json["data"]["documentOf"], "document")
    return response.json["data"]["id"]


def _upload_contract_proforma_by_renderer_bot(self, document_id):
    """
    Utility for upload contractProforma document by rendererBot
    """
    response = self.app.get("/tenders/{}/documents/{}".format(self.tender_id, document_id))
    self.assertEqual(response.json["data"]["title"], "paper0000001.pdf")
    self.assertEqual(response.json["data"]["author"], "tender_owner")

    with change_auth(self.app, ("Basic", ("rBot", ""))):
        response = self.app.put(
            "/tenders/{}/documents/{}".format(self.tender_id, document_id),
            upload_files=[("file", "contractProforma.pdf", "contentRenderedPDF")],
        )
        self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}/documents/{}".format(self.tender_id, document_id))
    self.assertEqual(response.json["data"]["title"], "contractProforma.pdf")
    self.assertEqual(response.json["data"]["author"], "tender_owner")


def create_tender_contract_proforma_document_json_invalid(self):
    return _create_contract_proforma_document_invalid(self)


def create_tender_contract_proforma_document_json(self):
    return _create_contract_proforma_document(self)


def create_lot_contract_proforma_document_json(self):
    return _create_contract_proforma_document(self, lots=True)


def create_lot_contract_proforma_document_json_invalid(self):
    return _create_contract_proforma_document_invalid(self, lots=True)


def create_tender_documents_by_registry_bot(self):
    document_id = _create_contract_proforma_document(self)
    _create_docs_by_registry_bot(self, document_id)


def create_lot_documents_by_registry_bot(self):
    document_id = _create_contract_proforma_document(self, lots=True)
    _create_docs_by_registry_bot(self, document_id)


def create_tender_documents_by_registry_bot_invalid(self):
    document_id = _create_contract_proforma_document(self)

    _create_docs_by_registry_bot(self, document_id)
    _create_docs_by_registry_bot_invalid(self, document_id)


def create_lot_documents_by_registry_bot_invalid(self):
    document_id = _create_contract_proforma_document(self, lots=True)

    _create_docs_by_registry_bot(self, document_id)
    _create_docs_by_registry_bot_invalid(self, document_id, res="lot")


def create_tender_contract_data_document_json(self):
    document_id = _create_contract_proforma_document(self)

    ids = set()
    ids.add(document_id)

    contract_data_id = _create_contract_data_document(self, document_id)
    ids.add(contract_data_id)

    response = self.app.get("/tenders/{}/documents".format(self.tender_id))
    doc_ids = {doc['id'] for doc in response.json["data"]}
    self.assertTrue(ids.issubset(doc_ids))


def create_lot_contract_data_document_json(self):
    document_id = _create_contract_proforma_document(self, lots=True)

    ids = set()
    ids.add(document_id)

    contract_data_id = _create_contract_data_document(self, document_id)
    ids.add(contract_data_id)

    response = self.app.get("/tenders/{}/documents".format(self.tender_id))
    doc_ids = {doc['id'] for doc in response.json["data"]}
    self.assertTrue(ids.issubset(doc_ids))


def upload_tender_document_by_renderer_bot(self):
    document_id = _create_contract_proforma_document(self)
    _create_docs_by_registry_bot(self, document_id)
    _create_contract_data_document(self, document_id)
    _upload_contract_proforma_by_renderer_bot(self, document_id)


def upload_lot_document_by_renderer_bot(self):
    document_id = _create_contract_proforma_document(self, lots=True)
    _create_docs_by_registry_bot(self, document_id)
    _create_contract_data_document(self, document_id)
    _upload_contract_proforma_by_renderer_bot(self, document_id)


def patch_tender_contract_proforma_document_invalid(self):
    doc_id = _create_contract_proforma_document(self)

    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {"data": {"templateId": "seeds00010001"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{u'description': u'Not allowed update document with documentType contractProforma, use append new version of'
            ' this document instead',
          u'location': u'body',
          u'name': u'data'}]
    )


def put_tender_contract_proforma_document(self):
    doc_id = _create_contract_proforma_document(self)

    response = self.app.get("/tenders/{}/documents/{}".format(self.tender_id, doc_id))
    self.assertEqual(response.json["data"]["title"], "paper0000001.pdf")
    self.assertEqual(response.json["data"]["templateId"], "paper00000001")

    data = {
        "title": "flowers0000001.pdf",
        "hash": "md5:" + "0" * 32,
        "templateId": "flowers0000001",
        "documentType": "contractProforma",
    }
    response = self.app.put_json(
        "/tenders/{}/documents/{}?acc_token={}".format(self.tender_id, doc_id, self.tender_token),
        {"data": data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], data["title"])
    self.assertEqual(response.json["data"]["templateId"], data["templateId"])

    response = self.app.get("/tenders/{}/documents/{}".format(self.tender_id, doc_id))
    self.assertEqual(response.json["data"]["title"], data["title"])
    self.assertEqual(response.json["data"]["templateId"], data["templateId"])


def upload_tender_document_contract_proforma_by_rbot_fail(self):
    document_id = _create_contract_proforma_document(self)
    _create_docs_by_registry_bot(self, document_id)
    _create_contract_data_document(self, document_id)
    _upload_contract_proforma_by_renderer_bot(self, document_id)

    data = {
        "title": "contractProforma.pdf",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/json",
        "documentOf": "document",
        "documentType": "contractProforma",
        "relatedItem": document_id,
        "templateId": "paper0000001"
    }
    with change_auth(self.app, ("Basic", ("rBot", ""))):
        response = self.app.post_json("/tenders/{}/documents".format(self.tender_id),
                                      {'data': data},
                                      status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.json["errors"],
                     [{"location": "body",
                       "name": "documents",
                       "description": ["Can't link document 'contractProforma' to another 'contractProforma'"]}])
