# -*- coding: utf-8 -*-
import mock
from copy import deepcopy
from datetime import timedelta
from freezegun import freeze_time

from openprocurement.api.mask import MASK_STRING
from openprocurement.api.utils import get_now
from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.tests.base import change_auth
from openprocurement.tender.core.procedure.utils import dt_from_iso


def listing(self):
    response = self.app.get("/submissions")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    submissions = []

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
        submissions.append(response.json["data"])

    ids = ",".join([i["id"] for i in submissions])
    response = self.app.get("/submissions")
    self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in submissions]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in submissions])
    )
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in submissions])
    )

    response = self.app.get("/submissions?limit=2")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("prev_page", response.json)
    self.assertEqual(len(response.json["data"]), 2)
    next_page = response.json["next_page"]

    response = self.app.get("/submissions?offset={}".format(next_page["offset"]))
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

    response = self.app.get("/submissions", params=[("opt_fields", "status")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/submissions", params=[("opt_fields", "status,owner")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/submissions?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in submissions]))
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]],
        sorted([i["dateModified"] for i in submissions], reverse=True),
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
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
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
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/submissions?feed=changes", params=[("opt_fields", "status,owner")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/submissions?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in submissions]))
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]],
        sorted([i["dateModified"] for i in submissions], reverse=True),
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
        submissions.append(response.json["data"])
        # Draft submissions
        response = self.app.post_json(
            "/submissions",
            {
                "data": data,
                "config": self.initial_submission_config,
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    ids = ",".join([i["id"] for i in submissions])

    while True:
        response = self.app.get("/submissions")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in submissions]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in submissions])
    )
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in submissions])
    )


def create_submission_after_period_ends(self):
    response = self.app.get(f"/frameworks/{self.framework_id}")
    self.assertEqual(response.status, "200 OK")
    period_end_date = dt_from_iso(response.json["data"]["period"]["endDate"])
    data = deepcopy(self.initial_submission_data)
    data["frameworkID"] = self.framework_id
    with freeze_time((period_end_date + timedelta(days=1)).isoformat()):
        response = self.app.post_json(
            "/submissions",
            {
                "data": data,
                "config": self.initial_submission_config,
            },
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertIn(
            "Submission can be add only during the period:",
            response.json["errors"][0]["description"],
        )


def create_submission_draft_invalid(self):
    request_path = "/submissions"

    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Expecting value: line 1 column 1 (char 0)", "location": "body", "name": "data"}],
    )

    response = self.app.post_json(request_path, "data", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"not_data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json(request_path, {"data": []}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    data = {
        "frameworkID": self.framework_id,
        "invalid_field": "invalid_value",
        "submissionType": self.initial_submission_data["submissionType"],
    }
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    data = {
        "frameworkID": self.framework_id,
        "submissionType": self.initial_submission_data["submissionType"],
    }
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "tenderers"},
        response.json["errors"],
    )

    data = deepcopy(self.initial_submission_data)
    data["frameworkID"] = "some_id"
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': ['frameworkID must be one of exists frameworks'],
                'location': 'body',
                'name': 'frameworkID',
            }
        ],
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
        [
            {
                'description': [
                    {
                        'address': ['This field is required.'],
                        'contactPoint': ['This field is required.'],
                        'name': ['This field is required.'],
                    }
                ],
                'location': 'body',
                'name': 'tenderers',
            }
        ],
    )

    data = deepcopy(self.initial_submission_data)
    del data["tenderers"][0]["address"]["postalCode"]
    del data["tenderers"][0]["address"]["streetAddress"]
    del data["tenderers"][0]["address"]["region"]
    del data["tenderers"][0]["address"]["locality"]
    del data["tenderers"][0]["contactPoint"]["telephone"]
    del data["tenderers"][0]["contactPoint"]["email"]
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'location': 'body',
                'name': 'tenderers',
                'description': [
                    {
                        'address': {
                            'postalCode': ['This field is required.'],
                            'region': ['This field is required.'],
                            'streetAddress': ['This field is required.'],
                            'locality': ['This field is required.'],
                        },
                        'contactPoint': {
                            'email': ['This field is required.'],
                        },
                    }
                ],
            }
        ],
    )


