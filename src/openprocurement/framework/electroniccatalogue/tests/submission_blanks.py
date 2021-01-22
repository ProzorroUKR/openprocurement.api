# -*- coding: utf-8 -*-
from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from openprocurement.api.utils import get_now
from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.tests.base import change_auth


def listing(self):
    response = self.app.get("/submissions")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    submissions = []

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
        submissions.append(response.json["data"])

    ids = ",".join([i["id"] for i in submissions])

    while True:
        response = self.app.get("/submissions")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in submissions]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in submissions])
    )
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in submissions])
    )

    while True:
        response = self.app.get("/submissions?offset={}".format(offset))
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/submissions?limit=2")
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

    response = self.app.get("/submissions", params=[("opt_fields", "status")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/submissions", params=[("opt_fields", "status,owner")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/submissions?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in submissions]))
    self.assertEqual(
        [i["dateModified"]
         for i in response.json["data"]], sorted([i["dateModified"] for i in submissions], reverse=True)
    )

    response = self.app.get("/submissions?descending=1&limit=2")
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
    response = self.app.get("/submissions")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    submissions = []

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
        submissions.append(response.json["data"])

    ids = ",".join([i["id"] for i in submissions])

    while True:
        response = self.app.get("/submissions?feed=changes")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in submissions]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in submissions])
    )
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in submissions])
    )

    response = self.app.get("/submissions?feed=changes&limit=2")
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

    response = self.app.get("/submissions?feed=changes", params=[("opt_fields", "status")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/submissions?feed=changes", params=[("opt_fields", "status,owner")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/submissions?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in submissions]))
    self.assertEqual(
        [i["dateModified"]
         for i in response.json["data"]], sorted([i["dateModified"] for i in submissions], reverse=True)
    )

    response = self.app.get("/submissions?feed=changes&descending=1&limit=2")
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


def listing_draft(self):
    response = self.app.get("/submissions")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    submissions = []

    data = deepcopy(self.initial_submission_data)
    data["frameworkID"] = self.framework_id

    tenderer_ids = ["00037256", "00037257", "00037258"]

    for i in tenderer_ids:
        # Active frameworks
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
        submissions.append(response.json["data"])
        # Draft submissions
        response = self.app.post_json("/submissions", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    ids = ",".join([i["id"] for i in submissions])

    while True:
        response = self.app.get("/submissions")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in submissions]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in submissions])
    )
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in submissions])
    )


def create_submission_draft_invalid(self):
    request_path = "/submissions"
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

    response = self.app.post_json(request_path, {"data": []}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Data not available", u"location": u"body", u"name": u"data"}]
    )

    response = self.app.post_json(request_path, {"data": {"submissionType": "invalid_value"}}, status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"Not implemented", u"location": u"body", u"name": u"submissionType"}],
    )

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"qualificationID": "0" * 32}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"tenderers"},
        response.json["errors"],
    )
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"frameworkID"},
        response.json["errors"],
    )

    data = deepcopy(self.initial_submission_data)
    data["tenderers"] = u"This is string"
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u'description': [u'Please use a mapping for this field or BusinessOrganization instance instead of unicode.'],
          u'location': u'body',
          u'name': u'tenderers'}],
    )

    data = deepcopy(self.initial_submission_data)
    data["frameworkID"] = "some_id"
    response = self.app.post_json(request_path, {"data": data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{
            u'description': u'frameworkID must be one of exists frameworks',
            u'location': u'body',
            u'name': u'data',
        }],
    )

    data = deepcopy(self.initial_submission_data)
    del data["tenderers"][0]["name"]
    del data["tenderers"][0]["address"]
    del data["tenderers"][0]["contactPoint"]
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{
            u'description':
                [
                    {
                        u'address': [u'This field is required.'],
                        u'contactPoint': [u'This field is required.'],
                        u'name': [u'This field is required.'],
                    }
                ],
            u'location': u'body',
            u'name': u'tenderers',
        }],
    )


def create_submission_draft(self):
    response = self.app.post_json("/submissions", {"data": self.initial_submission_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(submission["status"], "draft")
    self.assertNotIn("qualificationID", submission)

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "active")

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "active")


