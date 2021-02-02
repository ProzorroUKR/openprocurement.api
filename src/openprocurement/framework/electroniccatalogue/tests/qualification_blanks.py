# -*- coding: utf-8 -*-

from copy import deepcopy
from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import change_auth
from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.framework.electroniccatalogue.tests.base import test_electronicCatalogue_documents
from datetime import timedelta
from uuid import uuid4


def listing(self):
    response = self.app.get("/qualifications")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    qualifications = []

    data = deepcopy(self.initial_submission_data)

    tenderer_ids = ["00037256", "00037257", "00037258"]

    for i in tenderer_ids:

        data["tenderers"][0]["identifier"]["id"] = i
        offset = get_now().isoformat()
        response = self.app.post_json("/submissions", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(response.json["data"]["id"], response.json["access"]["token"]),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["status"], "active")
        qualification_id = response.json["data"]["qualificationID"]

        response = self.app.patch_json(
            "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
            {"data": {"status": "active"}}
        )
        qualifications.append(response.json["data"])

    ids = ",".join([i["id"] for i in qualifications])

    while True:
        response = self.app.get("/qualifications")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in qualifications]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in qualifications])
    )
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in qualifications])
    )

    while True:
        response = self.app.get("/qualifications?offset={}".format(offset))
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/qualifications?limit=2")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("prev_page", response.json)
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/qualifications", params=[("opt_fields", "status")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/qualifications", params=[("opt_fields", "status,owner")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/qualifications?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in qualifications]))
    self.assertEqual(
        [i["dateModified"]
         for i in response.json["data"]], sorted([i["dateModified"] for i in qualifications], reverse=True)
    )

    response = self.app.get("/qualifications?descending=1&limit=2")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 0)


def listing_changes(self):
    response = self.app.get("/qualifications")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    qualifications = []

    data = deepcopy(self.initial_submission_data)

    tenderer_ids = ["00037256", "00037257", "00037258"]

    for i in tenderer_ids:
        data["tenderers"][0]["identifier"]["id"] = i
        offset = get_now().isoformat()
        response = self.app.post_json("/submissions", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(response.json["data"]["id"], response.json["access"]["token"]),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        qualification_id = response.json["data"]["qualificationID"]

        response = self.app.patch_json(
            "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
            {"data": {"status": "active"}}
        )
        qualifications.append(response.json["data"])

    ids = ",".join([i["id"] for i in qualifications])

    while True:
        response = self.app.get("/qualifications?feed=changes")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in qualifications]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in qualifications])
    )
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in qualifications])
    )

    response = self.app.get("/qualifications?feed=changes&limit=2")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("prev_page", response.json)
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/qualifications?feed=changes", params=[("opt_fields", "status")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/qualifications?feed=changes", params=[("opt_fields", "status,owner")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/qualifications?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in qualifications]))
    self.assertEqual(
        [i["dateModified"]
         for i in response.json["data"]], sorted([i["dateModified"] for i in qualifications], reverse=True)
    )

    response = self.app.get("/qualifications?feed=changes&descending=1&limit=2")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 2)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertEqual(len(response.json["data"]), 0)


