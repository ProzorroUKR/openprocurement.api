# -*- coding: utf-8 -*-
from openprocurement.framework.cfaua.tests.data import TEST_DOCUMENTS


def get_documents_list(self):
    resp = self.app.get("/agreements/{}/documents".format(self.agreement_id))
    documents = resp.json["data"]
    self.assertEqual(len(documents), len(TEST_DOCUMENTS))


def get_document_by_id(self):
    documents = self.mongodb.agreements.get(self.agreement_id).get("documents")
    for doc in documents:
        resp = self.app.get("/agreements/{}/documents/{}".format(self.agreement_id, doc["id"]))
        document = resp.json["data"]
        self.assertEqual(doc["id"], document["id"])
        self.assertEqual(doc["title"], document["title"])
        self.assertEqual(doc["format"], document["format"])
        self.assertEqual(doc["datePublished"], document["datePublished"])


def create_agreement_document_forbidden(self):
    response = self.app.post(
        "/agreements/{}/documents".format(self.agreement_id), upload_files=[("file", "укр.doc", b"content")], status=403
    )
    self.assertEqual(response.status, "403 Forbidden")


def create_agreement_documents(self):
    response = self.app.post(
        "/agreements/{}/documents?acc_token={}".format(self.agreement_id, self.agreement_token),
        upload_files=[("file", "укр.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def not_found(self):
    response = self.app.get("/agreements/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}]
    )

    response = self.app.post(
        "/agreements/some_id/documents", status=404, upload_files=[("file", "name.doc", b"content")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}]
    )
    response = self.app.post(
        "/agreements/{}/documents?acc_token={}".format(self.agreement_id, self.agreement_token),
        status=404,
        upload_files=[("invalid_name", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "body", "name": "file"}])
    response = self.app.put(
        "/agreements/some_id/documents/some_id", status=404, upload_files=[("file", "name.doc", b"content2")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}]
    )

    response = self.app.put(
        "/agreements/{}/documents/some_id".format(self.agreement_id),
        status=404,
        upload_files=[("file", "name.doc", b"content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
    )

    response = self.app.get("/agreements/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}]
    )

    response = self.app.get("/agreements/{}/documents/some_id".format(self.agreement_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
    )


def put_contract_document(self):
    response = self.app.post(
        "/agreements/{}/documents?acc_token={}".format(self.agreement_id, self.agreement_token),
        upload_files=[("file", "укр.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/agreements/{}/documents/{}?acc_token={}".format(self.agreement_id, doc_id, self.agreement_token),
        upload_files=[("file", "name name.doc", b"content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]

    response = self.app.get("/agreements/{}/documents/{}".format(self.agreement_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name name.doc", response.json["data"]["title"])
    dateModified2 = response.json["data"]["dateModified"]
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]["dateModified"])

    response = self.app.get("/agreements/{}/documents?all=true".format(self.agreement_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified2, response.json["data"][1]["dateModified"])

    response = self.app.post(
        "/agreements/{}/documents?acc_token={}".format(self.agreement_id, self.agreement_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.get("/agreements/{}/documents".format(self.agreement_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified2, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified, response.json["data"][1]["dateModified"])
    response = self.app.put(
        "/agreements/{}/documents/{}?acc_token={}".format(self.agreement_id, doc_id, self.agreement_token),
        status=404,
        upload_files=[("invalid_name", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "body", "name": "file"}])
    response = self.app.put(
        "/agreements/{}/documents/{}?acc_token={}".format(self.agreement_id, doc_id, self.agreement_token),
        "content3",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]

    response = self.app.get("/agreements/{}/documents/{}".format(self.agreement_id, doc_id, key))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/agreements/{}/documents".format(self.agreement_id, self.agreement_token))
    self.assertEqual(response.status, "200 OK")
    doc_id = response.json["data"][0]["id"]
    response = self.app.patch_json(
        "/agreements/{}/documents/{}?acc_token={}".format(self.agreement_id, doc_id, self.agreement_token),
        {"data": {"documentType": None}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/agreements/{}?acc_token={}".format(self.agreement_id, self.agreement_token),
        {"data": {"status": "terminated"}},
        content_type="application/json",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "terminated")
    response = self.app.put(
        "/agreements/{}/documents/{}?acc_token={}".format(self.agreement_id, doc_id, self.agreement_token),
        "contentX",
        content_type="application/msword",
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update document in current (terminated) agreement status",
                "location": "body",
                "name": "data",
            }
        ],
    )
    #  document in current (terminated}) agreement status
    response = self.app.patch_json(
        "/agreements/{}/documents/{}?acc_token={}".format(self.agreement_id, doc_id, self.agreement_token),
        {"data": {"documentType": None}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update document in current (terminated) agreement status",
                "location": "body",
                "name": "data",
            }
        ],
    )