def patch_submission_draft(self):
    data = deepcopy(self.initial_submission_data)
    response = self.app.post_json("/submissions", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(submission["status"], "draft")

    submission_ignore_patch_data = {
        "date": (get_now() + timedelta(days=2)).isoformat(),
        "dateModified": (get_now() + timedelta(days=1)).isoformat(),
        "datePublished": (get_now() + timedelta(days=1)).isoformat(),
        "owner": "changed",
        "qualificationID": "0"*32,
        "submissionType": "changed",
    }
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": submission_ignore_patch_data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = self.app.get("/submissions/{}".format(submission["id"], token)).json["data"]
    for field in submission_ignore_patch_data:
        self.assertNotEqual(submission.get(field, ""), submission_ignore_patch_data[field])

    submission_patch_data = {
        u"tenderers": [{
            u"name": u"Оновленна назва",
            u"name_en": u"Updated name",
            u"identifier": {
                u"legalName_en": u"dus.gov.ua",
                u"legalName": u"Оновлено",
                u"scheme": u"UA-EDR",
                u"id": u"00037260",
                u"uri": u"http://www.dus.gov.ua/"
            },
            u"address": {
                u"countryName": u"Україна",
                u"postalCode": u"01229",
                u"region": u"м. Київ",
                u"locality": u"м. Київ",
                u"streetAddress": u"вул. Андрія Малишка, 11, корпус 1"
            },
            u"contactPoint": {
                u"name": u"Оновлена назва",
                u"name_en": u"State administration",
                u"telephone": u"0440000001",
                u"email": u"someemaill@test.com",
            },
            u"scale": u"micro"
        }],
        u"frameworkID": u"0"*32,
    }
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": submission_patch_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{
            u'description': u'frameworkID must be one of exists frameworks',
            u'location': u'body',
            u'name': u'data'
        }],
    )

    del submission_patch_data["frameworkID"]

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": submission_patch_data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = self.app.get("/submissions/{}".format(submission["id"], token)).json["data"]
    contact = submission["tenderers"][0]["contactPoint"]
    self.assertEqual(contact["telephone"], submission_patch_data["tenderers"][0]["contactPoint"]["telephone"])
    self.assertEqual(contact["name"], submission_patch_data["tenderers"][0]["contactPoint"]["name"])
    self.assertEqual(contact["email"], submission_patch_data["tenderers"][0]["contactPoint"]["email"])
    identifier = submission["tenderers"][0]["identifier"]
    self.assertEqual(identifier["legalName"], submission_patch_data["tenderers"][0]["identifier"]["legalName"])
    address = submission["tenderers"][0]["address"]
    self.assertEqual(address["postalCode"], submission_patch_data["tenderers"][0]["address"]["postalCode"])
    self.assertEqual(address["streetAddress"], submission_patch_data["tenderers"][0]["address"]["streetAddress"])
    self.assertEqual(address["locality"], submission_patch_data["tenderers"][0]["address"]["locality"])


def patch_framework_draft_to_active(self):
    data = deepcopy(self.initial_submission_data)
    response = self.app.post_json("/submissions", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(submission["status"], "draft")
    self.assertNotIn("qualificationID", submission)

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotEqual(response.json["data"]["date"], submission["date"])
    self.assertNotEqual(response.json["data"]["dateModified"], submission["dateModified"])
    self.assertIn("qualificationID", response.json["data"])
    self.assertEqual(len(response.json["data"]["qualificationID"]), 32)

    response = self.app.post_json("/submissions", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": {"status": "deleted"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


def patch_submission_draft_to_active_invalid(self):
    data = deepcopy(self.initial_submission_data)
    response = self.app.post_json("/submissions", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(submission["status"], "draft")

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.post_json("/submissions", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(submission["status"], "draft")

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            u'description': u'Tenderer already have active submission for framework %s' % self.framework_id,
            u'location': u'body',
            u'name': u'data',
        }]
    )


def patch_submission_active(self):
    data = deepcopy(self.initial_submission_data)
    response = self.app.post_json("/submissions", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(submission["status"], "draft")

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "active")

    data["tenderers"][0]["name"] = u"Updated name"

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            u'description': u"Can't update submission in current (active) status",
            u'location': u'body',
            u'name': u'data',
        }]
    )

    statuses = ("active", "draft", "deleted", "complete")

    for status in statuses:
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{
                u'description': u"Can't update submission in current (active) status",
                u'location': u'body',
                u'name': u'data',
            }]
        )


def patch_submission_draft_to_deleted(self):
    data = deepcopy(self.initial_submission_data)
    response = self.app.post_json("/submissions", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(submission["status"], "draft")

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "deleted"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "deleted")


def patch_submission_deleted(self):
    data = deepcopy(self.initial_submission_data)
    response = self.app.post_json("/submissions", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(submission["status"], "draft")

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "deleted"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "deleted")

    data["tenderers"][0]["name"] = u"Updated name"

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            u'description': u"Can't update submission in current (deleted) status",
            u'location': u'body',
            u'name': u'data',
        }]
    )

    statuses = ("active", "draft", "deleted", "complete")

    for status in statuses:
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{
                u'description': u"Can't update submission in current (deleted) status",
                u'location': u'body',
                u'name': u'data',
            }]
        )