def create_submission_draft(self):
    data = self.initial_submission_data
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
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "active")

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "active")


def create_submission_config_test(self):
    # Create framework
    config = deepcopy(self.initial_config)
    config["test"] = True
    self.create_framework(config=config)
    response = self.activate_framework()

    framework = response.json["data"]
    self.assertNotIn("config", framework)
    self.assertEqual(framework["mode"], "test")
    self.assertTrue(response.json["config"]["test"])

    # Create submission
    expected_config = deepcopy(self.initial_submission_config)
    expected_config["test"] = True

    response = self.create_submission()

    submission = response.json["data"]
    self.assertNotIn("config", submission)
    self.assertEqual(submission["mode"], "test")
    self.assertEqual(response.json["config"], expected_config)

    response = self.activate_submission()

    submission = response.json["data"]
    self.assertNotIn("config", submission)
    self.assertEqual(submission["mode"], "test")
    self.assertEqual(response.json["config"], expected_config)

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    submission = response.json["data"]
    self.assertNotIn("config", submission)
    self.assertEqual(submission["mode"], "test")
    self.assertEqual(response.json["config"], expected_config)


def create_submission_config_restricted(self):
    # Create framework
    with change_auth(self.app, ("Basic", ("brokerr", ""))):

        data = deepcopy(self.initial_data)
        data["procuringEntity"]["kind"] = "defense"
        config = deepcopy(self.initial_config)
        config["restrictedDerivatives"] = True
        self.create_framework(data=data, config=config)
        response = self.activate_framework()

        framework = response.json["data"]

        self.assertTrue(response.json["config"]["restrictedDerivatives"])
        self.assertEqual(framework["procuringEntity"]["kind"], "defense")

    # Fail to create submission (no accreditation for restricted)
    with change_auth(self.app, ("Basic", ("broker", ""))):

        config = deepcopy(self.initial_submission_config)
        config["restricted"] = True

        response = self.create_submission(config=config, status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "url",
                    "name": "accreditation",
                    "description": "Broker Accreditation level does not permit framework restricted data access",
                }
            ],
        )

    # Create submission
    with change_auth(self.app, ("Basic", ("brokerr", ""))):

        expected_config = {
            "restricted": True,
        }

        config = deepcopy(self.initial_submission_config)
        config["restricted"] = True

        response = self.create_submission(config=config)

        token = response.json["access"]["token"]

        submission = response.json["data"]
        self.assertEqual(response.json["config"], expected_config)

    # Fail to modify submission (no accreditation for restricted)
    with change_auth(self.app, ("Basic", ("broker", ""))):

        response = self.app.patch_json(
            f"/submissions/{self.submission_id}?acc_token={self.submission_token}",
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
                    "description": "Broker Accreditation level does not permit submission restricted data access",
                }
            ],
        )

    # Activate submission
    with change_auth(self.app, ("Basic", ("brokerr", ""))):

        response = self.app.post_json(
            "/submissions/{}/documents?acc_token={}".format(self.submission_id, self.submission_token),
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

        response = self.activate_submission()

        submission = response.json["data"]
        self.assertEqual(response.json["config"], expected_config)

        response = self.app.get("/submissions/{}".format(submission["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        submission = response.json["data"]
        self.assertEqual(response.json["config"], expected_config)

    # Check access
    with change_auth(self.app, ("Basic", ("brokerr", ""))):

        # Check object
        response = self.app.get("/submissions/{}".format(submission["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertNotEqual(
            response.json["data"]["tenderers"][0]["address"]["streetAddress"],
            MASK_STRING,
        )
        self.assertNotEqual(
            response.json["data"]["documents"][0]["url"],
            MASK_STRING,
        )

        # Check listing
        response = self.app.get("/submissions?opt_fields=status,tenderers")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        submissions = response.json["data"]
        self.assertEqual(len(submissions), 1)
        self.assertEqual(
            set(submissions[0].keys()),
            {
                "id",
                "dateModified",
                "status",
                "tenderers",
            },
        )
        self.assertNotEqual(
            submissions[0]["tenderers"][0]["address"]["streetAddress"],
            MASK_STRING,
        )

        # Check framework listing
        response = self.app.get("/frameworks/{}/submissions".format(self.framework_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        submissions = response.json["data"]
        self.assertEqual(len(submissions), 1)
        self.assertEqual(
            set(submissions[0].keys()),
            {
                "id",
                "dateModified",
                "status",
                "dateCreated",
                "datePublished",
                "frameworkID",
                "tenderers",
                "qualificationID",
                "date",
                "documents",
            },
        )
        self.assertNotEqual(
            submissions[0]["tenderers"][0]["address"]["streetAddress"],
            MASK_STRING,
        )
        self.assertNotEqual(
            submissions[0]["documents"][0]["url"],
            MASK_STRING,
        )

    # Check access (no accreditation for restricted)
    with change_auth(self.app, ("Basic", ("broker", ""))):

        # Check object
        response = self.app.get("/submissions/{}".format(submission["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["data"]["tenderers"][0]["address"]["streetAddress"],
            MASK_STRING,
        )
        self.assertEqual(
            response.json["data"]["documents"][0]["url"],
            MASK_STRING,
        )

    # Check access (anonymous)
    with change_auth(self.app, ("Basic", ("", ""))):

        # Check object
        response = self.app.get("/submissions/{}".format(submission["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["data"]["tenderers"][0]["address"]["streetAddress"],
            MASK_STRING,
        )
        self.assertEqual(
            response.json["data"]["documents"][0]["url"],
            MASK_STRING,
        )

        # Check object documents
        response = self.app.get("/submissions/{}/documents".format(submission["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["data"][0]["url"],
            MASK_STRING,
        )

        # Check object document
        response = self.app.get("/submissions/{}/documents/{}".format(submission["id"], document["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["data"]["url"],
            MASK_STRING,
        )

        # Check listing
        response = self.app.get("/submissions?opt_fields=status,tenderers")
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        submissions = response.json["data"]
        self.assertEqual(len(submissions), 1)
        self.assertEqual(
            set(submissions[0].keys()),
            {"id", "dateModified", "status", "tenderers"},
        )
        self.assertEqual(
            submissions[0]["tenderers"][0]["address"]["streetAddress"],
            MASK_STRING,
        )

        # Check framework listing
        response = self.app.get("/frameworks/{}/submissions".format(self.framework_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        submissions = response.json["data"]
        self.assertEqual(len(submissions), 1)
        self.assertEqual(
            set(submissions[0].keys()),
            {
                "id",
                "dateModified",
                "dateCreated",
                "frameworkID",
                "qualificationID",
                "date",
                "status",
                "datePublished",
                "tenderers",
                "documents",
            },
        )
        self.assertEqual(
            submissions[0]["tenderers"][0]["address"]["streetAddress"],
            MASK_STRING,
        )
        self.assertEqual(
            submissions[0]["documents"][0]["url"],
            MASK_STRING,
        )


def patch_submission_draft(self):
    data = deepcopy(self.initial_submission_data)
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

    submission_invalid_patch_data = {
        "date": (get_now() + timedelta(days=2)).isoformat(),
        "dateModified": (get_now() + timedelta(days=1)).isoformat(),
        "datePublished": (get_now() + timedelta(days=1)).isoformat(),
        "owner": "changed",
        "qualificationID": "0" * 32,
        "submissionType": "changed",
    }
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": submission_invalid_patch_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    error_fields = [field["name"] for field in response.json["errors"]]
    self.assertListEqual(sorted(error_fields), list(submission_invalid_patch_data.keys()))
    submission_patch_data = {
        "tenderers": [
            {
                "name": "Оновленна назва",
                "name_en": "Updated name",
                "identifier": {
                    "legalName_en": "dus.gov.ua",
                    "legalName": "Оновлено",
                    "scheme": "UA-EDR",
                    "id": "00037260",
                    "uri": "http://www.dus.gov.ua/",
                },
                "address": {
                    "countryName": "Україна",
                    "postalCode": "01229",
                    "region": "м. Київ",
                    "locality": "м. Київ",
                    "streetAddress": "вул. Андрія Малишка, 11, корпус 1",
                },
                "contactPoint": {
                    "name": "Оновлена назва",
                    "name_en": "State administration",
                    "telephone": "+0440000001",
                    "email": "someemaill@test.com",
                },
                "scale": "micro",
            }
        ],
        "frameworkID": "0" * 32,
    }
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": submission_patch_data},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "url", "name": "framework_id", "description": "Not Found"}],
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


def patch_submission_draft_to_active(self):
    data = deepcopy(self.initial_submission_data)
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
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotEqual(response.json["data"]["date"], submission["date"])
    self.assertNotEqual(response.json["data"]["dateModified"], submission["dateModified"])
    self.assertIn("qualificationID", response.json["data"])
    self.assertEqual(len(response.json["data"]["qualificationID"]), 32)

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

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "deleted"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


def patch_submission_draft_to_active_invalid(self):
    data = deepcopy(self.initial_submission_data)
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

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

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

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': 'Tenderer already have active submission for framework %s' % self.framework_id,
                'location': 'body',
                'name': 'data',
            }
        ],
    )


def patch_submission_active(self):
    data = deepcopy(self.initial_submission_data)
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

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "active")

    data["tenderers"][0]["name"] = "Updated name"

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": {}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Can't update submission in current (active) status",
                'location': 'body',
                'name': 'data',
            }
        ],
    )

    statuses = ("active", "draft", "deleted", "complete")

    for status in statuses:
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(submission["id"], token),
            {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': "Can't update submission in current (active) status",
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )


def patch_submission_active_fast(self):
    target = "openprocurement.framework.core.procedure.state.submission.FAST_CATALOGUE_FLOW_FRAMEWORK_IDS"

    data = deepcopy(self.initial_submission_data)
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

    with mock.patch(target, self.framework_id):
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(submission["id"], token),
            {"data": {"status": "active"}},
        )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "complete")

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "complete")

    response = self.app.get("/qualifications/{}".format(submission["qualificationID"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "active")


def patch_submission_draft_to_deleted(self):
    data = deepcopy(self.initial_submission_data)
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

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "deleted"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "deleted")


def patch_submission_deleted(self):
    data = deepcopy(self.initial_submission_data)
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

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "deleted"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    self.assertEqual(submission["status"], "deleted")

    data["tenderers"][0]["name"] = "Updated name"
    data.pop("submissionType", None)

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Can't update submission in current (deleted) status",
                'location': 'body',
                'name': 'data',
            }
        ],
    )

    statuses = ("active", "draft", "deleted", "complete")

    for status in statuses:
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(submission["id"], token),
            {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': "Can't update submission in current (deleted) status",
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )


def patch_submission_complete(self):
    data = deepcopy(self.initial_submission_data)
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
            "/submissions/{}?acc_token={}".format(submission["id"], token),
            {"data": {"status": status}},
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    'description': "Can't update submission in current (complete) status",
                    'location': 'body',
                    'name': 'data',
                }
            ],
        )


def submission_fields(self):
    data = deepcopy(self.initial_submission_data)
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
    fields = set(
        [
            "id",
            "dateModified",
            "date",
            "status",
            "owner",
        ]
    )
    self.assertEqual(set(submission) - set(self.initial_submission_data), fields)
    self.assertIn(submission["id"], response.headers["Location"])
    self.assertIn("submissionType", submission)

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    submission = response.json["data"]
    fields.update(("qualificationID", "datePublished"))
    self.assertEqual(set(submission) - set(self.initial_submission_data), fields)


def get_submission(self):
    response = self.app.get("/submissions")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    data = deepcopy(self.initial_submission_data)
    response = self.app.post_json(
        "/submissions",
        {
            "data": data,
            "config": self.initial_submission_config,
        },
    )
    self.assertEqual(response.status, "201 Created")
    submission = response.json["data"]

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], submission)

    response = self.app.get("/submissions/{}?opt_jsonp=callback".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"data": {"', response.body.decode())

    response = self.app.get("/submissions/{}?opt_pretty=1".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "data": {\n        "', response.body.decode())


def date_submission(self):
    response = self.app.get("/submissions")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    data = deepcopy(self.initial_submission_data)
    response = self.app.post_json(
        "/submissions",
        {
            "data": data,
            "config": self.initial_submission_config,
        },
    )
    self.assertEqual(response.status, "201 Created")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    date = submission["date"]

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], date)

    tenderer = deepcopy(self.initial_submission_data["tenderers"][0])
    tenderer["name"] = "Updated title"
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": {"tenderers": [tenderer]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], date)

    with freeze_time((get_now() + timedelta(days=1)).isoformat()):
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

    data = deepcopy(self.initial_submission_data)
    response = self.app.post_json(
        "/submissions",
        {
            "data": data,
            "config": self.initial_submission_config,
        },
    )
    self.assertEqual(response.status, "201 Created")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    dateModified = submission["dateModified"]

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["dateModified"], dateModified)

    with freeze_time((get_now() + timedelta(days=1)).isoformat()):
        tenderer = deepcopy(self.initial_submission_data["tenderers"][0])
        tenderer["name"] = "Draft_change"
        response = self.app.patch_json(
            "/submissions/{}?acc_token={}".format(submission["id"], token),
            {"data": {"tenderers": [tenderer]}},
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

    data = deepcopy(self.initial_submission_data)
    response = self.app.post_json(
        "/submissions",
        {
            "data": data,
            "config": self.initial_submission_config,
        },
    )
    self.assertEqual(response.status, "201 Created")
    submission = response.json["data"]
    token = response.json["access"]["token"]
    self.assertNotIn("datePublished", submission)

    response = self.app.get("/submissions/{}".format(submission["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["data"]["date"], date)

    tenderer = deepcopy(self.initial_submission_data["tenderers"][0])
    tenderer["name"] = "Updated title"
    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission["id"], token),
        {"data": {"tenderers": [tenderer]}},
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
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "submission_id"}]
    )

    response = self.app.patch_json("/submissions/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Not Found", "location": "url", "name": "submission_id"}],
    )


