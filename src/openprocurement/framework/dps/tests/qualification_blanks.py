from copy import deepcopy
from freezegun import freeze_time
from openprocurement.api.utils import get_now
from openprocurement.api.tests.base import change_auth
from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.database import MongodbResourceConflict
from datetime import timedelta
from mock import Mock, patch


def listing(self):
    response = self.app.get("/qualifications")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    qualifications = []

    data = deepcopy(self.initial_submission_data)

    tenderer_ids = ["00037256", "00037257", "00037258"]

    for i in tenderer_ids:
        data["tenderers"][0]["identifier"]["id"] = i
        response = self.app.post_json("/submissions", {
            "data": data,
            "config": self.initial_submission_config,
        })
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

    response = self.app.get("/qualifications")
    self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in qualifications]))
    self.assertEqual(
        {i["dateModified"] for i in response.json["data"]},
        {i["dateModified"] for i in qualifications},
    )
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]],
        sorted([i["dateModified"] for i in qualifications])
    )

    response = self.app.get("/qualifications?limit=2")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("prev_page", response.json)
    self.assertEqual(len(response.json["data"]), 2)
    next_page = response.json["next_page"]

    response = self.app.get("/qualifications?offset={}".format(next_page["offset"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get(next_page["path"].replace(ROUTE_PREFIX, ""))
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
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/qualifications", params=[("opt_fields", "status,owner")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/qualifications?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
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
        response = self.app.post_json("/submissions", {
            "data": data,
            "config": self.initial_submission_config,
        })
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
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
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
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/qualifications?feed=changes", params=[("opt_fields", "status,owner")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/qualifications?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
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

    qualification_invalid_patch_data = {
        "date": (get_now() + timedelta(days=2)).isoformat(),
        "dateModified": (get_now() + timedelta(days=1)).isoformat(),
        "qualificationType": "changed",
        "submissionID": "0" * 32,
    }
    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": qualification_invalid_patch_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    error_fields = [field["name"] for field in response.json["errors"]]
    self.assertListEqual(sorted(error_fields), list(qualification_invalid_patch_data.keys()))

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
    response = self.app.post_json("/submissions", {
        "data": submission_data,
        "config": self.initial_submission_config,
    })
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


def activate_qualification_for_submission_with_docs(self):
    data = deepcopy(self.initial_submission_data)
    data["documents"] = [{
        "id": "040cfd87cca140d98bcff5a40b2b067a",
        "datePublished": get_now().isoformat(),
        "title": "name1.doc",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/msword",
    }]
    response = self.app.post_json(
        "/submissions", {
            "data": data,
            "config": self.initial_submission_config,
        }
    )
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
    self.assertIn("qualificationID", response.json["data"])
    self.assertEqual(len(response.json["data"]["qualificationID"]), 32)
    qualification_id = response.json["data"]["qualificationID"]

    qualification_patch_data = {
        "status": "active",
        "documents": [{
            "id": "040cfd87cca140d98bcff5a40b2b067a",
            "datePublished": get_now().isoformat(),
            "title": "name1.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }],
    }

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": qualification_patch_data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")


def patch_submission_pending_config_test(self):
    # Create framework
    config = deepcopy(self.initial_config)
    config["test"] = True
    self.create_framework(config=config)
    response = self.activate_framework()

    framework = response.json["data"]
    self.assertNotIn("config", framework)
    self.assertEqual(framework["mode"], "test")
    self.assertTrue(response.json["config"]["test"])

    # Create and activate submission
    self.create_submission()
    response = self.activate_submission()

    qualification_id = response.json["data"]["qualificationID"]

    # Activate qualification
    expected_config = {
        "test": True,
    }

    response = self.activate_qualification()

    qualification = response.json["data"]
    self.assertNotIn("config", qualification)
    self.assertEqual(qualification["mode"], "test")
    self.assertEqual(response.json["config"], expected_config)

    response = self.app.get("/qualifications/{}".format(qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    qualification = response.json["data"]
    self.assertNotIn("config", qualification)
    self.assertEqual(qualification["mode"], "test")
    self.assertEqual(response.json["config"], expected_config)


def patch_submission_pending_config_restricted(self):
    # Create framework
    with change_auth(self.app, ("Basic", ("broker1", ""))):
        data = deepcopy(self.initial_data)
        data["procuringEntity"]["kind"] = "defense"
        config = deepcopy(self.initial_config)
        config["restrictedDerivatives"] = True
        self.create_framework(data=data, config=config)
        response = self.activate_framework()

        framework = response.json["data"]
        framework_owner = framework["owner"]

        self.assertNotIn("config", framework)
        self.assertEqual(framework["procuringEntity"]["kind"], "defense")

    # Create and activate submission
    with change_auth(self.app, ("Basic", ("broker2", ""))):
        # Change authorization so framework and submission have different owners

        config = deepcopy(self.initial_submission_config)
        config["restricted"] = True

        response = self.create_submission(config=config)
        response = self.activate_submission()

        submission = response.json["data"]
        qualification_id = submission["qualificationID"]

        submission_owner = submission["owner"]
        self.assertNotEqual(submission_owner, framework_owner)

    # Activate qualification
    with change_auth(self.app, ("Basic", ("broker1", ""))):
        expected_config = {
            "restricted": True,
        }

        response = self.app.post_json(
            "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
            {"data": {
                "title": "name name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }},
        )
        self.assertEqual(response.status, "201 Created")
        document = response.json["data"]

        response = self.activate_qualification()

        qualification = response.json["data"]
        self.assertNotIn("config", qualification)
        self.assertEqual(response.json["config"], expected_config)

        response = self.app.get("/qualifications/{}".format(qualification_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        qualification = response.json["data"]
        self.assertNotIn("config", qualification)
        self.assertEqual(response.json["config"], expected_config)

    # Check access (framework owner)
    with change_auth(self.app, ("Basic", ("broker1", ""))):
        # Check object
        response = self.app.get("/qualifications/{}".format(qualification_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        # Check listing
        response = self.app.get("/qualifications?opt_fields=status")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        qualifications = response.json["data"]
        self.assertEqual(len(qualifications), 1)
        self.assertNotIn("config", qualifications[0])
        self.assertNotIn("owner", qualifications[0])
        self.assertEqual(set(qualifications[0].keys()), {"id", "dateModified", "status"})

        response = self.app.get("/frameworks/{}/qualifications".format(self.framework_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        qualifications = response.json["data"]
        self.assertEqual(len(qualifications), 1)
        self.assertNotIn("config", qualifications[0])
        self.assertNotIn("owner", qualifications[0])
        self.assertEqual(set(qualifications[0].keys()), {
            "id",
            "dateModified",
            "status",
            "submissionID",
            "documents",
            "date",
            "frameworkID",
            "dateCreated",
        })

    # Check access (submission owner)
    with change_auth(self.app, ("Basic", ("broker2", ""))):
        # Check object
        response = self.app.get("/qualifications/{}".format(qualification_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        # Check listing
        response = self.app.get("/qualifications?opt_fields=status")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        qualifications = response.json["data"]
        self.assertEqual(len(qualifications), 1)
        self.assertNotIn("config", qualifications[0])
        self.assertNotIn("owner", qualifications[0])
        self.assertEqual(set(qualifications[0].keys()), {"id", "dateModified", "status"})

        response = self.app.get("/frameworks/{}/qualifications".format(self.framework_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        qualifications = response.json["data"]
        self.assertEqual(len(qualifications), 1)
        self.assertNotIn("config", qualifications[0])
        self.assertNotIn("owner", qualifications[0])
        self.assertEqual(set(qualifications[0].keys()), {
            "id",
            "dateModified",
            "status",
            "submissionID",
            "documents",
            "date",
            "frameworkID",
            "dateCreated",
        })

    # Check access (anonymous)
    with change_auth(self.app, ("Basic", ("", ""))):
        # Check object
        response = self.app.get("/qualifications/{}".format(qualification_id), status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{
                "location": "body",
                "name": "data",
                "description": "Access restricted for qualification object"
            }]
        )

        # Check object documents
        response = self.app.get("/qualifications/{}/documents".format(qualification_id), status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{
                "location": "body",
                "name": "data",
                "description": "Access restricted for qualification object"
            }]
        )

        # Check object document
        response = self.app.get("/qualifications/{}/documents".format(qualification_id, document["id"]), status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{
                "location": "body",
                "name": "data",
                "description": "Access restricted for qualification object"
            }]
        )

        # Check listing
        response = self.app.get("/qualifications?opt_fields=status")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        qualifications = response.json["data"]
        self.assertEqual(len(qualifications), 1)
        self.assertNotIn("config", qualifications[0])
        self.assertNotIn("owner", qualifications[0])
        self.assertEqual(
            set(qualifications[0].keys()),
            {"id", "dateModified", "restricted"},
        )

        response = self.app.get("/frameworks/{}/qualifications".format(self.framework_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        qualifications = response.json["data"]
        self.assertEqual(len(qualifications), 1)
        self.assertNotIn("config", qualifications[0])
        self.assertNotIn("owner", qualifications[0])
        self.assertEqual(
            set(qualifications[0].keys()),
            {"id", "dateModified", "dateCreated", "submissionID", "frameworkID", "restricted"},
        )


def patch_qualification_active(self):
    response = self.app.post_json("/frameworks", {
        "data": self.initial_data,
        "config": self.initial_config,
    })
    framework2_id = response.json["data"]["id"]
    framework2_token = response.json["access"]["token"]

    self.app.patch_json(
        f"/frameworks/{framework2_id}?acc_token={framework2_token}",
        {"data": {"status": "active"}}
    )

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification_id = response.json["data"]["qualificationID"]

    response = self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {
            "title": "name1.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
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
    self.assertEqual(response.json["data"]["frameworkID"], self.framework_id)

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
            'description': "Can't update qualification in current (active) status",
            'location': 'body',
            'name': 'data',
        }]
    )

    response = self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {
            "title": "name1.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{
            'description': "Can't add document in current (active) qualification status",
            'location': 'body',
            'name': 'data'
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
            'description': "Can't update document in current (active) qualification status",
            'location': 'body',
            'name': 'data'
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

    response = self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {
            "title": "name1.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
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
            'description': "Can't update qualification in current (unsuccessful) status",
            'location': 'body',
            'name': 'data',
        }]
    )

    response = self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {
            "title": "name1.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{
            'description': "Can't add document in current (unsuccessful) qualification status",
            'location': 'body',
            'name': 'data'
        }]
    )

    response = self.app.patch_json(
        "/qualifications/{}/documents/{}?acc_token={}".format(qualification_id, document_id, self.framework_token),
        {"data": {"title": "name1.doc"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [{
            'description': "Can't update document in current (unsuccessful) qualification status",
            'location': 'body',
            'name': 'data'
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
            "id",
            "dateModified",
            "date",
            "status",
            "qualificationType",
            "submissionID",
            "frameworkID",
        ]
    )
    self.assertEqual(set(qualification), fields)

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification["id"], self.framework_token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification = response.json["data"]
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

    response = self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {
            "title": "укр.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
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

    with freeze_time((get_now() + timedelta(days=1)).isoformat()):
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

    with freeze_time((get_now() + timedelta(days=1)).isoformat()):
        response = self.app.post_json(
            "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
            {"data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }},
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
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "qualification_id"}]
    )

    response = self.app.patch_json("/qualifications/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "qualification_id"}]
    )


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
        response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}]
    )

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, ""), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}]
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
    self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
        {"data": {
            "title": "укр.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )

    response = self.app.get("/qualifications/{}/documents".format(self.qualification_id))
    documents = response.json["data"]
    self.assertEqual(len(documents), 1)


def get_document_by_id(self):
    self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
        {"data": [{
            "title": f"укр{i}.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        } for i in range(3)]},
    )
    documents = self.mongodb.qualifications.get(self.qualification_id).get("documents")
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
        upload_files=[("file", "укр.doc", b"content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}],
    )

    with change_auth(self.app, ("Basic", ("broker1", ""))):
        response = self.app.post(
            "/qualifications/{}/documents".format(self.qualification_id),
            upload_files=[("file", "укр.doc", b"content")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}],
        )


def create_qualification_document(self):
    response = self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
        {"data": {
            "title": "укр.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


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
    self.assertEqual("name1.doc", doc_1["title"])
    self.assertEqual("name2.doc", doc_2["title"])

    qualification = self.mongodb.qualifications.get(self.qualification_id)
    doc_1 = qualification["documents"][0]
    doc_2 = qualification["documents"][1]
    self.assertEqual("name1.doc", doc_1["title"])
    self.assertEqual("name2.doc", doc_2["title"])

    response = self.app.get("/qualifications/{}/documents".format(self.qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]
    self.assertEqual("name1.doc", doc_1["title"])
    self.assertEqual("name2.doc", doc_2["title"])


def document_not_found(self):
    response = self.app.get("/qualifications/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "qualification_id"}]
    )

    response = self.app.post_json(
        "/qualifications/some_id/documents",
        {"data": {
            "title": "name1.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "qualification_id"}]
    )
    response = self.app.put(
        "/qualifications/some_id/documents/some_id", status=404, upload_files=[("file", "name.doc", b"content2")]
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "qualification_id"}]
    )

    response = self.app.put_json(
        "/qualifications/{}/documents/some_id".format(self.qualification_id),
        {"data": {
            "title": "name1.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
    )

    response = self.app.get("/qualifications/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "qualification_id"}]
    )

    response = self.app.get("/qualifications/{}/documents/some_id".format(self.qualification_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
    )


def put_qualification_document(self):
    response = self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
        {"data": {
            "title": "укр.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    with freeze_time((get_now() + timedelta(days=1)).isoformat()):
        response = self.app.put_json(
            "/qualifications/{}/documents/{}?acc_token={}".format(self.qualification_id, doc_id, self.framework_token),
            {"data": {
                "title": "name name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    qualification = self.mongodb.qualifications.get(self.qualification_id)
    self.assertIn(key, qualification["documents"][-1]["url"])
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

    with freeze_time((get_now() + timedelta(days=2)).isoformat()):
        response = self.app.post_json(
            "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
            {"data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }},
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
    response = self.app.put_json(
        "/qualifications/{}/documents/{}?acc_token={}".format(self.qualification_id, doc_id, self.framework_token),
        {"data": {
            "title": "name name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    qualification = self.mongodb.qualifications.get(self.qualification_id)
    self.assertIn(key, qualification["documents"][-1]["url"])

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

    response = self.app.put_json(
        "/qualifications/{}/documents/{}?acc_token={}".format(self.qualification_id, doc_id, self.framework_token),
        {"data": {
            "title": "name name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't update document in current (active) qualification status",
                "location": "body",
                "name": "data",
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
                "description": "Can't update document in current (active) qualification status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def active_qualification_changes_atomic(self):
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification_id = response.json["data"]["qualificationID"]

    with patch("openprocurement.framework.core.database.SubmissionCollection.save") as agreement_save_mock:
        agreement_save_mock.side_effect = MongodbResourceConflict("Conflict")
        # submission is updated last, we make it fail
        # and check that previous operations were not performed

        self.app.patch_json(
            "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
            {"data": {"status": "active"}},
            status=409
        )

    response = self.app.get(f"/qualifications/{qualification_id}")
    qualification = response.json["data"]
    self.assertEqual("pending", qualification["status"])  # not "active"

    response = self.app.get(f"/submissions/{qualification['submissionID']}")
    submission = response.json["data"]
    self.assertEqual("active", submission["status"])  # not "complete"

    response = self.app.get(f"/frameworks/{qualification['frameworkID']}")
    framework = response.json["data"]
    self.assertNotIn("agreementID", framework)

    agreements = list(self.mongodb.agreements.collection.find({}))
    self.assertEqual(0, len(agreements))