def patch_submission_complete(self):
    data = deepcopy(self.initial_submission_data)
    response = self.app.post_json("/submissions", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(submission["status"], "draft")

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "active")
    qualification_id = submission["qualificationID"]

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(submission["status"], "active")

    statuses = ("active", "draft", "deleted", "complete")

    for status in statuses:
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{
                u'description': u"Can't update submission in current (complete) status",
                u'location': u'body',
                u'name': u'data',
            }]
        )


def submission_fields(self):
    response = self.app.post_json("/submissions", {"data": self.initial_submission_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    fields = set(
            [
                u"id",
                u"dateModified",
                u"date",
                u"status",
                u"submissionType",
                u"owner",
            ]
        )
    self.assertEqual(set(submission) - set(self.initial_submission_data), fields)
    self.assertIn(submission["id"], response.headers["Location"])

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "active"}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    fields.update(("qualificationID", "datePublished"))
    self.assertEqual(set(submission) - set(self.initial_submission_data), fields)


def get_submission(self):
    response = self.app.get("/submissions")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/submissions", {"data": self.initial_submission_data})
    self.assertEqual(response.status, "201 Created")
    submission = response.json["data"]

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], submission)

    response = self.app.get("/submissions/{}?opt_jsonp=callback".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"data": {"', response.body)

    response = self.app.get("/submissions/{}?opt_pretty=1".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "data": {\n        "', response.body)


def date_submission(self):
    response = self.app.get("/submissions")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/submissions", {"data": self.initial_submission_data})
    self.assertEqual(response.status, "201 Created")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    date = submission["date"]

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], date)

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": {"tenderers": [{"name": "Updated title"}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], date)

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "deleted"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["date"], date)


def dateModified_submission(self):
    response = self.app.get("/submissions")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/submissions", {"data": self.initial_submission_data})
    self.assertEqual(response.status, "201 Created")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    dateModified = submission["dateModified"]

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["dateModified"], dateModified)

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": {"tenderers": [{"name": "Draft_change"}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["dateModified"], dateModified)
    submission = response.json["data"]
    dateModified = submission["dateModified"]

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], submission)
    self.assertEqual(response.json["data"]["dateModified"], dateModified)

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["dateModified"], dateModified)
    submission = response.json["data"]
    dateModified = submission["dateModified"]

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], submission)
    self.assertEqual(response.json["data"]["dateModified"], dateModified)


def datePublished_submission(self):
    response = self.app.get("/submissions")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/submissions", {"data": self.initial_submission_data})
    self.assertEqual(response.status, "201 Created")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    self.assertNotIn("datePublished", submission)

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["data"]["date"], date)

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": {"tenderers": [{"name": "Updated title"}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("datePublished", response.json["data"])

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("datePublished", response.json["data"])


def submission_not_found(self):
    response = self.app.get("/submissions")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/submissions/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"submission_id"}]
    )

    response = self.app.patch_json("/submissions/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"submission_id"}]
    )

    # put custom document object into database to check frameworks construction on non-Submission data
    data = {"contract": "test", "_id": uuid4().hex}
    self.db.save(data)

    response = self.app.get("/submissions/{}".format(data["_id"]), status=404)
    self.assertEqual(response.status, "404 Not Found")


def submission_token_invalid(self):
    response = self.app.post_json("/submissions", {"data": self.initial_submission_data})
    self.assertEqual(response.status, "201 Created")
    submission_id = response.json["data"]["id"]

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission_id, "fake token"), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}]
    )

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission_id, "токен з кирилицею"), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}]
    )


def get_documents_list(self):
    response = self.app.get("/submissions/{}/documents".format(self.submission_id))
    documents = response.json["data"]
    self.assertEqual(len(documents), len(self.initial_submission_data["documents"]))


def get_document_by_id(self):
    documents = self.db.get(self.submission_id).get("documents")
    for doc in documents:
        response = self.app.get("/submissions/{}/documents/{}".format(self.submission_id, doc["id"]))
        document = response.json["data"]
        self.assertEqual(doc["id"], document["id"])
        self.assertEqual(doc["title"], document["title"])
        self.assertEqual(doc["format"], document["format"])
        self.assertEqual(doc["datePublished"], document["datePublished"])


def create_submission_document_forbidden(self):
    with change_auth(self.app, ("Basic", ("broker1", ""))):
        response = self.app.post(
            "/submissions/{}/documents".format(self.submission_id),
            upload_files=[("file", u"укр.doc", "content")],
            status=403
        )
        self.assertEqual(response.status, "403 Forbidden")