def submission_token_invalid(self):
    data = deepcopy(self.initial_submission_data)
    response = self.app.post_json(
        "/submissions",
        {
            "data": data,
            "config": self.initial_submission_config,
        },
    )
    self.assertEqual(response.status, "201 Created")
    submission_id = response.json["data"]["id"]

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission_id, "fake token"), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.patch_json(
        "/submissions/{}?acc_token={}".format(submission_id, "токен з кирилицею"),
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
    response = self.app.get("/submissions/{}/documents".format(self.submission_id))
    documents = response.json["data"]
    self.assertEqual(len(documents), len(self.initial_submission_data["documents"]))


def get_document_by_id(self):
    documents = self.mongodb.submissions.get(self.submission_id).get("documents")
    for doc in documents:
        response = self.app.get("/submissions/{}/documents/{}".format(self.submission_id, doc["id"]))
        document = response.json["data"]
        self.assertEqual(doc["id"], document["id"])
        self.assertEqual(doc["title"], document["title"])
        self.assertEqual(doc["format"], document["format"])
        self.assertEqual(doc["datePublished"], document["datePublished"])


def create_submission_document_forbidden(self):
    # without acc_token
    response = self.app.post(
        "/submissions/{}/documents".format(self.submission_id),
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
            "/submissions/{}/documents?acc_token={}".format(self.submission_id, self.submission_token),
            upload_files=[("file", "укр.doc", b"content")],
            status=403,
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(
            response.json["errors"],
            [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}],
        )


def create_submission_documents(self):
    response = self.app.post_json(
        "/submissions/{}/documents?acc_token={}".format(self.submission_id, self.submission_token),
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
    self.assertEqual(response.content_type, "application/json")


def create_submission_document_json_bulk(self):
    response = self.app.post_json(
        "/submissions/{}/documents?acc_token={}".format(self.submission_id, self.submission_token),
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

    submission = self.mongodb.submissions.get(self.submission_id)
    doc_1 = submission["documents"][0]
    doc_2 = submission["documents"][1]
    self.assertEqual("name1.doc", doc_1["title"])
    self.assertEqual("name2.doc", doc_2["title"])

    response = self.app.get("/submissions/{}/documents".format(self.submission_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    doc_1 = response.json["data"][0]
    doc_2 = response.json["data"][1]
    self.assertEqual("name1.doc", doc_1["title"])
    self.assertEqual("name2.doc", doc_2["title"])


def document_not_found(self):
    response = self.app.get("/submissions/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "submission_id"}]
    )

    response = self.app.post_json(
        "/submissions/some_id/documents",
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
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "submission_id"}]
    )
    response = self.app.put_json(
        "/submissions/some_id/documents/some_id",
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
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "submission_id"}]
    )

    response = self.app.put_json(
        "/submissions/{}/documents/some_id".format(self.submission_id),
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

    response = self.app.get("/submissions/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "submission_id"}]
    )

    response = self.app.get("/submissions/{}/documents/some_id".format(self.submission_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}])


def put_submission_document(self):
    response = self.app.post_json(
        "/submissions/{}/documents?acc_token={}".format(self.submission_id, self.submission_token),
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
            "/submissions/{}/documents/{}?acc_token={}".format(self.submission_id, doc_id, self.submission_token),
            {
                "data": {
                    "title": "name name.doc",
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
        submission = self.mongodb.submissions.get(self.submission_id)
        self.assertIn(key, submission["documents"][-1]["url"])

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

        response = self.app.post_json(
            "/submissions/{}/documents?acc_token={}".format(self.submission_id, self.submission_token),
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

        response = self.app.get("/submissions/{}/documents".format(self.submission_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(dateModified2, response.json["data"][0]["dateModified"])
        self.assertEqual(dateModified, response.json["data"][1]["dateModified"])
    response = self.app.put_json(
        "/submissions/{}/documents/{}?acc_token={}".format(self.submission_id, doc_id, self.submission_token),
        {
            "data": {
                "title": "name name.doc",
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
    framework = self.mongodb.submissions.get(self.submission_id)
    self.assertIn(key, framework["documents"][-1]["url"])

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
    response = self.app.put_json(
        "/submissions/{}/documents/{}?acc_token={}".format(self.submission_id, doc_id, self.submission_token),
        {
            "data": {
                "title": "name name.doc",
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
                "description": "Can't update document in current (complete) submission status",
                "location": "body",
                "name": "data",
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
                "description": "Can't update document in current (complete) submission status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def put_submission_document_fast(self):
    target = "openprocurement.framework.core.procedure.validation.FAST_CATALOGUE_FLOW_FRAMEWORK_IDS"

    with mock.patch(target, self.framework_id):
        response = self.app.post_json(
            "/submissions/{}/documents?acc_token={}".format(
                self.submission_id,
                self.submission_token,
            ),
            {
                "data": {
                    "title": "укр.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
    self.set_submission_status("complete")

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("укр.doc", response.json["data"]["title"])
    doc_id = response.json["data"]["id"]
    dateModified = response.json["data"]["dateModified"]
    self.assertIn(doc_id, response.headers["Location"])

    with mock.patch(target, self.framework_id):
        response = self.app.put_json(
            "/submissions/{}/documents/{}?acc_token={}".format(
                self.submission_id,
                doc_id,
                self.submission_token,
            ),
            {
                "data": {
                    "title": "name name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                }
            },
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get(
        "/submissions/{}/documents".format(
            self.submission_id,
            self.submission_token,
        )
    )
    self.assertEqual(response.status, "200 OK")
    doc_id = response.json["data"][0]["id"]

    with mock.patch(target, self.framework_id):
        response = self.app.patch_json(
            "/submissions/{}/documents/{}?acc_token={}".format(
                self.submission_id,
                doc_id,
                self.submission_token,
            ),
            {"data": {"documentType": None}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
