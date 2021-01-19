# -*- coding: utf-8 -*-
from openprocurement.api.tests.base import change_auth
from openprocurement.framework.electroniccatalogue.tests.base import test_electronicCatalogue_documents


def get_documents_list(self):
    response = self.app.get("/frameworks/{}/documents".format(self.framework_id))
    documents = response.json["data"]
    self.assertEqual(len(documents), len(test_electronicCatalogue_documents))


def get_document_by_id(self):
    documents = self.db.get(self.framework_id).get("documents")
    for doc in documents:
        response = self.app.get("/frameworks/{}/documents/{}".format(self.framework_id, doc["id"]))
        document = response.json["data"]
        self.assertEqual(doc["id"], document["id"])
        self.assertEqual(doc["title"], document["title"])
        self.assertEqual(doc["format"], document["format"])
        self.assertEqual(doc["datePublished"], document["datePublished"])


def create_framework_document_forbidden(self):
    with change_auth(self.app, ("Basic", ("broker1", ""))):
        response = self.app.post(
            "/frameworks/{}/documents".format(self.framework_id),
            upload_files=[("file", u"укр.doc", "content")],
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")


def create_framework_document(self):
    response = self.app.post(
        "/frameworks/{}/documents".format(self.framework_id),
        upload_files=[("file", u"укр.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def create_framework_document_json_bulk(self):
    response = self.app.post_json(
        "/frameworks/{}/documents?acc_token={}".format(self.framework_id, self.framework_token),
        {
            "data": [
                {
                    "title": "name1.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                },
                {
                    "title": "name2.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            ]
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]

    def assert_document(document, title):
        self.assertEqual(title, document["title"])
        self.assertIn("Signature=", document["url"])
        self.assertIn("KeyID=", document["url"])
        self.assertNotIn("Expires=", document["url"])

    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")

    framework = self.db.get(self.framework_id)
    doc_1 = framework["documents"][0]
    doc_2 = framework["documents"][1]
    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")

    response = self.app.get("/frameworks/{}/documents".format(self.framework_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]
    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")


def not_found(self):
    response = self.app.get("/frameworks/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"framework_id"}]
    )

    response = self.app.post(
        "/frameworks/some_id/documents", status=404, upload_files=[("file", "name.doc", "content")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"framework_id"}]
    )
    response = self.app.post(
        "/frameworks/{}/documents".format(self.framework_id),
        status=404,
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])
    response = self.app.put(
        "/frameworks/some_id/documents/some_id", status=404, upload_files=[("file", "name.doc", "content2")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"framework_id"}]
    )

    response = self.app.put(
        "/frameworks/{}/documents/some_id".format(self.framework_id),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )

    response = self.app.get("/frameworks/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"framework_id"}]
    )

    response = self.app.get("/frameworks/{}/documents/some_id".format(self.framework_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )


def put_contract_document(self):
    from six import BytesIO
    from urllib import quote

    body = u"""--BOUNDARY\nContent-Disposition: form-data; name="file"; filename={}\nContent-Type: application/msword\n\ncontent\n""".format(
        u"\uff07"
    )
    environ = self.app._make_environ()
    environ["CONTENT_TYPE"] = "multipart/form-data; boundary=BOUNDARY"
    environ["REQUEST_METHOD"] = "POST"
    req = self.app.RequestClass.blank(
        self.app._remove_fragment("/frameworks/{}/documents".format(self.framework_id)), environ
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
            "/frameworks/{}/documents?acc_token={}".format(self.framework_id, self.framework_token)
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
        "/frameworks/{}/documents/{}?acc_token={}".format(self.framework_id, doc_id, self.framework_token),
        upload_files=[("file", "name name.doc", "content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    if self.docservice:
        self.assertIn("Signature=", response.json["data"]["url"])
        self.assertIn("KeyID=", response.json["data"]["url"])
        self.assertNotIn("Expires=", response.json["data"]["url"])
        key = response.json["data"]["url"].split("/")[-1].split("?")[0]
        framework = self.db.get(self.framework_id)
        self.assertIn(key, framework["documents"][-1]["url"])
        self.assertIn("Signature=", framework["documents"][-1]["url"])
        self.assertIn("KeyID=", framework["documents"][-1]["url"])
        self.assertNotIn("Expires=", framework["documents"][-1]["url"])
    response = self.app.get("/frameworks/{}/documents/{}".format(self.framework_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name name.doc", response.json["data"]["title"])
    dateModified2 = response.json["data"]["dateModified"]
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]["dateModified"])

    response = self.app.get("/frameworks/{}/documents?all=true".format(self.framework_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified2, response.json["data"][1]["dateModified"])

    response = self.app.post(
        "/frameworks/{}/documents?acc_token={}".format(self.framework_id, self.framework_token),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.get("/frameworks/{}/documents".format(self.framework_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified2, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified, response.json["data"][1]["dateModified"])
    response = self.app.put(
        "/frameworks/{}/documents/{}?acc_token={}".format(self.framework_id, doc_id, self.framework_token),
        status=404,
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])
    response = self.app.put(
        "/frameworks/{}/documents/{}?acc_token={}".format(self.framework_id, doc_id, self.framework_token),
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
        framework = self.db.get(self.framework_id)
        self.assertIn(key, framework["documents"][-1]["url"])
        self.assertIn("Signature=", framework["documents"][-1]["url"])
        self.assertIn("KeyID=", framework["documents"][-1]["url"])
        self.assertNotIn("Expires=", framework["documents"][-1]["url"])
    else:
        key = response.json["data"]["url"].split("?")[-1].split("=")[-1]
    if self.docservice:
        response = self.app.get("/frameworks/{}/documents/{}".format(self.framework_id, doc_id, key))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/frameworks/{}/documents".format(self.framework_id, self.framework_token))
    self.assertEqual(response.status, "200 OK")
    doc_id = response.json["data"][0]["id"]
    response = self.app.patch_json(
        "/frameworks/{}/documents/{}?acc_token={}".format(self.framework_id, doc_id, self.framework_token),
        {"data": {"documentType": None}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.set_status("complete")
    response = self.app.put(
        "/frameworks/{}/documents/{}?acc_token={}".format(self.framework_id, doc_id, self.framework_token),
        "contentX",
        content_type="application/msword",
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can't update document in current (complete) framework status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )
    #  document in current (complete) framework status
    response = self.app.patch_json(
        "/frameworks/{}/documents/{}?acc_token={}".format(self.framework_id, doc_id, self.framework_token),
        {"data": {"documentType": None}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can't update document in current (complete)" u" framework status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )
