from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

import mock
from freezegun import freeze_time

from openprocurement.api.constants import (
    ROUTE_PREFIX,
    FRAMEWORK_ENQUIRY_PERIOD_OFF_FROM,
)
from openprocurement.api.context import set_now
from openprocurement.api.tests.base import change_auth
from openprocurement.api.utils import get_now
from openprocurement.framework.dps.models import Framework
from openprocurement.framework.core.utils import ENQUIRY_PERIOD_DURATION
from openprocurement.framework.core.utils import (
    calculate_framework_date,
    get_framework_unsuccessful_status_check_date,
)


def simple_add_framework(self):
    set_now()

    u = Framework(self.initial_data)
    u.prettyID = "UA-F"
    u.dateModified = get_now().isoformat()

    assert u.id is None
    assert u.rev is None

    u.id = uuid4().hex
    self.mongodb.frameworks.save(u, insert=True)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.mongodb.frameworks.get(u.id)

    assert u.prettyID == fromdb["prettyID"]
    assert u.doc_type is None

    self.mongodb.frameworks.delete(u.id)


def listing(self):
    response = self.app.get("/frameworks")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    frameworks = []

    for i in range(3):
        offset = get_now().timestamp()
        response = self.app.post_json(
            "/frameworks", {
                "data": self.initial_data,
                "config": self.initial_config,
            }
            )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.app.patch_json(
            "/frameworks/{}?acc_token={}".format(response.json["data"]["id"], response.json["access"]["token"]),
            {"data": {"status": "active"}}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        frameworks.append(response.json["data"])
    ids = ",".join([i["id"] for i in frameworks])

    response = self.app.get("/frameworks")
    self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in frameworks]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in frameworks])
    )
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in frameworks])
    )

    response = self.app.get("/frameworks?offset={}".format(offset))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/frameworks?limit=2")
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

    response = self.app.get("/frameworks", params=[("opt_fields", "status")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "status"})
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/frameworks", params=[("opt_fields", "status,owner")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "status"})
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/frameworks?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in frameworks]))
    self.assertEqual(
        [i["dateModified"]
         for i in response.json["data"]], sorted([i["dateModified"] for i in frameworks], reverse=True)
    )

    response = self.app.get("/frameworks?descending=1&limit=2")
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

    test_framework_data2 = self.initial_data.copy()
    test_framework_data2["mode"] = "test"
    response = self.app.post_json(
        "/frameworks", {
            "data": test_framework_data2,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(response.json["data"]["id"], response.json["access"]["token"]),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    while True:
        response = self.app.get("/frameworks?mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/frameworks?mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def listing_changes(self):
    response = self.app.get("/frameworks?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    frameworks = []

    for i in range(3):
        response = self.app.post_json(
            "/frameworks", {
                "data": self.initial_data,
                "config": self.initial_config,
            }
            )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.app.patch_json(
            "/frameworks/{}?acc_token={}".format(response.json["data"]["id"], response.json["access"]["token"]),
            {"data": {"status": "active"}}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        frameworks.append(response.json["data"])

    ids = ",".join([i["id"] for i in frameworks])

    while True:
        response = self.app.get("/frameworks?feed=changes")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in frameworks]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in frameworks])
    )
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in frameworks])
    )

    response = self.app.get("/frameworks?feed=changes&limit=2")
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

    response = self.app.get("/frameworks?feed=changes", params=[("opt_fields", "status")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/frameworks?feed=changes", params=[("opt_fields", "status,owner")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/frameworks?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in frameworks]))
    self.assertEqual(
        [i["dateModified"]
         for i in response.json["data"]], sorted([i["dateModified"] for i in frameworks], reverse=True)
    )

    response = self.app.get("/frameworks?feed=changes&descending=1&limit=2")
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

    test_framework_data2 = self.initial_data.copy()
    test_framework_data2["mode"] = "test"
    response = self.app.post_json(
        "/frameworks", {
            "data": test_framework_data2,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(response.json["data"]["id"], response.json["access"]["token"]),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    while True:
        response = self.app.get("/frameworks?feed=changes&mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/frameworks?feed=changes&mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def listing_draft(self):
    response = self.app.get("/frameworks")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    frameworks = []
    data = self.initial_data

    for i in range(3):
        # Active frameworks
        response = self.app.post_json(
            "/frameworks", {
                "data": self.initial_data,
                "config": self.initial_config,
            }
            )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.app.patch_json(
            "/frameworks/{}?acc_token={}".format(response.json["data"]["id"], response.json["access"]["token"]),
            {"data": {"status": "active"}}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        frameworks.append(response.json["data"])
        # Draft frameworks
        response = self.app.post_json(
            "/frameworks", {
                "data": self.initial_data,
                "config": self.initial_config,
            }
            )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    ids = ",".join([i["id"] for i in frameworks])

    while True:
        response = self.app.get("/frameworks")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in frameworks]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in frameworks])
    )
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in frameworks])
    )


def create_framework_draft_invalid(self):
    request_path = "/frameworks"
    response = self.app.post(request_path, "data", status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Content-Type header should be one of ['application/json']",
                "location": "header",
                "name": "Content-Type",
            }
        ],
    )

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

    data = {"frameworkType": "invalid_value"}
    response = self.app.post_json(request_path, {"data": data}, status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Not implemented", "location": "body", "name": "frameworkType"}],
    )

    data = {
        "frameworkType": self.initial_data["frameworkType"],
        "invalid_field": "invalid_value",
    }
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    data = {
        "frameworkType": self.initial_data["frameworkType"],
        "title_ru": "invalid_value",
    }
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "qualificationPeriod"},
        response.json["errors"],
    )
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "procuringEntity"},
        response.json["errors"],
    )
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "classification"},
        response.json["errors"],
    )
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "title"},
        response.json["errors"]
    )

    data = {
        "frameworkType": self.initial_data["frameworkType"],
        "qualificationPeriod": {"endDate": "invalid_value"}
    }
    response = self.app.post_json(
        request_path, {"data": data}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"endDate": ["Could not parse invalid_value. Should be ISO8601."]},
                "location": "body",
                "name": "qualificationPeriod",
            }
        ],
    )

    data = {
        "frameworkType": self.initial_data["frameworkType"],
        "qualificationPeriod": {"endDate": "9999-12-31T23:59:59.999999"}
    }
    response = self.app.post_json(
        request_path, {"data": data}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{
            "description": {
                "endDate": ["date value out of range"]
            }, "location": "body", "name": "qualificationPeriod"
        }],
    )

    data = deepcopy(self.initial_data)
    data["classification"]["scheme"] = "Не ДКПП"
    data["classification"]["id"] = "9999999919"
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertTrue(
        response.json["errors"][0]["description"]["scheme"][0].startswith("Value must be one of")
    )
    data["classification"]["scheme"] = "ДК021"
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertTrue(
        response.json["errors"][0]["description"]["id"][0].startswith("Value must be one of")
    )

    data = deepcopy(self.initial_data)
    data["procuringEntity"]["address"]["region"] = "???"
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': {'address': {'region': ['field address:region not exist in ua_regions catalog']}},
                'location': 'body', 'name': 'procuringEntity'
            }
        ],
    )

    data = deepcopy(self.initial_data)
    del data["procuringEntity"]["contactPoint"]["telephone"]
    del data["procuringEntity"]["contactPoint"]["email"]
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': {
                    'contactPoint': {
                        'email': ['This field is required.'],
                    }
                },
                'location': 'body', 'name': 'procuringEntity'
            }
        ],
    )


def create_framework_draft_invalid_kind(self):
    request_path = "/frameworks"

    data = deepcopy(self.initial_data)
    data["procuringEntity"]["kind"] = "invalid"
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': {
                    'kind': [
                        "Value must be one of ('authority', 'central', 'defense', 'general', 'other', 'social', 'special')."
                    ]
                },
                'location': 'body', 'name': 'procuringEntity'
            }
        ],
    )


def create_framework_draft(self):
    response = self.app.post_json(
        "/frameworks", {
            "data": self.initial_data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(framework["status"], "draft")

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    self.assertEqual(framework["status"], "active")

    response = self.app.get("/frameworks/{}".format(framework["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    self.assertEqual(framework["status"], "active")
    self.assertTrue(framework["prettyID"].startswith("UA-F"))


def create_framework_config_test(self):
    initial_config = deepcopy(self.initial_config)
    initial_config["test"] = True
    response = self.create_framework(config=initial_config)

    token = response.json["access"]["token"]

    framework = response.json["data"]
    self.assertNotIn("config", framework)
    self.assertEqual(framework["mode"], "test")
    self.assertEqual(response.json["config"], initial_config)

    response = self.activate_framework()

    framework = response.json["data"]
    self.assertNotIn("config", framework)
    self.assertEqual(framework["mode"], "test")
    self.assertEqual(response.json["config"], initial_config)

    response = self.app.get("/frameworks/{}".format(framework["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    framework = response.json["data"]
    self.assertNotIn("config", framework)
    self.assertEqual(framework["mode"], "test")
    self.assertEqual(response.json["config"], initial_config)


def create_framework_config_restricted(self):
    data = deepcopy(self.initial_data)

    config = deepcopy(self.initial_config)
    config.pop("restrictedDerivatives")
    response = self.app.post_json(
        "/frameworks", {
            "data": data,
            "config": config,
        }, status=422
        )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [
            {
                "description": ["restrictedDerivatives is required for this framework type"],
                "location": "body",
                "name": "restrictedDerivatives",
            }
        ]
        )

    config["restrictedDerivatives"] = True
    response = self.app.post_json(
        "/frameworks", {
            "data": data,
            "config": config,
        }, status=422
        )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [
            {
                "description": ["restrictedDerivatives must be false for non-defense procuring entity"],
                "location": "body",
                "name": "restrictedDerivatives",
            }
        ]
        )

    data["procuringEntity"]["kind"] = "defense"
    config["restrictedDerivatives"] = False
    response = self.app.post_json(
        "/frameworks", {
            "data": data,
            "config": config,
        }, status=422
        )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [
            {
                "description": ["restrictedDerivatives must be true for defense procuring entity"],
                "location": "body",
                "name": "restrictedDerivatives",
            }
        ]
        )

    data["procuringEntity"]["kind"] = "defense"
    config = deepcopy(self.initial_config)
    config["restrictedDerivatives"] = True
    response = self.app.post_json(
        "/frameworks", {
            "data": data,
            "config": config,
        }
        )

    framework = response.json["data"]
    framework_owner = framework["owner"]

    self.assertNotIn("config", framework)
    self.assertTrue(response.json["config"]["restrictedDerivatives"])
    self.assertEqual(framework["procuringEntity"]["kind"], "defense")


def patch_framework_draft(self):
    data = deepcopy(self.initial_data)
    response = self.app.post_json(
        "/frameworks", {
            "data": data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(framework["status"], "draft")

    framework_ignore_patch_data = {
        "date": (get_now() + timedelta(days=2)).isoformat(),
        "dateModified": (get_now() + timedelta(days=1)).isoformat(),
        "owner": "changed",
        "period": {"endDate": (get_now() + timedelta(days=1)).isoformat()},
        "enquiryPeriod": {"endDate": (get_now() + timedelta(days=1)).isoformat()},
        "frameworkType": "changed",
    }
    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": framework_ignore_patch_data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    framework = self.app.get("/frameworks/{}".format(framework["id"], token)).json["data"]
    for field in framework_ignore_patch_data:
        self.assertNotEqual(framework.get(field, ""), framework_ignore_patch_data[field])

    qualification_endDate = (get_now() + timedelta(days=90)).isoformat()
    framework_patch_data = {
        "procuringEntity": {
            "contactPoint": {
                "telephone": "+04400000001",
                "name": "changed",
                "email": "bb@bb.ua"
            },
            "identifier": {
                "legalName": "changed"
            },
            "address": {
                "postalCode": "changed",
                "streetAddress": "changed",
                "locality": "changed"
            },
            "name": "changed"
        },
        "additionalClassifications": [
            {
                "scheme": "changed",
                "id": "changed",
                "description": "changed"
            }
        ],
        "classification": {
            "description": "changed",
            "id": "44115810-0"
        },
        "title": "changed",
        "description": "changed",
        "qualificationPeriod": {"endDate": qualification_endDate},
    }
    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": framework_patch_data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    framework = self.app.get("/frameworks/{}".format(framework["id"], token)).json["data"]
    contact = framework["procuringEntity"]["contactPoint"]
    self.assertEqual(contact["telephone"], framework_patch_data["procuringEntity"]["contactPoint"]["telephone"])
    self.assertEqual(contact["name"], framework_patch_data["procuringEntity"]["contactPoint"]["name"])
    self.assertEqual(contact["email"], framework_patch_data["procuringEntity"]["contactPoint"]["email"])
    identifier = framework["procuringEntity"]["identifier"]
    self.assertEqual(identifier["legalName"], framework_patch_data["procuringEntity"]["identifier"]["legalName"])
    address = framework["procuringEntity"]["address"]
    self.assertEqual(address["postalCode"], framework_patch_data["procuringEntity"]["address"]["postalCode"])
    self.assertEqual(address["streetAddress"], framework_patch_data["procuringEntity"]["address"]["streetAddress"])
    self.assertEqual(address["locality"], framework_patch_data["procuringEntity"]["address"]["locality"])
    self.assertEqual(framework["procuringEntity"]["name"], framework_patch_data["procuringEntity"]["name"])
    additional = framework["additionalClassifications"][0]
    self.assertEqual(additional["scheme"], framework_patch_data["additionalClassifications"][0]["scheme"])
    self.assertEqual(additional["id"], framework_patch_data["additionalClassifications"][0]["id"])
    self.assertEqual(additional["description"], framework_patch_data["additionalClassifications"][0]["description"])
    classification = framework["classification"]
    self.assertEqual(classification["id"], framework_patch_data["classification"]["id"])
    self.assertEqual(classification["description"], framework_patch_data["classification"]["description"])
    self.assertEqual(framework["title"], framework_patch_data["title"])
    self.assertEqual(framework["description"], framework_patch_data["description"])
    self.assertEqual(framework["qualificationPeriod"], framework_patch_data["qualificationPeriod"])


def patch_framework_draft_to_active(self):
    data = deepcopy(self.initial_data)
    response = self.app.post_json(
        "/frameworks", {
            "data": data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(framework["status"], "draft")

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotEqual(response.json["data"]["date"], framework["date"])

    data = deepcopy(self.initial_data)
    enquiry_end_date = calculate_framework_date(
        get_now(), timedelta(days=ENQUIRY_PERIOD_DURATION), data, working_days=True, ceil=True
    )
    data["qualificationPeriod"]["endDate"] = (enquiry_end_date + timedelta(days=30)).isoformat()
    response = self.app.post_json(
        "/frameworks", {
            "data": data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(framework["status"], "draft")

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotEqual(response.json["data"]["date"], framework["date"])

    data = deepcopy(self.initial_data)
    data["qualificationPeriod"]["endDate"] = (get_now() + timedelta(days=1095)).isoformat()
    response = self.app.post_json(
        "/frameworks", {
            "data": data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(framework["status"], "draft")

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotEqual(response.json["data"]["date"], framework["date"])


def patch_framework_draft_to_active_invalid(self):
    data = deepcopy(self.initial_data)
    enquiry_end_date = calculate_framework_date(
        get_now(), timedelta(days=ENQUIRY_PERIOD_DURATION), data, working_days=True, ceil=True
    )
    if get_now() > FRAMEWORK_ENQUIRY_PERIOD_OFF_FROM:
        enquiry_end_date = get_now()
    data["qualificationPeriod"]["endDate"] = (enquiry_end_date + timedelta(days=29)).isoformat()
    response = self.app.post_json(
        "/frameworks", {
            "data": data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(framework["status"], "draft")

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body", "name": "data",
                "description": "qualificationPeriod must be at least 30 full calendar days long"
            }
        ]
    )

    data = deepcopy(self.initial_data)
    data["qualificationPeriod"]["endDate"] = (get_now() + timedelta(days=1096)).isoformat()
    response = self.app.post_json(
        "/frameworks", {
            "data": data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(framework["status"], "draft")

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body", "name": "data",
                "description": "qualificationPeriod must be less than 1095 full calendar days long"
            }
        ]
    )


def patch_framework_active(self):
    data = deepcopy(self.initial_data)
    response = self.app.post_json(
        "/frameworks", {
            "data": data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(framework["status"], "draft")

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    self.assertEqual(framework["status"], "active")

    framework_ignore_patch_data = {
        "classification": {},
        "title": "",
        "additionalClassifications": [],
        "procuringEntity": {},
    }

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": framework_ignore_patch_data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    for field in framework_ignore_patch_data:
        self.assertEqual(framework[field], response.json["data"][field])

    qualificationPeriod_endDate = (get_now() + timedelta(days=100)).isoformat()
    framework_patch_data = {
        "procuringEntity": {
            "contactPoint": {
                "telephone": "+0440000001",
                "name": "changed",
                "email": "bb@bb.com",
            }
        },
        "description": "changed",
        "qualificationPeriod": {"endDate": qualificationPeriod_endDate}
    }
    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": framework_patch_data}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    contact = framework["procuringEntity"]["contactPoint"]
    self.assertEqual(contact["telephone"], framework_patch_data["procuringEntity"]["contactPoint"]["telephone"])
    self.assertEqual(contact["name"], framework_patch_data["procuringEntity"]["contactPoint"]["name"])
    self.assertEqual(contact["email"], framework_patch_data["procuringEntity"]["contactPoint"]["email"])
    self.assertEqual(framework["description"], framework_patch_data["description"])
    self.assertEqual(
        framework["qualificationPeriod"]["endDate"], framework_patch_data["qualificationPeriod"]["endDate"]
    )


def framework_fields(self):
    response = self.app.post_json(
        "/frameworks", {
            "data": self.initial_data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    token = response.json["access"]["token"]
    fields = {
        "id",
        "dateModified",
        "dateCreated",
        "prettyID",
        "date",
        "status",
        "owner",
    }
    self.assertEqual(set(framework) - set(self.initial_data), fields)
    self.assertIn(framework["id"], response.headers["Location"])

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    framework = response.json["data"]
    fields.update(("next_check", "enquiryPeriod", "period"))
    self.assertEqual(set(framework) - set(self.initial_data), fields)


def get_framework(self):
    response = self.app.get("/frameworks")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json(
        "/frameworks", {
            "data": self.initial_data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    framework = response.json["data"]

    response = self.app.get("/frameworks/{}".format(framework["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], framework)

    response = self.app.get("/frameworks/{}?opt_jsonp=callback".format(framework["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"data": {"', response.body.decode())

    response = self.app.get("/frameworks/{}?opt_pretty=1".format(framework["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "data": {\n        "', response.body.decode())


def periods_deletion(self):
    response = self.app.post_json(
        "/frameworks", {
            "data": self.initial_data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    framework = response.json["data"]
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token),
        {"data": {"qualificationPeriod": {"endDate": None}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"endDate": ["This field is required."]},
                "location": "body",
                "name": "qualificationPeriod",
            }
        ],
    )

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    period = response.json["data"]["period"]
    enquiryPeriod = response.json["data"]["enquiryPeriod"]

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": {"period": {"startDate": None}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["period"], period)

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": {"enquiryPeriod": {"startDate": None}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["enquiryPeriod"], enquiryPeriod)


def date_framework(self):
    response = self.app.get("/frameworks")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json(
        "/frameworks", {
            "data": self.initial_data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    framework = response.json["data"]
    token = response.json["access"]["token"]
    date = framework["date"]

    response = self.app.get("/frameworks/{}".format(framework["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], date)

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": {"title": "Draft_change"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["date"], date)

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["dateModified"], date)


def dateModified_framework(self):
    response = self.app.get("/frameworks")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json(
        "/frameworks", {
            "data": self.initial_data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    framework = response.json["data"]
    token = response.json["access"]["token"]
    dateModified = framework["dateModified"]

    response = self.app.get("/frameworks/{}".format(framework["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["dateModified"], dateModified)

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": {"title": "Draft_change"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["dateModified"], dateModified)
    framework = response.json["data"]
    dateModified = framework["dateModified"]

    response = self.app.get("/frameworks/{}".format(framework["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], framework)
    self.assertEqual(response.json["data"]["dateModified"], dateModified)

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework["id"], token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["dateModified"], dateModified)
    framework = response.json["data"]
    dateModified = framework["dateModified"]

    response = self.app.get("/frameworks/{}".format(framework["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], framework)
    self.assertEqual(response.json["data"]["dateModified"], dateModified)


def framework_not_found(self):
    response = self.app.get("/frameworks")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/frameworks/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "framework_id"}]
    )

    response = self.app.patch_json("/frameworks/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "framework_id"}]
    )


def framework_token_invalid(self):
    response = self.app.post_json(
        "/frameworks", {
            "data": self.initial_data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    framework_id = response.json["data"]["id"]

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework_id, "fake token"), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}]
    )

    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(framework_id, "токен з кирилицею"), {"data": {}}, status=422,
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


def accreditation_level(self):
    with change_auth(self.app, ("Basic", ("broker1", ""))):
        response = self.app.post_json(
            "/frameworks", {
                "data": self.initial_data,
                "config": self.initial_config,
            }
            )
        self.assertEqual(response.status, "201 Created")

    with change_auth(self.app, ("Basic", ("broker2", ""))):
        response = self.app.post_json(
            "/frameworks", {
                "data": self.initial_data,
                "config": self.initial_config,
            }, status=403
            )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{
                 "location": "url", "name": "accreditation",
                 "description": "Broker Accreditation level does not permit framework creation"
             }],
        )

    with change_auth(self.app, ("Basic", ("broker3", ""))):
        response = self.app.post_json(
            "/frameworks", {
                "data": self.initial_data,
                "config": self.initial_config,
            }
            )
        self.assertEqual(response.status, "201 Created")

    with change_auth(self.app, ("Basic", ("broker4", ""))):
        response = self.app.post_json(
            "/frameworks", {
                "data": self.initial_data,
                "config": self.initial_config,
            }, status=403
            )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"],
            [{
                 "location": "url", "name": "accreditation",
                 "description": "Broker Accreditation level does not permit framework creation"
             }],
        )

    with change_auth(self.app, ("Basic", ("broker5", ""))):
        response = self.app.post_json(
            "/frameworks", {
                "data": self.initial_data,
                "config": self.initial_config,
            }
            )
        self.assertEqual(response.status, "201 Created")


def unsuccessful_status(self):
    # Without submissions
    response = self.app.post_json(
        "/frameworks", {
            "data": self.initial_data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.framework_id = response.json["data"]["id"]
    token = response.json["access"]["token"]
    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(self.framework_id, token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.check_chronograph()
    response = self.app.get("/frameworks/{}".format(self.framework_id))
    self.assertEqual(response.json["data"]["status"], "active")

    framework = Framework(response.json["data"])
    date = get_framework_unsuccessful_status_check_date(framework)
    with freeze_time((date + timedelta(hours=1)).isoformat()):
        self.check_chronograph()
    response = self.app.get("/frameworks/{}".format(self.framework_id))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")

    # With submissions
    response = self.app.post_json(
        "/frameworks", {
            "data": self.initial_data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.framework_id = response.json["data"]["id"]
    token = response.json["access"]["token"]
    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(self.framework_id, token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    framework = Framework(response.json["data"])
    date = get_framework_unsuccessful_status_check_date(framework)
    with freeze_time((date + timedelta(hours=1)).isoformat()):
        with mock.patch(
            "openprocurement.framework.core.utils.get_framework_number_of_submissions",
            lambda x, y: 1
        ):
            self.check_chronograph()
    response = self.app.get("/frameworks/{}".format(self.framework_id))
    self.assertEqual(response.json["data"]["status"], "active")


def complete_status(self):
    response = self.app.post_json(
        "/frameworks", {
            "data": self.initial_data,
            "config": self.initial_config,
        }
        )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.framework_id = response.json["data"]["id"]
    token = response.json["access"]["token"]
    response = self.app.patch_json(
        "/frameworks/{}?acc_token={}".format(self.framework_id, token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.check_chronograph()
    response = self.app.get("/frameworks/{}".format(self.framework_id))
    self.assertEqual(response.json["data"]["status"], "active")

    framework = Framework(response.json["data"])
    date = framework["qualificationPeriod"]["endDate"]
    with freeze_time((date + timedelta(hours=1)).isoformat()):
        with mock.patch(
            "openprocurement.framework.core.utils.get_framework_number_of_submissions",
            lambda x, y: 1
        ):
            self.check_chronograph()
    response = self.app.get("/frameworks/{}".format(self.framework_id))
    self.assertEqual(response.json["data"]["status"], "complete")
