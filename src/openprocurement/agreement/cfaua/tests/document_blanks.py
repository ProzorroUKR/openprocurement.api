# -*- coding: utf-8 -*-
from openprocurement.agreement.cfaua.tests.base import TEST_DOCUMENTS


def get_documents_list(self):
    resp = self.app.get("/agreements/{}/documents".format(self.agreement_id))
    documents = resp.json["data"]
    self.assertEqual(len(documents), len(TEST_DOCUMENTS))


def get_document_by_id(self):
    documents = self.db.get(self.agreement_id).get("documents")
    for doc in documents:
        resp = self.app.get("/agreements/{}/documents/{}".format(self.agreement_id, doc["id"]))
        document = resp.json["data"]
        self.assertEqual(doc["id"], document["id"])
        self.assertEqual(doc["title"], document["title"])
        self.assertEqual(doc["format"], document["format"])
        self.assertEqual(doc["datePublished"], document["datePublished"])


def create_agreement_document_forbidden(self):
    response = self.app.post(
        "/agreements/{}/documents".format(self.agreement_id), upload_files=[("file", u"укр.doc", "content")], status=403
    )
    self.assertEqual(response.status, "403 Forbidden")


def create_agreement_documents(self):
    response = self.app.post(
        "/agreements/{}/documents?acc_token={}".format(self.agreement_id, self.agreement_token),
        upload_files=[("file", u"укр.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def not_found(self):
    response = self.app.get("/agreements/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"agreement_id"}]
    )

    response = self.app.post(
        "/agreements/some_id/documents", status=404, upload_files=[("file", "name.doc", "content")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"agreement_id"}]
    )
    response = self.app.post(
        "/agreements/{}/documents?acc_token={}".format(self.agreement_id, self.agreement_token),
        status=404,
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])
    response = self.app.put(
        "/agreements/some_id/documents/some_id", status=404, upload_files=[("file", "name.doc", "content2")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"agreement_id"}]
    )

    response = self.app.put(
        "/agreements/{}/documents/some_id".format(self.agreement_id),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )

    response = self.app.get("/agreements/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"agreement_id"}]
    )

    response = self.app.get("/agreements/{}/documents/some_id".format(self.agreement_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )


def put_contract_document(self):
    from six import BytesIO
    from urllib import quote

    response = self.app.patch_json(
        "/agreements/{}?acc_token={}".format(self.agreement_id, self.agreement_token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")

    body = u"""--BOUNDARY\nContent-Disposition: form-data; name="file"; filename={}\nContent-Type: application/msword\n\ncontent\n""".format(
        u"\uff07"
    )
    environ = self.app._make_environ()
    environ["CONTENT_TYPE"] = "multipart/form-data; boundary=BOUNDARY"
    environ["REQUEST_METHOD"] = "POST"
    req = self.app.RequestClass.blank(
        self.app._remove_fragment("/agreements/{}/documents".format(self.agreement_id)), environ
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
        self.app._remove_fragment(
            "/agreements/{}/documents?acc_token={}".format(self.agreement_id, self.agreement_token)
        ),
        environ,
    )
    req.environ["wsgi.input"] = BytesIO(body.encode(req.charset or "utf8"))
    req.content_length = len(body)
    response = self.app.do_request(req)
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(u"укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/agreements/{}/documents/{}?acc_token={}".format(self.agreement_id, doc_id, self.agreement_token),
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
        contract = self.db.get(self.agreement_id)
        self.assertIn(key, contract["documents"][-1]["url"])
        self.assertIn("Signature=", contract["documents"][-1]["url"])
        self.assertIn("KeyID=", contract["documents"][-1]["url"])
        self.assertNotIn("Expires=", contract["documents"][-1]["url"])
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
        upload_files=[("file", "name.doc", "content")],
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
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])
    response = self.app.put(
        "/agreements/{}/documents/{}?acc_token={}".format(self.agreement_id, doc_id, self.agreement_token),
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
        contract = self.db.get(self.agreement_id)
        self.assertIn(key, contract["documents"][-1]["url"])
        self.assertIn("Signature=", contract["documents"][-1]["url"])
        self.assertIn("KeyID=", contract["documents"][-1]["url"])
        self.assertNotIn("Expires=", contract["documents"][-1]["url"])
    else:
        key = response.json["data"]["url"].split("?")[-1].split("=")[-1]
    if self.docservice:
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
                u"description": u"Can't update document in current (terminated) agreement status",
                u"location": u"body",
                u"name": u"data",
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
                u"description": u"Can't update document in current (terminated) agreement status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )
