from uuid import uuid4

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
    response = self.app.post_json(
        "/agreements/{}/documents?acc_token={}".format(self.agreement_id, self.agreement_token),
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


def not_found(self):
    response = self.app.get("/agreements/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}])

    response = self.app.post_json(
        "/agreements/some_id/documents",
        {
            "data": {
                "title": "name1.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}])
    response = self.app.put_json(
        "/agreements/some_id/documents/some_id",
        {
            "data": {
                "title": "name1.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}])

    response = self.app.put(
        "/agreements/{}/documents/some_id".format(self.agreement_id),
        {
            "data": {
                "title": "name1.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}])

    response = self.app.get("/agreements/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "agreement_id"}])

    response = self.app.get("/agreements/{}/documents/some_id".format(self.agreement_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}])


def put_contract_document(self):
    response = self.app.post_json(
        "/agreements/{}/documents?acc_token={}".format(self.agreement_id, self.agreement_token),
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
        "/agreements/{}/documents/{}?acc_token={}".format(self.agreement_id, doc_id, self.agreement_token),
        {
            "data": {
                "title": "укр.doc",
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

    response = self.app.get("/agreements/{}/documents/{}".format(self.agreement_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    dateModified2 = response.json["data"]["dateModified"]
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]["dateModified"])

    response = self.app.get("/agreements/{}/documents?all=true".format(self.agreement_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified2, response.json["data"][1]["dateModified"])

    response = self.app.post_json(
        "/agreements/{}/documents?acc_token={}".format(self.agreement_id, self.agreement_token),
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

    response = self.app.get("/agreements/{}/documents".format(self.agreement_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified2, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified, response.json["data"][1]["dateModified"])
    response = self.app.put_json(
        "/agreements/{}/documents/{}?acc_token={}".format(self.agreement_id, doc_id, self.agreement_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

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
    response = self.app.put_json(
        "/agreements/{}/documents/{}?acc_token={}".format(self.agreement_id, doc_id, self.agreement_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
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


def document_related_item(self):
    doc_data = {
        "title": "укр.doc",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/msword",
        "documentOf": "item",
    }
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/documents?acc_token={self.agreement_token}",
        {"data": doc_data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0],
        {"location": "body", "name": "documents.relatedItem", "description": "This field is required."},
    )
    doc_data["relatedItem"] = uuid4().hex
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/documents?acc_token={self.agreement_token}",
        {"data": doc_data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0],
        {"location": "body", "name": "documents.relatedItem", "description": "relatedItem should be one of items"},
    )
    doc_data["relatedItem"] = self.initial_data["items"][0]["id"]
    response = self.app.post_json(
        f"/agreements/{self.agreement_id}/documents?acc_token={self.agreement_token}",
        {"data": doc_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]

    doc_data["documentOf"] = "contract"
    response = self.app.put_json(
        f"/agreements/{self.agreement_id}/documents/{doc_id}?acc_token={self.agreement_token}",
        {"data": doc_data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0],
        {"location": "body", "name": "documents.relatedItem", "description": "relatedItem should be one of contracts"},
    )
    doc_data["relatedItem"] = self.initial_data["contracts"][0]["id"]
    response = self.app.put_json(
        f"/agreements/{self.agreement_id}/documents/{doc_id}?acc_token={self.agreement_token}",
        {"data": doc_data},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    del doc_data["relatedItem"]
    response = self.app.patch_json(
        f"/agreements/{self.agreement_id}/documents/{doc_id}?acc_token={self.agreement_token}",
        {"data": {"documentOf": "change"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0],
        {"location": "body", "name": "documents.relatedItem", "description": "relatedItem should be one of changes"},
    )