def create_submission_documents(self):
    response = self.app.post(
        "/submissions/{}/documents".format(self.submission_id),
        upload_files=[("file", u"укр.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def create_submission_document_json_bulk(self):
    response = self.app.post_json(
        "/submissions/{}/documents".format(self.submission_id),
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

    submission = self.db.get(self.submission_id)
    doc_1 = submission["documents"][0]
    doc_2 = submission["documents"][1]
    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")

    response = self.app.get("/submissions/{}/documents".format(self.submission_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]
    assert_document(doc_1, "name1.doc")
    assert_document(doc_2, "name2.doc")


def document_not_found(self):
    response = self.app.get("/submissions/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"submission_id"}]
    )

    response = self.app.post(
        "/submissions/some_id/documents", status=404, upload_files=[("file", "name.doc", "content")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"submission_id"}]
    )
    response = self.app.post(
        "/submissions/{}/documents".format(self.submission_id),
        status=404,
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])
    response = self.app.put(
        "/submissions/some_id/documents/some_id", status=404, upload_files=[("file", "name.doc", "content2")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"submission_id"}]
    )

    response = self.app.put(
        "/submissions/{}/documents/some_id".format(self.submission_id),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )

    response = self.app.get("/submissions/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"submission_id"}]
    )

    response = self.app.get("/submissions/{}/documents/some_id".format(self.submission_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )


def put_submission_document(self):
    from six import BytesIO
    from urllib import quote

    body = u"""--BOUNDARY\nContent-Disposition: form-data; name="file"; filename={}\nContent-Type: application/msword\n\ncontent\n""".format(
        u"\uff07"
    )
    environ = self.app._make_environ()
    environ["CONTENT_TYPE"] = "multipart/form-data; boundary=BOUNDARY"
    environ["REQUEST_METHOD"] = "POST"
    req = self.app.RequestClass.blank(
        self.app._remove_fragment("/submissions/{}/documents".format(self.submission_id)), environ
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
            "/submissions/{}/documents?acc_token={}".format(self.submission_id, self.submission_token)
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
        "/submissions/{}/documents/{}?acc_token={}".format(self.submission_id, doc_id, self.submission_token),
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
        submission = self.db.get(self.submission_id)
        self.assertIn(key, submission["documents"][-1]["url"])
        self.assertIn("Signature=", submission["documents"][-1]["url"])
        self.assertIn("KeyID=", submission["documents"][-1]["url"])
        self.assertNotIn("Expires=", submission["documents"][-1]["url"])
    response = self.app.get("/submissions/{}/documents/{}".format(self.submission_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name name.doc", response.json["data"]["title"])
    dateModified2 = response.json["data"]["dateModified"]
    self.assertTrue(dateModified < dateModified2)
    self.assertEqual(dateModified, response.json["data"]["previousVersions"][0]["dateModified"])

    response = self.app.get("/submissions/{}/documents?all=true".format(self.submission_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified2, response.json["data"][1]["dateModified"])

    response = self.app.post(
        "/submissions/{}/documents?acc_token={}".format(self.submission_id, self.framework_token),
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.get("/submissions/{}/documents".format(self.submission_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified2, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified, response.json["data"][1]["dateModified"])
    response = self.app.put(
        "/submissions/{}/documents/{}?acc_token={}".format(self.submission_id, doc_id, self.submission_token),
        status=404,
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])
    response = self.app.put(
        "/submissions/{}/documents/{}?acc_token={}".format(self.submission_id, doc_id, self.submission_token),
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
        framework = self.db.get(self.submission_id)
        self.assertIn(key, framework["documents"][-1]["url"])
        self.assertIn("Signature=", framework["documents"][-1]["url"])
        self.assertIn("KeyID=", framework["documents"][-1]["url"])
        self.assertNotIn("Expires=", framework["documents"][-1]["url"])
    else:
        key = response.json["data"]["url"].split("?")[-1].split("=")[-1]
    if self.docservice:
        response = self.app.get("/submissions/{}/documents/{}".format(self.submission_id, doc_id, key))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/submissions/{}/documents".format(self.submission_id, self.submission_token))
    self.assertEqual(response.status, "200 OK")
    doc_id = response.json["data"][0]["id"]
    response = self.app.patch_json(
        "/submissions/{}/documents/{}?acc_token={}".format(self.submission_id, doc_id, self.submission_token),
        {"data": {"documentType": None}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.set_submission_status("complete")
    response = self.app.put(
        "/submissions/{}/documents/{}?acc_token={}".format(self.submission_id, doc_id, self.submission_token),
        "contentX",
        content_type="application/msword",
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can't update document in current (complete) submission status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )
    #  document in current (complete) framework status
    response = self.app.patch_json(
        "/submissions/{}/documents/{}?acc_token={}".format(self.submission_id, doc_id, self.submission_token),
        {"data": {"documentType": None}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can't update document in current (complete)" u" submission status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )
