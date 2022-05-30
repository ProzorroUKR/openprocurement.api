# -*- coding: utf-8 -*-
from email.header import Header


# PlanDocumentResourceTest


def not_found(self):
    response = self.app.get("/plans/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "plan_id"}]
    )

    response = self.app.post("/plans/some_id/documents", status=404, upload_files=[("file", "name.doc", b"content")])
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "plan_id"}]
    )

    response = self.app.post(
        "/plans/{}/documents".format(self.plan_id), status=404, upload_files=[("invalid_name", "name.doc", b"content")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "body", "name": "file"}])

    response = self.app.put(
        "/plans/some_id/documents/some_id", status=404, upload_files=[("file", "name.doc", b"content2")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "plan_id"}]
    )

    response = self.app.put(
        "/plans/{}/documents/some_id".format(self.plan_id), status=404, upload_files=[("file", "name.doc", b"content2")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
    )

    response = self.app.get("/plans/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "plan_id"}]
    )

    response = self.app.get("/plans/{}/documents/some_id".format(self.plan_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
    )


def create_plan_document(self):
    response = self.app.get("/plans/{}/documents".format(self.plan_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json, {"data": []})

    response = self.app.post("/plans/{}/documents".format(self.plan_id), upload_files=[("file", "укр.doc", b"content")])
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("укр.doc", response.json["data"]["title"])

    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    plan = self.mongodb.plans.get(self.plan_id)
    self.assertIn(key, plan["documents"][-1]["url"])
    self.assertIn("Signature=", plan["documents"][-1]["url"])
    self.assertIn("KeyID=", plan["documents"][-1]["url"])
    self.assertNotIn("Expires=", plan["documents"][-1]["url"])

    response = self.app.get("/plans/{}/documents".format(self.plan_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("укр.doc", response.json["data"][0]["title"])

    response = self.app.get("/plans/{}/documents/{}?download=some_id".format(self.plan_id, doc_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}]
    )

    response = self.app.get("/plans/{}/documents/{}?download={}".format(self.plan_id, doc_id, key))
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertNotIn("Expires=", response.location)

    response = self.app.get("/plans/{}/documents/{}".format(self.plan_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("укр.doc", response.json["data"]["title"])

    response = self.app.post(
        "/plans/{}/documents?acc_token=acc_token".format(self.plan_id),
        upload_files=[("file", "укр.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertNotIn("acc_token", response.headers["Location"])


def put_plan_document(self):
    response = self.app.post(
        "/plans/{}/documents".format(self.plan_id), upload_files=[("file", "укр.doc", b"content")]
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/plans/{}/documents/{}".format(self.plan_id, doc_id), upload_files=[("file", "name name.doc", b"content2")]
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    plan = self.mongodb.plans.get(self.plan_id)
    self.assertIn(key, plan["documents"][-1]["url"])
    self.assertIn("Signature=", plan["documents"][-1]["url"])
    self.assertIn("KeyID=", plan["documents"][-1]["url"])
    self.assertNotIn("Expires=", plan["documents"][-1]["url"])

    response = self.app.get("/plans/{}/documents/{}?download={}".format(self.plan_id, doc_id, key))
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertNotIn("Expires=", response.location)

    response = self.app.get("/plans/{}/documents/{}".format(self.plan_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name name.doc", response.json["data"]["title"])
    dateModified2 = response.json["data"]["dateModified"]
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]["dateModified"])

    response = self.app.get("/plans/{}/documents?all=true".format(self.plan_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified2, response.json["data"][1]["dateModified"])

    response = self.app.post("/plans/{}/documents".format(self.plan_id), upload_files=[("file", "name.doc", b"content")])
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.get("/plans/{}/documents".format(self.plan_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified2, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified, response.json["data"][1]["dateModified"])

    response = self.app.put(
        "/plans/{}/documents/{}".format(self.plan_id, doc_id),
        status=404,
        upload_files=[("invalid_name", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "body", "name": "file"}])

    response = self.app.put(
        "/plans/{}/documents/{}".format(self.plan_id, doc_id), "content3", content_type="application/msword"
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    self.assertIn("Signature=", response.json["data"]["url"])
    self.assertIn("KeyID=", response.json["data"]["url"])
    self.assertNotIn("Expires=", response.json["data"]["url"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    plan = self.mongodb.plans.get(self.plan_id)
    self.assertIn(key, plan["documents"][-1]["url"])
    self.assertIn("Signature=", plan["documents"][-1]["url"])
    self.assertIn("KeyID=", plan["documents"][-1]["url"])
    self.assertNotIn("Expires=", plan["documents"][-1]["url"])

    response = self.app.get("/plans/{}/documents/{}?download={}".format(self.plan_id, doc_id, key))
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertNotIn("Expires=", response.location)


def patch_plan_document(self):
    response = self.app.post(
        "/plans/{}/documents".format(self.plan_id), upload_files=[("file", str(Header("укр.doc", "utf-8")), b"content")]
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("укр.doc", response.json["data"]["title"])
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.patch_json(
        "/plans/{}/documents/{}".format(self.plan_id, doc_id),
        {"data": {"description": "document description", "documentType": "notice"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertIn("documentType", response.json["data"])
    self.assertEqual(response.json["data"]["documentType"], "notice")

    response = self.app.patch_json(
        "/plans/{}/documents/{}".format(self.plan_id, doc_id), {"data": {"documentType": None}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertNotIn("documentType", response.json["data"])

    response = self.app.get("/plans/{}/documents/{}".format(self.plan_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])


# PlanDocumentWithDSResourceTest


def create_plan_document_json_invalid(self):
    response = self.app.post_json(
        "/plans/{}/documents".format(self.plan_id),
        {"data": {"title": "укр.doc", "url": self.generate_docservice_url(), "format": "application/msword"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "This field is required.")

    response = self.app.post_json(
        "/plans/{}/documents".format(self.plan_id),
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
        "/plans/{}/documents".format(self.plan_id),
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
        "/plans/{}/documents".format(self.plan_id),
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
        "/plans/{}/documents".format(self.plan_id),
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
        "/plans/{}/documents".format(self.plan_id),
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
        "/plans/{}/documents".format(self.plan_id),
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


def create_plan_document_json(self):
    response = self.app.post_json(
        "/plans/{}/documents".format(self.plan_id),
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
    plan = self.mongodb.plans.get(self.plan_id)
    self.assertIn(key, plan["documents"][-1]["url"])
    self.assertIn("Signature=", plan["documents"][-1]["url"])
    self.assertIn("KeyID=", plan["documents"][-1]["url"])
    self.assertNotIn("Expires=", plan["documents"][-1]["url"])

    response = self.app.get("/plans/{}/documents".format(self.plan_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("укр.doc", response.json["data"][0]["title"])

    response = self.app.get("/plans/{}/documents/{}?download=some_id".format(self.plan_id, doc_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}]
    )

    response = self.app.get("/plans/{}/documents/{}?download={}".format(self.plan_id, doc_id, key))
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertNotIn("Expires=", response.location)

    response = self.app.get("/plans/{}/documents/{}".format(self.plan_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("укр.doc", response.json["data"]["title"])

    response = self.app.post_json(
        "/plans/{}/documents".format(self.plan_id),
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


def put_plan_document_json(self):
    response = self.app.post_json(
        "/plans/{}/documents".format(self.plan_id),
        {
            "data": {
                "title": "name name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("name name.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put_json(
        "/plans/{}/documents/{}".format(self.plan_id, doc_id),
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
    plan = self.mongodb.plans.get(self.plan_id)
    self.assertIn(key, plan["documents"][-1]["url"])
    self.assertIn("Signature=", plan["documents"][-1]["url"])
    self.assertIn("KeyID=", plan["documents"][-1]["url"])
    self.assertNotIn("Expires=", plan["documents"][-1]["url"])

    response = self.app.get("/plans/{}/documents/{}?download={}".format(self.plan_id, doc_id, key))
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertNotIn("Expires=", response.location)

    response = self.app.get("/plans/{}/documents/{}".format(self.plan_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])
    dateModified2 = response.json["data"]["dateModified"]
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]["dateModified"])

    response = self.app.get("/plans/{}/documents?all=true".format(self.plan_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified2, response.json["data"][1]["dateModified"])

    response = self.app.post_json(
        "/plans/{}/documents".format(self.plan_id),
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

    response = self.app.get("/plans/{}/documents".format(self.plan_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified2, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified, response.json["data"][1]["dateModified"])

    response = self.app.put_json(
        "/plans/{}/documents/{}".format(self.plan_id, doc_id),
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
    plan = self.mongodb.plans.get(self.plan_id)
    self.assertIn(key, plan["documents"][-1]["url"])
    self.assertIn("Signature=", plan["documents"][-1]["url"])
    self.assertIn("KeyID=", plan["documents"][-1]["url"])
    self.assertNotIn("Expires=", plan["documents"][-1]["url"])

    response = self.app.get("/plans/{}/documents/{}?download={}".format(self.plan_id, doc_id, key))
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)
    self.assertNotIn("Expires=", response.location)