def patch_submission_pending(self):
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification_id = response.json["data"]["qualificationID"]

    qualification_ignore_patch_data = {
        "date": (get_now() + timedelta(days=2)).isoformat(),
        "dateModified": (get_now() + timedelta(days=1)).isoformat(),
        "frameworkID": "0"*32,
        "submissionID": "0"*32,
        "qualificationType": "changed",
    }
    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": qualification_ignore_patch_data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification = self.app.get("/qualifications/{}".format(qualification_id)).json["data"]
    for field in qualification_ignore_patch_data:
        self.assertNotEqual(qualification.get(field, ""), qualification_ignore_patch_data[field])

    qualification_patch_data = {
        "status": "active"
    }

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": qualification_patch_data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification = self.app.get("/qualifications/{}".format(qualification_id, self.framework_token)).json["data"]
    self.assertEqual(qualification["status"], "active")

    submission = self.app.get("/submissions/{}".format(self.submission_id)).json["data"]
    self.assertEqual(submission["status"], "complete")

    submission_data = deepcopy(self.initial_submission_data)
    submission_data["tenderers"][0]["identifier"]["id"] = "00037258"
    response = self.app.post_json("/submissions", {"data": submission_data})
    self.assertEqual(response.status, "201 Created")
    submission_id = response.json["data"]["id"]
    submission_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission_id, submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    qualification_id = response.json["data"]["qualificationID"]
    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {"status": "unsuccessful"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification = self.app.get("/qualifications/{}".format(qualification_id, self.framework_token)).json["data"]
    self.assertEqual(qualification["status"], "unsuccessful")

    submission = self.app.get("/submissions/{}".format(submission_id)).json["data"]
    self.assertEqual(submission["status"], "complete")


def patch_qualification_active(self):
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification_id = response.json["data"]["qualificationID"]

    response = self.app.post(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        upload_files=[("file", "name  name.doc", b"content")]
    )
    self.assertEqual(response.status, "201 Created")
    document_id = response.json["data"]["id"]

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            u'description': u"Can't update qualification in current (active) status",
            u'location': u'body',
            u'name': u'data',
        }]
    )

    response = self.app.post(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        upload_files=[("file", "name  name2.doc", b"content2")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{
            u'description': u"Can't add document in current (active) qualification status",
            u'location': u'body',
            u'name': u'data'
        }]
    )

    response = self.app.patch_json(
        "/qualifications/{}/documents/{}?acc_token={}".format(qualification_id, document_id, self.framework_token),
        {"data": {"name": "name2.doc"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [{
            u'description': u"Can't update document in current (active) qualification status",
            u'location': u'body',
            u'name': u'data'
        }]
    )


def patch_qualification_unsuccessful(self):
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification_id = response.json["data"]["qualificationID"]

    response = self.app.post(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        upload_files=[("file", "name  name.doc", b"content")]
    )
    self.assertEqual(response.status, "201 Created")
    document_id = response.json["data"]["id"]

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            u'description': u"Can't update qualification in current (unsuccessful) status",
            u'location': u'body',
            u'name': u'data',
        }]
    )

    response = self.app.post(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        upload_files=[("file", "name  name2.doc", b"content2")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{
            u'description': u"Can't add document in current (unsuccessful) qualification status",
            u'location': u'body',
            u'name': u'data'
        }]
    )

    response = self.app.patch_json(
        "/qualifications/{}/documents/{}?acc_token={}".format(qualification_id, document_id, self.framework_token),
        {"data": {"name": "name2.doc"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [{
            u'description': u"Can't update document in current (unsuccessful) qualification status",
            u'location': u'body',
            u'name': u'data'
        }]
    )


def get_qualification(self):
    response = self.app.get("/qualifications")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification_id = response.json["data"]["qualificationID"]

    response = self.app.get("/qualifications/{}".format(qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["frameworkID"], self.framework_id)
    self.assertEqual(response.json["data"]["submissionID"], self.submission_id)

    response = self.app.get("/qualifications/{}?opt_jsonp=callback".format(qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"data": {"', response.body.decode())

    response = self.app.get("/qualifications/{}?opt_pretty=1".format(qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "data": {\n        "', response.body.decode())


def qualification_fields(self):
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification_id = response.json["data"]["qualificationID"]

    response = self.app.get("/qualifications/{}".format(qualification_id))
    self.assertEqual(response.status, "200 OK")
    qualification = response.json["data"]

    fields = set(
            [
                u"id",
                u"dateModified",
                u"date",
                u"status",
                u"qualificationType",
                u"submissionID",
                u"frameworkID",
            ]
        )
    self.assertEqual(set(qualification), fields)

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification["id"], self.framework_token), {"data": {"status": "active"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification= response.json["data"]
    self.assertEqual(set(qualification), fields)


def date_qualification(self):
    response = self.app.get("/qualifications")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification_id = response.json["data"]["qualificationID"]

    response = self.app.get("/qualifications/{}".format(qualification_id))
    self.assertEqual(response.status, "200 OK")
    qualification = response.json["data"]
    date = qualification["date"]

    response = self.app.post(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        upload_files=[("file", "name  name.doc", b"content")]
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.get("/qualifications/{}".format(qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], date)

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], date)

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["date"], date)


def dateModified_qualification(self):
    response = self.app.get("/qualifications")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification_id = response.json["data"]["qualificationID"]

    response = self.app.get("/qualifications/{}".format(qualification_id))
    self.assertEqual(response.status, "200 OK")
    qualification = response.json["data"]
    dateModified = qualification["dateModified"]

    response = self.app.post(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        upload_files=[("file", "name  name.doc", b"content")]
    )
    self.assertEqual(response.status, "201 Created")

    response = self.app.get("/qualifications/{}".format(qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["dateModified"], dateModified)
    qualification = response.json["data"]
    dateModified = qualification["dateModified"]

    response = self.app.get("/qualifications/{}".format(qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], qualification)
    self.assertEqual(response.json["data"]["dateModified"], dateModified)

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["dateModified"], dateModified)

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["dateModified"], dateModified)
    qualification = response.json["data"]
    dateModified = qualification["dateModified"]

    response = self.app.get("/qualifications/{}".format(qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], qualification)
    self.assertEqual(response.json["data"]["dateModified"], dateModified)


def qualification_not_found(self):
    response = self.app.get("/qualifications")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/qualifications/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.patch_json("/qualifications/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    # put custom document object into database to check frameworks construction on non-Submission data
    data = {"contract": "test", "_id": uuid4().hex}
    self.db.save(data)

    response = self.app.get("/submissions/{}".format(data["_id"]), status=404)
    self.assertEqual(response.status, "404 Not Found")


def qualification_token_invalid(self):
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification_id = response.json["data"]["qualificationID"]

    response = self.app.get("/qualifications/{}".format(qualification_id))
    self.assertEqual(response.status, "200 OK")
    qualification = response.json["data"]

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.submission_token), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}]
    )

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, ""), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}]
    )

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, "токен з кирилицею"), {"data": {}}, status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"], [
            {
                'location': 'body', 'name': 'UnicodeEncodeError',
                'description': "'latin-1' codec can't encode characters in position 10-14: ordinal not in range(256)"
            }
        ]
    )


def get_documents_list(self):

    self.app.post(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
        upload_files=[("file", "name name.doc", b"content2")],
    )

    response = self.app.get("/qualifications/{}/documents".format(self.qualification_id))
    documents = response.json["data"]
    self.assertEqual(len(documents), 1)


def get_document_by_id(self):
    self.app.post(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
        upload_files=[("file", "name%s.doc" % i, b"content2") for i in range(3)],
    )
    documents = self.db.get(self.qualification_id).get("documents")
    for doc in documents:
        response = self.app.get("/qualifications/{}/documents/{}".format(self.qualification_id, doc["id"]))
        document = response.json["data"]
        self.assertEqual(doc["id"], document["id"])
        self.assertEqual(doc["title"], document["title"])
        self.assertEqual(doc["format"], document["format"])
        self.assertEqual(doc["datePublished"], document["datePublished"])


def create_qualification_document_forbidden(self):
    response = self.app.post(
        "/qualifications/{}/documents".format(self.qualification_id),
        upload_files=[("file", u"укр.doc", b"content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}],
    )

    with change_auth(self.app, ("Basic", ("broker1", ""))):
        response = self.app.post(
            "/qualifications/{}/documents".format(self.qualification_id),
            upload_files=[("file", u"укр.doc", b"content")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}],
        )


def create_qualification_document(self):
    response = self.app.post(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
        upload_files=[("file", u"укр.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.post(
            "/qualifications/{}/documents".format(self.qualification_id),
            upload_files=[("file", u"укр.doc", b"content")],
        )
        self.assertEqual(response.status, "201 Created")


def create_qualification_document_json_bulk(self):
    response = self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
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

    qualification = self.db.get(self.qualification_id)
    doc_1 = qualification["documents"][0]
    doc_2 = qualification["documents"][1]
    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")

    response = self.app.get("/qualifications/{}/documents".format(self.qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]
    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")


def document_not_found(self):
    response = self.app.get("/qualifications/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.post(
        "/qualifications/some_id/documents", status=404, upload_files=[("file", "name.doc", b"content")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )
    response = self.app.post(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
        status=404,
        upload_files=[("invalid_name", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])
    response = self.app.put(
        "/qualifications/some_id/documents/some_id", status=404, upload_files=[("file", "name.doc", b"content2")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.put(
        "/qualifications/{}/documents/some_id".format(self.qualification_id),
        status=404,
        upload_files=[("file", "name.doc", b"content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )

    response = self.app.get("/qualifications/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"qualification_id"}]
    )

    response = self.app.get("/qualifications/{}/documents/some_id".format(self.qualification_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )


def put_qualification_document(self):
    response = self.app.post(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
        upload_files=[("file", "укр.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(u"укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/qualifications/{}/documents/{}?acc_token={}".format(self.qualification_id, doc_id, self.framework_token),
        upload_files=[("file", "name name.doc", b"content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    if self.docservice:
        self.assertIn("Signature=", response.json["data"]["url"])
        self.assertIn("KeyID=", response.json["data"]["url"])
        self.assertNotIn("Expires=", response.json["data"]["url"])
        key = response.json["data"]["url"].split("/")[-1].split("?")[0]
        qualification = self.db.get(self.qualification_id)
        self.assertIn(key, qualification["documents"][-1]["url"])
        self.assertIn("Signature=", qualification["documents"][-1]["url"])
        self.assertIn("KeyID=", qualification["documents"][-1]["url"])
        self.assertNotIn("Expires=", qualification["documents"][-1]["url"])
    response = self.app.get("/qualifications/{}/documents/{}".format(self.qualification_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name name.doc", response.json["data"]["title"])
    dateModified2 = response.json["data"]["dateModified"]
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]["dateModified"])

    response = self.app.get("/qualifications/{}/documents?all=true".format(self.qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified2, response.json["data"][1]["dateModified"])

    response = self.app.post(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.get("/qualifications/{}/documents".format(self.qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified2, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified, response.json["data"][1]["dateModified"])
    response = self.app.put(
        "/qualifications/{}/documents/{}?acc_token={}".format(self.qualification_id, doc_id, self.framework_token),
        status=404,
        upload_files=[("invalid_name", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])
    response = self.app.put(
        "/qualifications/{}/documents/{}?acc_token={}".format(self.qualification_id, doc_id, self.framework_token),
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
        qualification = self.db.get(self.qualification_id)
        self.assertIn(key, qualification["documents"][-1]["url"])
        self.assertIn("Signature=", qualification["documents"][-1]["url"])
        self.assertIn("KeyID=", qualification["documents"][-1]["url"])
        self.assertNotIn("Expires=", qualification["documents"][-1]["url"])
    else:
        key = response.json["data"]["url"].split("?")[-1].split("=")[-1]
    if self.docservice:
        response = self.app.get("/qualifications/{}/documents/{}".format(self.qualification_id, doc_id, key))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/qualifications/{}/documents".format(self.qualification_id, self.framework_token))
    self.assertEqual(response.status, "200 OK")
    doc_id = response.json["data"][0]["id"]
    response = self.app.patch_json(
        "/qualifications/{}/documents/{}?acc_token={}".format(self.qualification_id, doc_id, self.framework_token),
        {"data": {"documentType": None}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(self.qualification_id, self.framework_token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put(
        "/qualifications/{}/documents/{}?acc_token={}".format(self.qualification_id, doc_id, self.framework_token),
        "contentX",
        content_type="application/msword",
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can't update document in current (active) qualification status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )
    #  document in current (complete) framework status
    response = self.app.patch_json(
        "/qualifications/{}/documents/{}?acc_token={}".format(self.qualification_id, doc_id, self.framework_token),
        {"data": {"documentType": None}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can't update document in current (active) qualification status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )
