from copy import deepcopy
from datetime import timedelta
from unittest.mock import patch

from freezegun import freeze_time

from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.database import MongodbResourceConflict
from openprocurement.api.mask import MASK_STRING
from openprocurement.api.tests.base import change_auth
from openprocurement.api.utils import calculate_full_date, get_now


def listing(self):
    response = self.app.get("/qualifications")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    qualifications = []

    data = deepcopy(self.initial_submission_data)

    tenderer_ids = ["00037256", "00037257", "00037258"]

    for i in tenderer_ids:
        data["tenderers"][0]["identifier"]["id"] = i
        response = self.app.post_json(
            "/submissions",
            {
                "data": data,
                "config": self.initial_submission_config,
            },
        )
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

        response = self.activate_qualification(qualification_id)
        qualifications.append(response.json["data"])

    ids = ",".join([i["id"] for i in qualifications])

    response = self.app.get("/qualifications")
    self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in qualifications})
    self.assertEqual(
        {i["dateModified"] for i in response.json["data"]},
        {i["dateModified"] for i in qualifications},
    )
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in qualifications])
    )

    response = self.app.get("/qualifications?limit=1")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("prev_page", response.json)
    self.assertEqual(len(response.json["data"]), 1)
    offset = response.json["next_page"]["offset"]

    response = self.app.get(f"/qualifications?offset={offset}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)

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
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "status"})
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/qualifications", params=[("opt_fields", "status,owner")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "status"})
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/qualifications?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in qualifications})
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]],
        sorted([i["dateModified"] for i in qualifications], reverse=True),
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
        response = self.app.post_json(
            "/submissions",
            {
                "data": data,
                "config": self.initial_submission_config,
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(response.json["data"]["id"], response.json["access"]["token"]),
            {"data": {"status": "active"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        qualification_id = response.json["data"]["qualificationID"]

        response = self.activate_qualification(qualification_id)
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
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in qualifications})
    self.assertEqual({i["dateModified"] for i in response.json["data"]}, {i["dateModified"] for i in qualifications})
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
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "status"})
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/qualifications?feed=changes", params=[("opt_fields", "status,owner")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "status"})
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/qualifications?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in qualifications})
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]],
        sorted([i["dateModified"] for i in qualifications], reverse=True),
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

    self.activate_qualification(qualification_id)
    qualification = self.app.get("/qualifications/{}".format(qualification_id, self.framework_token)).json["data"]
    self.assertEqual(qualification["status"], "active")

    submission = self.app.get("/submissions/{}".format(self.submission_id)).json["data"]
    self.assertEqual(submission["status"], "complete")

    submission_data = deepcopy(self.initial_submission_data)
    submission_data["tenderers"][0]["identifier"]["id"] = "00037258"
    response = self.app.post_json(
        "/submissions",
        {
            "data": submission_data,
            "config": self.initial_submission_config,
        },
    )
    self.assertEqual(response.status, "201 Created")
    submission_id = response.json["data"]["id"]
    submission_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission_id, submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    qualification_id = response.json["data"]["qualificationID"]
    response = self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        {
            "data": {
                "title": "sign.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentType": "evaluationReports",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification = self.app.get("/qualifications/{}".format(qualification_id, self.framework_token)).json["data"]
    self.assertEqual(qualification["status"], "unsuccessful")

    submission = self.app.get("/submissions/{}".format(submission_id)).json["data"]
    self.assertEqual(submission["status"], "complete")


def activate_qualification_for_submission_with_docs(self):
    data = deepcopy(self.initial_submission_data)
    data["documents"] = [
        {
            "id": "040cfd87cca140d98bcff5a40b2b067a",
            "datePublished": get_now().isoformat(),
            "title": "name1.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    response = self.app.post_json(
        "/submissions",
        {
            "data": data,
            "config": self.initial_submission_config,
        },
    )
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
    self.assertIn("qualificationID", response.json["data"])
    self.assertEqual(len(response.json["data"]["qualificationID"]), 32)
    qualification_id = response.json["data"]["qualificationID"]

    qualification_patch_data = {
        "status": "active",
        "documents": [
            {
                "id": "040cfd87cca140d98bcff5a40b2b067a",
                "datePublished": get_now().isoformat(),
                "title": "evalouationReports.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentType": "evaluationReports",
            }
        ],
    }

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": qualification_patch_data},
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
        "restricted": False,
        'qualificationComplainDuration': 0,
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
    with change_auth(self.app, ("Basic", ("brokerr", ""))):

        data = deepcopy(self.initial_data)
        data["procuringEntity"]["kind"] = "defense"
        config = deepcopy(self.initial_config)
        config["restrictedDerivatives"] = True
        self.create_framework(data=data, config=config)
        response = self.activate_framework()

        framework = response.json["data"]

        self.assertEqual(framework["procuringEntity"]["kind"], "defense")

    # Create and activate submission
    with change_auth(self.app, ("Basic", ("brokerr", ""))):

        config = deepcopy(self.initial_submission_config)
        config["restricted"] = True

        response = self.create_submission(config=config)
        response = self.activate_submission()

        submission = response.json["data"]
        qualification_id = submission["qualificationID"]

    # Fail to modify qualification (no accreditation for restricted)
    with change_auth(self.app, ("Basic", ("broker", ""))):

        response = self.app.patch_json(
            f"/qualifications/{self.qualification_id}?acc_token={self.framework_token}",
            {"data": {}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "url",
                    "name": "accreditation",
                    "description": "Broker Accreditation level does not permit qualification restricted data access",
                }
            ],
        )

    # Activate qualification
    with change_auth(self.app, ("Basic", ("brokerr", ""))):

        expected_config = {
            "restricted": True,
            "qualificationComplainDuration": 0,
        }

        response = self.app.post_json(
            "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
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
        document = response.json["data"]

        response = self.activate_qualification()

        qualification = response.json["data"]
        self.assertEqual(response.json["config"], expected_config)

        response = self.app.get("/qualifications/{}".format(qualification_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        qualification = response.json["data"]
        self.assertEqual(response.json["config"], expected_config)

    # Check access
    with change_auth(self.app, ("Basic", ("brokerr", ""))):

        # Check object
        response = self.app.get("/qualifications/{}".format(qualification_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertNotEqual(
            response.json["data"]["documents"][0]["url"],
            MASK_STRING,
        )

        # Check listing
        response = self.app.get("/qualifications?opt_fields=status")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        qualifications = response.json["data"]
        self.assertEqual(len(qualifications), 1)
        self.assertEqual(
            set(qualifications[0].keys()),
            {
                "id",
                "dateModified",
                "status",
            },
        )

        # Check framework listing
        response = self.app.get("/frameworks/{}/qualifications".format(self.framework_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        qualifications = response.json["data"]
        self.assertEqual(len(qualifications), 1)
        self.assertEqual(
            set(qualifications[0].keys()),
            {
                "id",
                "dateModified",
                "status",
                "submissionID",
                "documents",
                "date",
                "frameworkID",
                "dateCreated",
            },
        )
        self.assertNotEqual(
            qualifications[0]["documents"][0]["url"],
            MASK_STRING,
        )

    # Check access (no accreditation for restricted)
    with change_auth(self.app, ("Basic", ("broker", ""))):

        # Check object
        response = self.app.get("/qualifications/{}".format(qualification_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["data"]["documents"][0]["url"],
            MASK_STRING,
        )

    # Check access (anonymous)
    with change_auth(self.app, ("Basic", ("", ""))):

        # Check object
        response = self.app.get("/qualifications/{}".format(qualification_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["data"]["documents"][0]["url"],
            MASK_STRING,
        )

        # Check object documents
        response = self.app.get("/qualifications/{}/documents".format(qualification_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["data"][0]["url"],
            MASK_STRING,
        )

        # Check object document
        response = self.app.get("/qualifications/{}/documents/{}".format(qualification_id, document["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["data"]["url"],
            MASK_STRING,
        )

        # Check listing
        response = self.app.get("/qualifications?opt_fields=status")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        qualifications = response.json["data"]
        self.assertEqual(len(qualifications), 1)
        self.assertEqual(
            set(qualifications[0].keys()),
            {
                "id",
                "dateModified",
                "status",
            },
        )

        # Check framework listing
        response = self.app.get("/frameworks/{}/qualifications".format(self.framework_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        qualifications = response.json["data"]
        self.assertEqual(len(qualifications), 1)
        self.assertEqual(
            set(qualifications[0].keys()),
            {
                "id",
                "dateModified",
                "status",
                "submissionID",
                "documents",
                "date",
                "frameworkID",
                "dateCreated",
            },
        )
        self.assertEqual(
            qualifications[0]["documents"][0]["url"],
            MASK_STRING,
        )


def patch_qualification_active_mock(self):
    qualification_id = self.qualification_id
    response = self.app.post_json(
        f"/qualifications/{qualification_id}/documents?acc_token={self.framework_token}",
        {
            "data": {
                "title": "sign.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentType": "evaluationReports",
            }
        },
    )

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["frameworkID"], self.framework_id)

    complaint_period = response.json["data"]["complaintPeriod"]
    end_date = calculate_full_date(
        get_now(),
        timedelta(days=self.initial_config["qualificationComplainDuration"]),
        working_days=True,
        ceil=True,
    )
    assert end_date.isoformat() == complaint_period["endDate"]


def patch_qualification_active(self):
    response = self.app.post_json(
        "/frameworks",
        {
            "data": self.initial_data,
            "config": self.initial_config,
        },
    )
    framework2_id = response.json["data"]["id"]
    framework2_token = response.json["access"]["token"]

    self.app.patch_json(f"/frameworks/{framework2_id}?acc_token={framework2_token}", {"data": {"status": "active"}})

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification_id = response.json["data"]["qualificationID"]

    response = self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        {
            "data": {
                "title": "name1.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    document_id = response.json["data"]["id"]

    self.activate_qualification(qualification_id)

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
        {"data": {}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Can't update qualification in current (active) status",
                'location': 'body',
                'name': 'data',
            }
        ],
    )

    response = self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        {
            "data": {
                "title": "name1.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
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
                'description': "Can't add document in current (active) qualification status",
                'location': 'body',
                'name': 'data',
            }
        ],
    )

    response = self.app.patch_json(
        "/qualifications/{}/documents/{}?acc_token={}".format(qualification_id, document_id, self.framework_token),
        {"data": {"name": "name2.doc"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Can't update document in current (active) qualification status",
                'location': 'body',
                'name': 'data',
            }
        ],
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
        {
            "data": {
                "title": "sign.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentType": "evaluationReports",
            }
        },
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
        [
            {
                'description': "Can't update qualification in current (unsuccessful) status",
                'location': 'body',
                'name': 'data',
            }
        ],
    )

    response = self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(qualification_id, self.framework_token),
        {
            "data": {
                "title": "name1.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
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
                'description': "Can't add document in current (unsuccessful) qualification status",
                'location': 'body',
                'name': 'data',
            }
        ],
    )

    response = self.app.patch_json(
        "/qualifications/{}/documents/{}?acc_token={}".format(qualification_id, document_id, self.framework_token),
        {"data": {"title": "name1.doc"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Can't update document in current (unsuccessful) qualification status",
                'location': 'body',
                'name': 'data',
            }
        ],
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

    fields = {
        "id",
        "dateModified",
        "date",
        "status",
        "qualificationType",
        "submissionID",
        "frameworkID",
    }
    self.assertEqual(set(qualification), fields)

    response = self.activate_qualification(qualification_id)
    qualification = response.json["data"]
    fields = fields | {"documents"}
    self.assertEqual(set(qualification), fields)


def qualification_evaluation_reports_documents(self):
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(self.submission_id, self.submission_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    qualification_id = response.json["data"]["qualificationID"]

    # try to activate qualification without docs
    response = self.app.patch_json(
        f"/qualifications/{qualification_id}?acc_token={self.framework_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Document with type 'evaluationReports' and format pkcs7-signature is required",
    )

    # try to set qualification as unsuccessfull without docs
    response = self.app.patch_json(
        f"/qualifications/{qualification_id}?acc_token={self.framework_token}",
        {"data": {"status": "unsuccessful"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Document with type 'evaluationReports' and format pkcs7-signature is required",
    )

    # try to patch qualification with two evaluationReports documents
    data = {
        "documents": [
            {
                "id": "e4d7216f28dc4a1cbf18c5e4ee2cd1c5",
                "title": "sign.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentType": "evaluationReports",
            },
            {
                "title": "evalouationReports.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentType": "evaluationReports",
            },
        ],
    }
    response = self.app.patch_json(
        f"/qualifications/{qualification_id}?acc_token={self.framework_token}",
        {"data": data},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "evaluationReports document in qualification should be only one",
    )

    # try to add bulk of evaluationReports documents via docs endpoints
    response = self.app.post_json(
        f"/qualifications/{qualification_id}/documents?acc_token={self.framework_token}",
        {"data": data["documents"]},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "evaluationReports document in qualification should be only one",
    )

    response = self.app.post_json(
        f"/qualifications/{qualification_id}/documents?acc_token={self.framework_token}",
        {"data": data["documents"][0]},
    )
    self.assertEqual(response.status, "201 Created")
    doc_id = response.json["data"]["id"]

    # add evaluationReports document when another one already exists
    response = self.app.post_json(
        f"/qualifications/{qualification_id}/documents?acc_token={self.framework_token}",
        {"data": data["documents"][0]},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "evaluationReports document in qualification should be only one",
    )

    # patch documentType in evaluationReports doc
    response = self.app.patch_json(
        f"/qualifications/{qualification_id}/documents/{doc_id}?acc_token={self.framework_token}",
        {"data": {"documentType": "notice"}},
    )
    self.assertEqual(response.status, "200 OK")

    # try to add another evaluationReports
    response = self.app.post_json(
        f"/qualifications/{qualification_id}/documents?acc_token={self.framework_token}",
        {"data": data["documents"][0]},
    )
    self.assertEqual(response.status, "201 Created")

    # try to activate qualification
    response = self.app.patch_json(
        f"/qualifications/{qualification_id}?acc_token={self.framework_token}",
        {"data": {"status": "unsuccessful"}},
    )
    self.assertEqual(response.status, "200 OK")


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
        {
            "data": {
                "title": "sign.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentType": "evaluationReports",
            }
        },
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

    response = self.activate_qualification(qualification_id)
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
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, ""), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.patch_json(
        "/qualifications/{}?acc_token={}".format(qualification_id, "токен з кирилицею"),
        {"data": {}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'location': 'body',
                'name': 'UnicodeEncodeError',
                'description': "'latin-1' codec can't encode characters in position 10-14: ordinal not in range(256)",
            }
        ],
    )


def get_documents_list(self):
    self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
        {
            "data": {
                "title": "укр.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )

    response = self.app.get("/qualifications/{}/documents".format(self.qualification_id))
    documents = response.json["data"]
    self.assertEqual(len(documents), 1)


def get_document_by_id(self):
    self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
        {
            "data": [
                {
                    "title": f"укр{i}.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
                for i in range(3)
            ]
        },
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
        status=403,
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
                },
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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}])


def put_qualification_document(self):
    response = self.app.post_json(
        "/qualifications/{}/documents?acc_token={}".format(self.qualification_id, self.framework_token),
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

    with freeze_time((get_now() + timedelta(days=1)).isoformat()):
        response = self.app.put_json(
            "/qualifications/{}/documents/{}?acc_token={}".format(self.qualification_id, doc_id, self.framework_token),
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

    key = response.json["data"]["url"].split("/")[-1].split("?")[0]
    qualification = self.mongodb.qualifications.get(self.qualification_id)
    self.assertIn(key, qualification["documents"][-1]["url"])
    response = self.app.get("/qualifications/{}/documents/{}".format(self.qualification_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
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

    response = self.app.get("/qualifications/{}/documents".format(self.qualification_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(dateModified2, response.json["data"][0]["dateModified"])
    self.assertEqual(dateModified, response.json["data"][1]["dateModified"])
    response = self.app.put_json(
        "/qualifications/{}/documents/{}?acc_token={}".format(self.qualification_id, doc_id, self.framework_token),
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

    self.activate_qualification()

    response = self.app.put_json(
        "/qualifications/{}/documents/{}?acc_token={}".format(self.qualification_id, doc_id, self.framework_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
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

    response = self.app.post_json(
        f"/qualifications/{qualification_id}/documents?acc_token={self.framework_token}",
        {
            "data": {
                "title": "sign.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentType": "evaluationReports",
            }
        },
    )

    with patch("openprocurement.framework.core.database.SubmissionCollection.save") as agreement_save_mock:
        agreement_save_mock.side_effect = MongodbResourceConflict("Conflict")
        # submission is updated last, we make it fail
        # and check that previous operations were not performed

        self.app.patch_json(
            "/qualifications/{}?acc_token={}".format(qualification_id, self.framework_token),
            {"data": {"status": "active"}},
            status=409,
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
