from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_supplier
from openprocurement.tender.limited.tests.base import (
    test_tender_reporting_config,
    test_tender_reporting_data,
)


def not_found(self):
    response = self.app.get("/contracts/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.post(
        "/contracts/some_id/documents", status=404, upload_files=[("file", "name.doc", b"content")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.put(
        "/contracts/some_id/documents/some_id",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "1" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.put(
        f"/contracts/{self.contract_id}/documents/some_id",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "1" * 32,
                "format": "application/msword",
            }
        },
        status=404,
        upload_files=[("file", "name.doc", b"content2")],
    )
    self.assertEqual(response.status, "404 Not Found")

    response = self.app.get("/contracts/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.get(f"/contracts/{self.contract_id}/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}])


def create_contract_document(self):
    if self.contract["status"] != "active":
        self.set_status("active")

    response = self.app.get("/contracts/{}/documents".format(self.contract_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json, {"data": []})

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
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
    self.assertEqual("укр.doc", response.json["data"]["title"])
    self.assertEqual(response.json["data"]["documentOf"], "contract")

    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]

    response = self.app.get("/contracts/{}/documents".format(self.contract_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("укр.doc", response.json["data"][0]["title"])

    response = self.app.get(f"/contracts/{self.contract_id}/documents/{doc_id}?download=some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}])

    response = self.app.get(f"/contracts/{self.contract_id}/documents/{doc_id}?download={key}")
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    response = self.app.get(f"/contracts/{self.contract_id}/documents/{doc_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("укр.doc", response.json["data"]["title"])

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertNotIn("acc_token", response.headers["Location"])

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
        {"data": {"status": "terminated", "amountPaid": {"amount": 12, "amountNet": 11}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "terminated")

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "1" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't add document in current (terminated) contract status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def put_contract_document(self):
    if self.contract["status"] != "active":
        self.set_status("active")

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url("1" * 32),
                "hash": "md5:" + "1" * 32,
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

    response = self.app.get(f"/contracts/{self.contract_id}/documents/{doc_id}?download={key}")
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    response = self.app.get(f"/contracts/{self.contract_id}/documents/{doc_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    dateModified2 = response.json["data"]["dateModified"]
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]["dateModified"])

    response = self.app.get(f"/contracts/{self.contract_id}/documents?all=true")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified2, response.json["data"][1]["dateModified"])

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
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

    response = self.app.get("/contracts/{}/documents".format(self.contract_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified2, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified, response.json["data"][1]["dateModified"])

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url("2" * 32),
                "hash": "md5:" + "2" * 32,
                "format": "application/msword",
            }
        },
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]

    response = self.app.get(f"/contracts/{self.contract_id}/documents/{doc_id}?download={key}")
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract_id, self.contract_token),
        {"data": {"status": "terminated", "amountPaid": {"amount": 100, "amountNet": 90}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "terminated")

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url("3" * 32),
                "hash": "md5:" + "3" * 32,
                "format": "application/msword",
            }
        },
        content_type="application/msword",
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update document in current (terminated) contract status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def patch_contract_document(self):
    self.activate_contract()

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
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
    self.assertEqual("укр.doc", response.json["data"]["title"])
    self.assertEqual(response.json["data"]["documentOf"], "contract")
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"description": "document description", "documentType": "notice"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn("documentType", response.json["data"])
    self.assertEqual(response.json["data"]["documentType"], "notice")

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"documentType": None}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.get("/contracts/{}/documents/{}".format(self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.contract_token}",
        {"data": {"status": "terminated", "amountPaid": {"amount": 100, "amountNet": 90}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "terminated")

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"description": "document description X"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update document in current (terminated) contract status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def contract_change_document(self):
    self.activate_contract()

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
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
    self.assertEqual("укр.doc", response.json["data"]["title"])
    self.assertEqual(response.json["data"]["documentOf"], "contract")
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"documentOf": "change", "relatedItem": "1234" * 8}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "relatedItem", "description": ["relatedItem should be one of changes"]}],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/changes?acc_token={self.contract_token}",
        {
            "data": {
                "rationale": "причина зміни укр",
                "rationale_en": "change cause en",
                "rationaleTypes": ["priceReduction"],
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    change = response.json["data"]

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"documentOf": "change", "relatedItem": change["id"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(response.json["data"]["documentOf"], "change")
    self.assertEqual(response.json["data"]["relatedItem"], change["id"])

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url("1" * 32),
                "hash": "md5:" + "1" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/changes/{change['id']}?acc_token={self.contract_token}",
        {"data": {"status": "active", "dateSigned": get_now().isoformat()}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр2.doc",
                "url": self.generate_docservice_url("2" * 32),
                "hash": "md5:" + "2" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    doc_id = response.json["data"]["id"]

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"documentOf": "change", "relatedItem": change["id"]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't add document to 'active' change"}],
    )


def create_contract_document_json_invalid(self):
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {"data": {"title": "укр.doc", "url": self.generate_docservice_url(), "format": "application/msword"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "This field is required.")

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
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
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
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
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
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
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url().replace(list(self.app.app.registry.keyring.keys())[-1], "0" * 8),
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
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
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
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
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


def create_contract_document_json(self):
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
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
    self.assertEqual("укр.doc", response.json["data"]["title"])
    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    contract = self.mongodb.contracts.get(self.contract_id)
    self.assertIn(key, contract["documents"][-1]["url"])
    self.assertNotIn("Signature=", contract["documents"][-1]["url"])
    self.assertNotIn("KeyID=", contract["documents"][-1]["url"])
    self.assertNotIn("Expires=", contract["documents"][-1]["url"])

    response = self.app.get(f"/contracts/{self.contract_id}/documents")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("укр.doc", response.json["data"][0]["title"])

    response = self.app.get(f"/contracts/{self.contract_id}/documents/{doc_id}?download=some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}])

    response = self.app.get(f"/contracts/{self.contract_id}/documents/{doc_id}?download={key}")
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    response = self.app.get(f"/contracts/{self.contract_id}/documents/{doc_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("укр.doc", response.json["data"]["title"])

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertNotIn("acc_token", response.headers["Location"])


def put_contract_document_json(self):
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
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
    self.assertEqual("name.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
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
    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    contract = self.mongodb.contracts.get(self.contract_id)
    self.assertIn(key, contract["documents"][-1]["url"])
    self.assertNotIn("Signature=", contract["documents"][-1]["url"])
    self.assertNotIn("KeyID=", contract["documents"][-1]["url"])
    self.assertNotIn("Expires=", contract["documents"][-1]["url"])

    response = self.app.get(f"/contracts/{self.contract_id}/documents/{doc_id}?download={key}")
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    response = self.app.get(f"/contracts/{self.contract_id}/documents/{doc_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])
    dateModified2 = response.json["data"]["dateModified"]
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]["dateModified"])

    response = self.app.get(f"/contracts/{self.contract_id}/documents?all=true")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified2, response.json["data"][1]["dateModified"])

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
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

    response = self.app.get(f"/contracts/{self.contract_id}/documents")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified2, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified, response.json["data"][1]["dateModified"])

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
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
    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    contract = self.mongodb.contracts.get(self.contract_id)
    self.assertIn(key, contract["documents"][-1]["url"])
    self.assertNotIn("Signature=", contract["documents"][-1]["url"])
    self.assertNotIn("KeyID=", contract["documents"][-1]["url"])
    self.assertNotIn("Expires=", contract["documents"][-1]["url"])

    response = self.app.get(f"/contracts/{self.contract_id}/documents/{doc_id}?download={key}")
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)


def create_contract_transaction_document_json(self):
    transaction_id = 123456
    response = self.app.put_json(
        f"/contracts/{self.contract_id}/transactions/{transaction_id}?acc_token={self.contract_token}",
        {
            "data": {
                "date": "2020-05-20T18:47:47.136678+02:00",
                "value": {"amount": 500, "currency": "UAH"},
                "payer": {"bankAccount": {"id": 789, "scheme": "IBAN"}, "name": "payer1"},
                "payee": {"bankAccount": {"id": 789, "scheme": "IBAN"}, "name": "payee1"},
                "status": "status1234",
            }
        },
    )

    self.assertEqual(response.status, "200 OK")

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/transactions/{transaction_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "name name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/xml",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("name name.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]

    response = self.app.get(f"/contracts/{self.contract['id']}/transactions/{transaction_id}")
    documents = response.json['data']['documents']

    self.assertEqual(doc_id, documents[0]['id'])

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/transactions/{transaction_id}/documents?acc_token={self.contract_token}",
        {"dt": {}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/transactions/{transaction_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "name name2.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/xml",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("name name2.doc", response.json["data"]["title"])
    doc_id2 = response.json["data"]["id"]

    response = self.app.get(f"/contracts/{self.contract['id']}/transactions/{transaction_id}")
    documents = response.json['data']['documents']
    self.assertEqual(len(documents), 2)
    self.assertEqual(doc_id2, documents[1]['id'])

    invalid_transaction_id = 678123
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/transactions/{invalid_transaction_id}/documents?acc_token={self.contract_token}",
        {
            "data": {
                "title": "name name2.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/xml",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Not Found",
                'location': 'url',
                'name': 'transaction_id',
            }
        ],
    )


@patch(
    "openprocurement.tender.core.procedure.state.award.AWARD_NOTICE_DOC_REQUIRED_FROM", get_now() + timedelta(days=1)
)
def limited_contract_confidential_document(self):
    tender_data = deepcopy(test_tender_reporting_data)
    tender_data["cause"] = "UZ"
    response = self.app.post_json("/tenders", {"data": tender_data, "config": test_tender_reporting_config})
    tender = response.json["data"]
    tender_id = tender["id"]
    tender_token = response.json["access"]["token"]
    # activate tender
    self.app.patch_json(f"/tenders/{tender_id}?acc_token={tender_token}", {"data": {"status": "active"}})
    # post award
    response = self.app.post_json(
        f"/tenders/{tender_id}/awards?acc_token={tender_token}",
        {
            "data": {
                "suppliers": [test_tender_below_supplier],
                "subcontractingDetails": "Details",
                "status": "pending",
                "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
            }
        },
    )
    award_id = response.json["data"]["id"]
    # activate winner
    self.app.patch_json(
        f"/tenders/{tender_id}/awards/{award_id}?acc_token={tender_token}",
        {"data": {"status": "active", "qualified": True}},
    )

    response = self.app.get(f"/tenders/{tender_id}/contracts")
    contract_id = response.json["data"][0]["id"]

    response = self.app.patch_json(
        f"/contracts/{contract_id}/credentials?acc_token={tender_token}",
        {"data": {}},
    )
    contract_token = response.json["access"]["token"]

    request_data = {
        "title": "name.doc",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/msword",
        "confidentiality": "true",
    }

    # rogue value
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={contract_token}",
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {
                    "location": "body",
                    "name": "confidentiality",
                    "description": ["Value must be one of ['public', 'buyerOnly']."],
                }
            ],
        },
    )

    # add doc without documentType
    request_data["confidentiality"] = "buyerOnly"
    request_data["confidentialityRationale"] = f"{'a' * 30}"
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={contract_token}",
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [{"location": "body", "name": "confidentiality", "description": "Document should be public"}],
        },
    )
    request_data["confidentiality"] = "public"
    del request_data["confidentialityRationale"]
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={contract_token}",
        {"data": request_data},
        status=201,
    )
    doc_id_1 = response.json["data"]["id"]
    self.assertEqual(response.json["data"]["confidentiality"], "public")

    # add doc with confidential documentType
    request_data["documentType"] = "contractAnnexe"
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={contract_token}",
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {"location": "body", "name": "confidentiality", "description": "Document should be confidential"}
            ],
        },
    )
    # post confidential doc without rationale
    request_data["confidentiality"] = "buyerOnly"
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={contract_token}",
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {
                    "location": "body",
                    "name": "confidentialityRationale",
                    "description": ["confidentialityRationale is required"],
                }
            ],
        },
    )
    request_data["confidentialityRationale"] = "coz it is hidden"
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={contract_token}",
        {"data": request_data},
        status=422,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [
                {
                    "location": "body",
                    "name": "confidentialityRationale",
                    "description": ["confidentialityRationale should contain at least 30 characters"],
                }
            ],
        },
    )
    request_data["confidentialityRationale"] = "coz it is hidden because of the law"
    response = self.app.post_json(
        f"/contracts/{contract_id}/documents?acc_token={contract_token}",
        {"data": request_data},
        status=201,
    )
    doc_id_2 = response.json["data"]["id"]
    self.assertEqual(response.json["data"]["confidentiality"], "buyerOnly")

    # get list as tender owner
    response = self.app.get(f"/contracts/{contract_id}/documents?acc_token={contract_token}")
    self.assertEqual(len(response.json["data"]), 2)
    for doc in response.json["data"]:
        self.assertIn("url", doc)

    # get list as public
    response = self.app.get(f"/contracts/{contract_id}/documents")
    self.assertEqual(len(response.json["data"]), 2)
    for doc in response.json["data"]:
        if doc["confidentiality"] == "buyerOnly":
            self.assertNotIn("url", doc)
        else:
            self.assertIn("url", doc)

    # get directly as tender owner
    response = self.app.get(f"/contracts/{contract_id}/documents/{doc_id_2}?acc_token={contract_token}")
    self.assertIn("url", response.json["data"])

    # get directly as public
    response = self.app.get(f"/contracts/{contract_id}/documents/{doc_id_2}")
    self.assertNotIn("url", response.json["data"])

    # download as tender owner
    response = self.app.get(
        f"/contracts/{contract_id}/documents/{doc_id_2}?acc_token={contract_token}&download=1",
    )
    self.assertEqual(response.status_code, 302)
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertIn("Expires=", response.location)

    # download as tender public
    response = self.app.get(
        f"/contracts/{contract_id}/documents/{doc_id_2}?download=1",
        status=403,
    )
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [{"location": "body", "name": "data", "description": "Document download forbidden."}],
        },
    )

    # patch first doc documentType to confidential
    self.app.patch_json(
        f"/contracts/{contract_id}/documents/{doc_id_1}?acc_token={contract_token}",
        {
            "data": {
                "documentType": "contractSigned",
                "confidentiality": "buyerOnly",
                "confidentialityRationale": f"{'a' * 30}",
            }
        },
    )
    # get directly as tender owner
    response = self.app.get(f"/contracts/{contract_id}/documents/{doc_id_1}?acc_token={contract_token}")
    self.assertIn("url", response.json["data"])

    # get directly as public
    response = self.app.get(f"/contracts/{contract_id}/documents/{doc_id_1}")
    self.assertNotIn("url", response.json["data"])

    # put second doc documentOf to non confidential
    request_data.update(
        {
            "documentOf": "tender",
            "confidentiality": "public",
        }
    )

    self.app.put_json(
        f"/contracts/{contract_id}/documents/{doc_id_2}?acc_token={contract_token}",
        {"data": request_data},
    )
    # get directly as tender owner
    response = self.app.get(f"/contracts/{contract_id}/documents/{doc_id_2}?acc_token={contract_token}")
    self.assertIn("url", response.json["data"])

    # get directly as public
    response = self.app.get(f"/contracts/{contract_id}/documents/{doc_id_2}")
    self.assertIn("url", response.json["data"])
