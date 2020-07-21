# -*- coding: utf-8 -*-
import mock
import uuid
from copy import deepcopy

from datetime import datetime, timedelta

from iso8601 import parse_date
from openprocurement.api.constants import (
    ROUTE_PREFIX,
    CPV_ITEMS_CLASS_FROM,
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM,
    TZ,
)
from openprocurement.api.utils import get_now

from openprocurement.planning.api.models import Plan
from openprocurement.planning.api.constants import PROCEDURES


# PlanTest
from openprocurement.tender.core.tests.base import change_auth


def simple_add_plan(self):
    u = Plan(self.initial_data)
    u.planID = "UA-P-X"

    assert u.id is None
    assert u.rev is None

    u.store(self.db)

    assert u.id is not None
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.planID == fromdb["planID"]
    assert u.doc_type == "Plan"

    u.delete_instance(self.db)


# AccreditationPlanTest


def create_plan_accreditation(self):
    self.app.authorization = ("Basic", ("broker3", ""))
    response = self.app.post_json("/plans", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    for broker in ["broker2", "broker4"]:
        self.app.authorization = ("Basic", (broker, ""))
        response = self.app.post_json("/plans", {"data": self.initial_data}, status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Broker Accreditation level does not permit plan creation"
        )

    self.app.authorization = ("Basic", ("broker1t", ""))
    response = self.app.post_json("/plans", {"data": self.initial_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Broker Accreditation level does not permit plan creation"
    )

    response = self.app.post_json("/plans", {"data": self.initial_data_mode_test})
    self.assertEqual(response.status, "201 Created")


# PlanResourceTest


def empty_listing(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertNotIn('{\n    "', response.body)
    self.assertNotIn("callback({", response.body)
    self.assertEqual(response.json["next_page"]["offset"], "")
    self.assertNotIn("prev_page", response.json)

    response = self.app.get("/plans?opt_jsonp=callback")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertNotIn('{\n    "', response.body)
    self.assertIn("callback({", response.body)

    response = self.app.get("/plans?opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body)
    self.assertNotIn("callback({", response.body)

    response = self.app.get("/plans?opt_jsonp=callback&opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('{\n    "', response.body)
    self.assertIn("callback({", response.body)

    response = self.app.get("/plans?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertIn("descending=1", response.json["next_page"]["uri"])
    self.assertIn("limit=10", response.json["next_page"]["uri"])
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertIn("limit=10", response.json["prev_page"]["uri"])

    response = self.app.get("/plans?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertEqual(response.json["next_page"]["offset"], "")
    self.assertNotIn("prev_page", response.json)

    response = self.app.get("/plans?feed=changes&offset=0", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"Offset expired/invalid", u"location": u"params", u"name": u"offset"}],
    )

    response = self.app.get("/plans?feed=changes&descending=1&limit=10")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertIn("descending=1", response.json["next_page"]["uri"])
    self.assertIn("limit=10", response.json["next_page"]["uri"])
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertIn("limit=10", response.json["prev_page"]["uri"])


def listing(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    plans = []

    for i in range(3):
        offset = get_now().isoformat()
        response = self.app.post_json("/plans", {"data": self.initial_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        plans.append(response.json["data"])

    ids = ",".join([i["id"] for i in plans])

    while True:
        response = self.app.get("/plans")
        self.assertEqual(response.status, "200 OK")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in plans]))
    self.assertEqual(set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in plans]))
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in plans]))

    response = self.app.get("/plans?offset={}".format(offset))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/plans?limit=2")
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

    response = self.app.get("/plans", params=[("opt_fields", "budget")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertNotIn("opt_fields=budget", response.json["next_page"]["uri"])

    response = self.app.get("/plans", params=[("opt_fields", "planID")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"planID"]))
    self.assertIn("opt_fields=planID", response.json["next_page"]["uri"])

    response = self.app.get("/plans?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in plans]))
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in plans], reverse=True)
    )

    response = self.app.get("/plans?descending=1&limit=2")
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

    test_plan_data2 = self.initial_data.copy()
    test_plan_data2["mode"] = "test"
    response = self.app.post_json("/plans", {"data": test_plan_data2})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    while True:
        response = self.app.get("/plans?mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/plans?mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def listing_changes(self):
    response = self.app.get("/plans?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    plans = []

    for i in range(3):
        response = self.app.post_json("/plans", {"data": self.initial_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        plans.append(response.json["data"])

    ids = ",".join([i["id"] for i in plans])

    while True:
        response = self.app.get("/plans?feed=changes")
        self.assertEqual(response.status, "200 OK")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in plans]))
    self.assertEqual(set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in plans]))
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in plans]))

    response = self.app.get("/plans?feed=changes&limit=2")
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

    response = self.app.get("/plans?feed=changes", params=[("opt_fields", "budget")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertNotIn("opt_fields=budget", response.json["next_page"]["uri"])

    response = self.app.get("/plans?feed=changes", params=[("opt_fields", "planID")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"planID"]))
    self.assertIn("opt_fields=planID", response.json["next_page"]["uri"])

    response = self.app.get("/plans?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in plans]))
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in plans], reverse=True)
    )

    response = self.app.get("/plans?feed=changes&descending=1&limit=2")
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

    test_plan_data2 = self.initial_data.copy()
    test_plan_data2["mode"] = "test"
    response = self.app.post_json("/plans", {"data": test_plan_data2})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    while True:
        response = self.app.get("/plans?mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/plans?feed=changes&mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def create_plan_invalid(self):
    request_path = "/plans"
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

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"budget": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [u"Please use a mapping for this field or Budget instance instead of unicode."],
                u"location": u"body",
                u"name": u"budget",
            }
        ],
    )

    response = self.app.post_json(
        request_path, {"data": {"tender": {"procurementMethod": "invalid_value"}}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"procuringEntity"},
        response.json["errors"],
    )
    self.assertIn(
        {u"description": [u"This field is required."], u"location": u"body", u"name": u"classification"},
        response.json["errors"],
    )

    initial_data = deepcopy(self.initial_data)
    data = initial_data["tender"]
    initial_data["tender"] = {
        "procurementMethod": "open",
        "procurementMethodType": "reporting",
        "tenderPeriod": data["tenderPeriod"],
    }
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    initial_data["tender"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {
            u"description": {u"procurementMethodType": [u"Value must be one of {!r}.".format(PROCEDURES["open"])]},
            u"location": u"body",
            u"name": u"tender",
        },
        response.json["errors"],
    )

    data = initial_data["tender"]
    initial_data["tender"] = {
        "procurementMethod": "limited",
        "procurementMethodType": "belowThreshold",
        "tenderPeriod": data["tenderPeriod"],
    }
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    initial_data["tender"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {
            u"description": {u"procurementMethodType": [u"Value must be one of {!r}.".format(PROCEDURES["limited"])]},
            u"location": u"body",
            u"name": u"tender",
        },
        response.json["errors"],
    )

    response = self.app.post_json(
        request_path, {"data": {"tender": {"tenderPeriod": {"startDate": "invalid_value"}}}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {
                    u"tenderPeriod": {u"startDate": [u"Could not parse invalid_value. Should be ISO8601."]}
                },
                u"location": u"body",
                u"name": u"tender",
            }
        ],
    )

    response = self.app.post_json(
        request_path, {"data": {"tender": {"tenderPeriod": {"startDate": "9999-12-31T23:59:59.999999"}}}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {u"tenderPeriod": {u"startDate": [u"date value out of range"]}},
                u"location": u"body",
                u"name": u"tender",
            }
        ],
    )

    additionalClassifications = [i.pop("additionalClassifications") for i in initial_data["items"]]
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = initial_data["classification"]["id"]
        cpv_codes = [i["classification"]["id"] for i in initial_data["items"]]
        initial_data["classification"]["id"] = "99999999-9"
        for index, cpv_code in enumerate(cpv_codes):
            initial_data["items"][index]["classification"]["id"] = "99999999-9"

    if get_now() < NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM:
        response = self.app.post_json(request_path, {"data": initial_data}, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    u"description": [
                        {u"additionalClassifications": [u"This field is required."]},
                        {u"additionalClassifications": [u"This field is required."]},
                        {u"additionalClassifications": [u"This field is required."]},
                    ],
                    u"location": u"body",
                    u"name": u"items",
                }
            ],
        )

    for index, additionalClassification in enumerate(additionalClassifications):
        initial_data["items"][index]["additionalClassifications"] = additionalClassification
    if get_now() > CPV_ITEMS_CLASS_FROM:
        initial_data["classification"]["id"] = cpv_code
        for index, cpv_code in enumerate(cpv_codes):
            initial_data["items"][index]["classification"]["id"] = cpv_code

    additionalClassifications = [i["additionalClassifications"][0]["scheme"] for i in initial_data["items"]]
    for index, _ in enumerate(additionalClassifications):
        initial_data["items"][index]["additionalClassifications"][0]["scheme"] = u"Не ДКПП"
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = initial_data["classification"]["id"]
        cpv_codes = [i["classification"]["id"] for i in initial_data["items"]]
        initial_data["classification"]["id"] = "99999999-9"
        for index, cpv_code in enumerate(cpv_codes):
            initial_data["items"][index]["classification"]["id"] = "99999999-9"
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    for index, data in enumerate(additionalClassifications):
        initial_data["items"][index]["additionalClassifications"][0]["scheme"] = data
    if get_now() > CPV_ITEMS_CLASS_FROM:
        initial_data["classification"]["id"] = cpv_code
        for index, cpv_code in enumerate(cpv_codes):
            initial_data["items"][index]["classification"]["id"] = cpv_code
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.assertEqual(
            response.json["errors"],
            [
                {
                    u"description": [
                        {
                            u"additionalClassifications": [
                                u"One of additional classifications should be one of [ДК003, ДК015, ДК018, specialNorms]."
                            ]
                        }
                        for _ in additionalClassifications
                    ],
                    u"location": u"body",
                    u"name": u"items",
                }
            ],
        )
    else:
        self.assertEqual(
            response.json["errors"],
            [
                {
                    u"description": [
                        {
                            u"additionalClassifications": [
                                u"One of additional classifications should be one of [ДКПП, NONE, ДК003, ДК015, ДК018]."
                            ]
                        }
                        for _ in additionalClassifications
                    ],
                    u"location": u"body",
                    u"name": u"items",
                }
            ],
        )

    data = initial_data["procuringEntity"]["name"]
    del initial_data["procuringEntity"]["name"]
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    initial_data["procuringEntity"]["name"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"name": [u"This field is required."]}, u"location": u"body", u"name": u"procuringEntity"}],
    )

    data = initial_data["budget"]
    del initial_data["budget"]
    initial_data["tender"]["procurementMethodType"] = "belowThreshold"
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    initial_data["budget"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"This field is required."], u"location": u"body", u"name": u"budget"}],
    )

    data = initial_data["items"][0].copy()
    classification = data["classification"].copy()
    classification["id"] = u"31519200-9"
    data["classification"] = classification
    initial_data["items"] = [initial_data["items"][0], data]
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    initial_data["items"] = initial_data["items"][:1]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.assertEqual(
            response.json["errors"],
            [
                {
                    u"description": [{u"classification": [u"CPV class of items should be identical to root cpv"]}],
                    u"location": u"body",
                    u"name": u"items",
                }
            ],
        )
    else:
        self.assertEqual(
            response.json["errors"],
            [
                {
                    u"description": [{u"classification": [u"CPV group of items be identical to root cpv"]}],
                    u"location": u"body",
                    u"name": u"items",
                }
            ],
        )

    classification_id = initial_data["classification"]["id"]
    initial_data["classification"]["id"] = u"33600000-6"
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    initial_data["classification"]["id"] = classification_id
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u"classification": [u"CPV group of items be identical to root cpv"]}],
                u"location": u"body",
                u"name": u"items",
            }
        ],
    )

    classification_id = initial_data["classification"]["id"]
    initial_data["classification"]["id"] = u"33600000-6"
    item = initial_data["items"][0].copy()
    data = initial_data["items"][0].copy()
    classification = data["classification"].copy()
    classification["id"] = u"33610000-9"
    data["classification"] = classification
    data2 = initial_data["items"][0].copy()
    classification = data2["classification"].copy()
    classification["id"] = u"33620000-2"
    data2["classification"] = classification
    initial_data["items"] = [data, data2]
    response = self.app.post_json(request_path, {"data": initial_data})
    initial_data["classification"]["id"] = classification_id
    initial_data["items"] = [item]
    self.assertEqual(response.status, "201 Created")


def create_plan_invalid_procurement_method_type(self):
    request_path = "/plans"
    initial_data = deepcopy(self.initial_data)
    response = self.app.post_json(request_path, {"data": initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    plan = response.json["data"]
    acc_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {
            "data": {
                "tender": {
                    "procurementMethod": "",
                    "procurementMethodType": ""
                }
            }
        },
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {
                    u'procurementMethodType': [u"Value must be one of ('centralizedProcurement',)."]
                },
                u"location": u"body",
                u"name": u"tender",
            }
        ],
    )

    initial_data["tender"]["procurementMethod"] = ""
    initial_data["tender"]["procurementMethodType"] = ""
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {
                    u'procurementMethodType': [u"Value must be one of ('centralizedProcurement',)."]
                },
                u"location": u"body",
                u"name": u"tender",
            }
        ],
    )

    with mock.patch('openprocurement.planning.api.models.PLAN_ADDRESS_KIND_REQUIRED_FROM',
                    get_now() + timedelta(seconds=1000)):
        with mock.patch('openprocurement.planning.api.validation.PLAN_ADDRESS_KIND_REQUIRED_FROM',
                        get_now() + timedelta(seconds=1000)):
            response = self.app.post_json('/plans', {"data": initial_data})
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status, "201 Created")

            initial_data = deepcopy(self.initial_data)
            response = self.app.post_json(request_path, {"data": initial_data})
            self.assertEqual(response.status, "201 Created")
            self.assertEqual(response.content_type, "application/json")

            plan = response.json["data"]
            acc_token = response.json["access"]["token"]

            response = self.app.patch_json(
                "/plans/{}?acc_token={}".format(plan["id"], acc_token),
                {
                    "data": {
                        "tender": {
                            "procurementMethod": "",
                            "procurementMethodType": ""
                        }
                    }
                },
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["tender"]["procurementMethodType"], u"")

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {
            "data": {
                "tender": {
                    "procurementMethod": "open",
                    "procurementMethodType": "aboveThresholdUA"
                }
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["tender"]["procurementMethodType"], u"aboveThresholdUA")


def create_plan_invalid_procuring_entity(self):
    request_path = "/plans"
    initial_data = deepcopy(self.initial_data)

    procuring_entity_address = initial_data["procuringEntity"].pop("address")
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)

    initial_data["procuringEntity"]["address"] = procuring_entity_address
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {u'address': [u'This field is required.']},
                u"location": u"body",
                u"name": u"procuringEntity",
            }
        ],
    )

    country_name = initial_data["procuringEntity"]["address"].pop("countryName")
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)

    initial_data["procuringEntity"]["address"]["countryName"] = country_name
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {u'address': {u'countryName': [u'This field is required.']}},
                u"location": u"body",
                u"name": u"procuringEntity",
            }
        ],
    )

    initial_data["procuringEntity"]["address"]["invalid_field"] = "invalid_field123"
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    del initial_data["procuringEntity"]["address"]["invalid_field"]

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {u'address': {u'invalid_field': u'Rogue field'}},
                u"location": u"body",
                u"name": u"procuringEntity",
            }
        ],
    )

    _kind = initial_data["procuringEntity"].pop("kind")
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)

    initial_data["procuringEntity"]["kind"] = _kind
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u'description': {u'kind': [u'This field is required.']},
                u"location": u"body",
                u"name": u"procuringEntity",
            }
        ],
    )

    _kind = initial_data["procuringEntity"].pop("kind")
    initial_data["procuringEntity"]["kind"] = "invalid_kind_type123"
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)

    initial_data["procuringEntity"]["kind"] = _kind

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {u'kind': [
                    u"Value must be one of ('authority', 'central', 'defense', 'general', 'other', 'social', 'special')."
                ]},
                u"location": u"body",
                u"name": u"procuringEntity",
            }
        ],
    )
    initial_data["procuringEntity"]["kind"] = u"general"
    initial_data["tender"]["procurementMethod"] = u"open"
    initial_data["tender"]["procurementMethodType"] = u"aboveThresholdUA.defense"

    response = self.app.post_json(request_path, {"data": initial_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    self.assertEqual(
        response.json["errors"], [
            {
                u'description': u'procuringEntity with general kind cannot publish this type of procedure.'
                                u' Procurement method types allowed for this kind: centralizedProcurement,'
                                u' reporting, negotiation, negotiation.quick, priceQuotation, belowThreshold, aboveThresholdUA,'
                                u' aboveThresholdEU, competitiveDialogueUA, competitiveDialogueEU, esco, '
                                u'closeFrameworkAgreementUA.', u'location': u'procuringEntity', u'name': u'kind'
            }
        ]
    )

    initial_data["procuringEntity"]["kind"] = u"defense"

    response = self.app.post_json(request_path, {"data": initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    initial_data["procuringEntity"]["kind"] = u"authority"
    initial_data["tender"]["procurementMethod"] = u"open"
    initial_data["tender"]["procurementMethodType"] = u"competitiveDialogueUA"

    response = self.app.post_json(request_path, {"data": initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    initial_data["procuringEntity"]["kind"] = u"other"
    initial_data["tender"]["procurementMethod"] = u""
    initial_data["tender"]["procurementMethodType"] = u"centralizedProcurement"

    response = self.app.post_json(request_path, {"data": initial_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    self.assertEqual(
        response.json["errors"], [
            {
                u'description': u'procuringEntity with other kind cannot publish this type of procedure. '
                                u'Procurement method types allowed for this kind: belowThreshold, reporting.',
                                u'location': u'procuringEntity', u'name': u'kind'
            }
        ]
    )

    # ignore address, kind validation for old plans
    with mock.patch('openprocurement.planning.api.models.PLAN_ADDRESS_KIND_REQUIRED_FROM',
                    get_now() + timedelta(seconds=1000)):
        with mock.patch('openprocurement.planning.api.validation.PLAN_ADDRESS_KIND_REQUIRED_FROM',
                        get_now() + timedelta(seconds=1000)):
            response = self.app.post_json('/plans', {"data": initial_data})
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status, "201 Created")

            address = initial_data["procuringEntity"].pop("address")
            response = self.app.post_json('/plans', {"data": initial_data})
            initial_data["procuringEntity"]["address"] = address

            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status, "201 Created")

            kind = initial_data["procuringEntity"].pop("kind")
            response = self.app.post_json('/plans', {"data": initial_data})
            initial_data["procuringEntity"]["kind"] = kind

            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status, "201 Created")

            address = initial_data["procuringEntity"].pop("address")
            kind = initial_data["procuringEntity"].pop("kind")
            response = self.app.post_json("/plans", {"data": initial_data})
            initial_data["procuringEntity"]["address"] = address
            initial_data["procuringEntity"]["kind"] = kind

            self.assertEqual(response.status, "201 Created")
            plan = response.json["data"]
            acc_token = response.json["access"]["token"]

            response = self.app.patch_json(
                "/plans/{}?acc_token={}".format(plan["id"], acc_token),
                {"data": {"procuringEntity": {"name": "new_name123"}}}
            )

            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(
                response.json['data']['procuringEntity'],
                {"identifier": {"scheme": u"UA-EDR", "id": u"111983", "legalName": u"ДП Державне Управління Справами"},
                 "name": u"new_name123"}
            )

            response = self.app.patch_json(
                "/plans/{}?acc_token={}".format(plan["id"], acc_token),
                {"data": {
                    "procuringEntity": {
                        "address": {"countryName": "Ірландія"},
                        "kind": "defense"
                    }
                }}
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(
                response.json['data']['procuringEntity'],
                {"identifier": {"scheme": u"UA-EDR", "id": u"111983", "legalName": u"ДП Державне Управління Справами"},
                 "name": u"new_name123",
                 "address": {"countryName": u"Ірландія"},
                 "kind": u"defense"
                 }
            )

    initial_data["procuringEntity"]["kind"] = u"other"
    initial_data["tender"]["procurementMethod"] = u"limited"
    initial_data["tender"]["procurementMethodType"] = u"reporting"

    response = self.app.post_json(request_path, {"data": initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.post_json(request_path, {"data": initial_data})
    self.assertEqual(response.status, "201 Created")


def create_plan_invalid_buyers(self):
    request_path = "/plans"
    initial_data = deepcopy(self.initial_data)

    buyers_address = initial_data["buyers"][0].pop("address")
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)

    initial_data["buyers"][0]["address"] = buyers_address
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u'address': [u'This field is required.']}],
                u"location": u"body",
                u"name": u"buyers",
            }
        ],
    )

    country_name = initial_data["buyers"][0]["address"].pop("countryName")
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)

    initial_data["buyers"][0]["address"]["countryName"] = country_name
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u'address': {u'countryName': [u'This field is required.']}}],
                u"location": u"body",
                u"name": u"buyers",
            }
        ],
    )

    initial_data["buyers"][0]["address"]["invalid_field"] = "invalid_field123"
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)
    del initial_data["buyers"][0]["address"]["invalid_field"]

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {u'address': {u'invalid_field': u'Rogue field'}},
                u"location": u"body",
                u"name": u"buyers",
            }
        ],
    )

    _kind = initial_data["buyers"][0].pop("kind")
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)

    initial_data["buyers"][0]["kind"] = _kind
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u'description': [{u'kind': [u'This field is required.']}],
                u"location": u"body",
                u"name": u"buyers",
            }
        ],
    )

    _kind = initial_data["buyers"][0].pop("kind")
    initial_data["buyers"][0]["kind"] = "invalid_kind_type123"
    response = self.app.post_json(request_path, {"data": initial_data}, status=422)

    initial_data["buyers"][0]["kind"] = _kind

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": [{u'kind': [
                    u"Value must be one of ('authority', 'central', 'defense', 'general', 'other', 'social', 'special')."
                ]}],
                u"location": u"body",
                u"name": u"buyers",
            }
        ],
    )

    with mock.patch('openprocurement.planning.api.models.PLAN_ADDRESS_KIND_REQUIRED_FROM',
                    get_now() + timedelta(seconds=1000)):
        response = self.app.post_json('/plans', {"data": initial_data})
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "201 Created")

        address = initial_data["buyers"][0].pop("address")
        response = self.app.post_json('/plans', {"data": initial_data})
        initial_data["buyers"][0]["address"] = address

        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "201 Created")

        kind = initial_data["buyers"][0].pop("kind")
        response = self.app.post_json('/plans', {"data": initial_data})
        initial_data["buyers"][0]["kind"] = kind

        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.status, "201 Created")

        address = initial_data["buyers"][0].pop("address")
        kind = initial_data["buyers"][0].pop("kind")
        response = self.app.post_json("/plans", {"data": initial_data})
        initial_data["buyers"][0]["address"] = address
        initial_data["buyers"][0]["kind"] = kind

        self.assertEqual(response.status, "201 Created")
        plan = response.json["data"]
        acc_token = response.json["access"]["token"]

        response = self.app.patch_json(
            "/plans/{}?acc_token={}".format(plan["id"], acc_token),
            {"data": {"buyers": [{"name": "new_name123"}]}}
        )

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json['data']['buyers'][0],
            {"identifier": {"scheme": u"UA-EDR", "id": u"111983", "legalName": u"ДП Державне Управління Справами"},
             "name": u"new_name123"}
        )

        response = self.app.patch_json(
            "/plans/{}?acc_token={}".format(plan["id"], acc_token),
            {"data": {
                "buyers": [{
                    "address": {"countryName": "Ірландія"},
                    "kind": "defense"
                }]
            }}
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json['data']['buyers'][0],
            {"identifier": {"scheme": u"UA-EDR", "id": u"111983", "legalName": u"ДП Державне Управління Справами"},
             "name": u"new_name123",
             "address": {"countryName": u"Ірландія"},
             "kind": u"defense"
             }
        )

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.post_json(request_path, {"data": initial_data})
    self.assertEqual(response.status, "201 Created")


def create_plan_generated(self):
    data = self.initial_data.copy()
    data.update({"id": "hash", "doc_id": "hash2", "planID": "hash3"})
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(
        set(plan),
        {
            u"id",
            u"dateModified",
            u"datePublished",
            u"planID",
            u"budget",
            u"tender",
            u"buyers",
            u"classification",
            u"additionalClassifications",
            u"items",
            u"procuringEntity",
            u"owner",
            u"status",
        },
    )
    self.assertNotEqual(data["id"], plan["id"])
    self.assertNotEqual(data["doc_id"], plan["id"])
    self.assertNotEqual(data["planID"], plan["planID"])


def create_plan(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/plans", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(
        set(plan) - set(self.initial_data), {u"id", u"dateModified", u"datePublished", u"planID", u"owner", u"status"}
    )
    self.assertIn(plan["id"], response.headers["Location"])

    response = self.app.get("/plans/{}".format(plan["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(set(response.json["data"]), set(plan))
    self.assertEqual(response.json["data"], plan)

    response = self.app.post_json("/plans?opt_jsonp=callback", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"', response.body)

    response = self.app.post_json("/plans?opt_pretty=1", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body)

    response = self.app.post_json("/plans", {"data": self.initial_data, "options": {"pretty": True}})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body)

    response = self.app.post_json("/plans", {"data": self.initial_data_with_year}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {u"year": [u"Can't use year field, use period field instead"]},
                u"location": u"body",
                u"name": u"budget",
            }
        ],
    )


def get_plan(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/plans", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    plan = response.json["data"]

    response = self.app.get("/plans/{}".format(plan["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], plan)

    response = self.app.get("/plans/{}?opt_jsonp=callback".format(plan["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"data": {"', response.body)

    response = self.app.get("/plans/{}?opt_pretty=1".format(plan["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "data": {\n        "', response.body)


def patch_plan(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/plans", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    plan = response.json["data"]
    acc_token = response.json["access"]["token"]
    dateModified = plan.pop("dateModified")

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": {"budget": {"id": u"12303111000-3"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_plan = response.json["data"]
    new_dateModified = new_plan.pop("dateModified")
    plan["budget"]["id"] = u"12303111000-3"
    self.assertEqual(plan, new_plan)
    self.assertNotEqual(dateModified, new_dateModified)

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": {"dateModified": new_dateModified}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_plan2 = response.json["data"]
    new_dateModified2 = new_plan2.pop("dateModified")
    self.assertEqual(new_plan, new_plan2)
    self.assertEqual(new_dateModified, new_dateModified2)

    revisions = self.db.get(plan["id"]).get("revisions")
    self.assertEqual(revisions[-1][u"changes"][0]["op"], u"replace")
    self.assertEqual(revisions[-1][u"changes"][0]["path"], u"/budget/id")

    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.get("/plans/{}/revisions".format(plan["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["revisions"], revisions)

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": {"items": [self.initial_data["items"][0]]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": {"items": [{}, self.initial_data["items"][0]]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    item0 = response.json["data"]["items"][0]
    item1 = response.json["data"]["items"][1]
    self.assertNotEqual(item0.pop("id"), item1.pop("id"))
    self.assertEqual(item0, item1)

    response = self.app.patch_json("/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": {"items": [{}]}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {
            "data": {
                "items": [
                    {
                        "classification": {
                            "scheme": "ДК021",
                            "id": "03117140-7",
                            "description": "Послуги з харчування у школах",
                        }
                    }
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {
            "data": {
                "items": [
                    {"additionalClassifications": [plan["items"][0]["additionalClassifications"][0] for i in range(3)]}
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"items": [{"additionalClassifications": plan["items"][0]["additionalClassifications"]}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"tender": {"tenderPeriod": {"startDate": new_dateModified2}}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_plan = response.json["data"]
    self.assertIn("startDate", new_plan["tender"]["tenderPeriod"])

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {
            "data": {
                "budget": {"period": {"endDate": datetime(year=datetime.now().year + 2, month=12, day=31).isoformat()}}
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {
                    u"period": {
                        u"endDate": [u"Period startDate and endDate must be within one year for belowThreshold."]
                    }
                },
                u"location": u"body",
                u"name": u"budget",
            }
        ],
    )

    # delete items
    response = self.app.patch_json("/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": {"items": []}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("items", response.json["data"])


def patch_plan_with_token(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/plans", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    plan = response.json["data"]
    acc_token = response.json["access"]["token"]
    date_modified = plan.pop("dateModified")

    self.app.patch_json("/plans/{}".format(plan["id"]), {"data": {"budget": {"id": u"12303111000-3"}}}, status=403)

    self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], uuid.uuid4().hex),
        {"data": {"budget": {"id": u"12303111000-3"}}},
        status=403,
    )

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": {"budget": {"id": u"12303111000-3"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_plan = response.json["data"]
    new_date_modified = new_plan.pop("dateModified")
    plan["budget"]["id"] = u"12303111000-3"
    self.assertEqual(plan, new_plan)
    self.assertNotEqual(date_modified, new_date_modified)


def patch_plan_item_quantity(self):
    response = self.app.post_json("/plans", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    acc_token = response.json["access"]["token"]

    quantities = [1, 1.999999, "9999.999999"]
    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(response.json["data"]["id"], acc_token),
        {"data": {"items": [{"quantity": q} for q in quantities]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    for n, i in enumerate(response.json["data"]["items"]):
        self.assertEqual(i["quantity"], float(quantities[n]))


def plan_not_found(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/plans/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"plan_id"}]
    )

    response = self.app.patch_json("/plans/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"plan_id"}]
    )


def esco_plan(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    data = deepcopy(self.initial_data)
    budget = data.pop("budget")
    data["tender"]["procurementMethodType"] = "esco"
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(
        set(plan) - set(self.initial_data), {u"id", u"dateModified", u"datePublished", u"planID", u"owner", u"status"}
    )
    self.assertNotIn("budget", plan)
    self.assertIn(plan["id"], response.headers["Location"])

    data["budget"] = budget
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(
        set(plan) - set(self.initial_data), {u"id", u"dateModified", u"datePublished", u"planID", u"owner", u"status"}
    )
    self.assertIn("budget", plan)
    self.assertIn(plan["id"], response.headers["Location"])


def cfaua_plan(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    data = deepcopy(self.initial_data)
    data["tender"]["procurementMethodType"] = "closeFrameworkAgreementUA"
    data["budget"]["period"]["endDate"] = datetime(year=datetime.now().year + 2, month=12, day=31).isoformat()
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(
        set(plan) - set(self.initial_data), {u"id", u"dateModified", u"datePublished", u"planID", u"owner", u"status"}
    )
    self.assertIn("budget", plan)
    period = plan["budget"]["period"]
    self.assertNotEqual(parse_date(period["startDate"]).year, parse_date(period["endDate"]).year)
    self.assertIn(plan["id"], response.headers["Location"])

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.patch_json(
        "/plans/{}".format(plan["id"]),
        {
            "data": {
                "budget": {"period": {"endDate": datetime(year=datetime.now().year + 5, month=12, day=31).isoformat()}}
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {
                    u"period": {
                        u"endDate": [
                            u"Period startDate and endDate must be within 5 budget years for closeFrameworkAgreementUA."
                        ]
                    }
                },
                u"location": u"body",
                u"name": u"budget",
            }
        ],
    )


def create_plan_budget_year(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/plans", {"data": self.initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {u"period": [u"Can't use period field, use year field instead"]},
                u"location": u"body",
                u"name": u"budget",
            }
        ],
    )

    response = self.app.post_json("/plans", {"data": self.initial_data_with_year})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(
        set(plan) - set(self.initial_data_with_year),
        {u"id", u"dateModified", u"datePublished", u"planID", u"owner", u"status"},
    )
    self.assertIn(plan["id"], response.headers["Location"])
    self.assertIn("year", plan["budget"])


def patch_plan_budget_year(self):
    response = self.app.post_json("/plans", {"data": self.initial_data_with_year})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    acc_token = response.json["access"]["token"]
    self.assertIn("year", plan["budget"])

    with mock.patch("openprocurement.planning.api.models.BUDGET_PERIOD_FROM", get_now() - timedelta(days=1)):
        response = self.app.patch_json(
            "/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": self.initial_data}
        )
        plan = response.json["data"]
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("year", plan["budget"])


def create_plan_without_buyers(self):
    response = self.app.post_json("/plans", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def fail_create_plan_without_buyers(self):
    with mock.patch("openprocurement.planning.api.models.PLAN_BUYERS_REQUIRED_FROM", get_now() - timedelta(seconds=1)):
        data = deepcopy(self.initial_data)
        del data["buyers"]
        response = self.app.post_json("/plans", {"data": data}, status=422)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json,
            {
                "status": "error",
                "errors": [{"location": "body", "name": "buyers", "description": ["This field is required."]}],
            },
        )

        data["buyers"] = []
        response = self.app.post_json("/plans", {"data": data}, status=422)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json,
            {
                "status": "error",
                "errors": [{"location": "body", "name": "buyers", "description": [u"Please provide at least 1 item."]}],
            },
        )

        data["buyers"] = [None]
        response = self.app.post_json("/plans", {"data": data}, status=422)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json,
            {
                u"status": u"error",
                u"errors": [{u"description": [[u"This field is required."]], u"location": u"body", u"name": u"buyers"}],
            },
        )


def create_plan_with_buyers(self):
    data = deepcopy(self.initial_data)
    data["buyers"] = [
        dict(
            name="",
            name_en="",
            identifier=dict(scheme=u"UA-EDR", id=u"111983", legalName=u"ДП Державне Управління Справами"),
            address=dict(countryName=u"Україна", postalCode=u"01220", locality= u"м. Київ"),
            kind=u"general"
        )
    ]
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(plan["buyers"], data["buyers"])

    # edit
    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], response.json["access"]["token"]),
        {"data": {"buyers": [dict(name="Hello", identifier=dict(id="666"))]}},
    )
    self.assertEqual(response.status, "200 OK")
    data["buyers"][0]["name"] = "Hello"
    data["buyers"][0]["identifier"]["id"] = "666"
    self.assertEqual(response.json["data"]["buyers"], data["buyers"])


def create_plan_with_two_buyers(self):
    data = deepcopy(self.initial_data)
    data["buyers"] = [
        dict(
            name="1",
            name_en="1",
            identifier=dict(scheme=u"UA-EDR", id=u"111983", legalName=u"ДП Державне Управління Справами"),
            address=dict(countryName=u"Україна", postalCode=u"01220", locality=u"м. Київ"),
            kind=u"general"
        ),
        dict(
            name="2",
            name_en="2",
            identifier=dict(scheme=u"UA-EDR", id=u"111983", legalName=u"ДП Державне Управління Справами"),
            address=dict(countryName=u"Україна", postalCode=u"01220", locality=u"м. Київ"),
            kind=u"other"
        ),
    ]
    response = self.app.post_json("/plans", {"data": data}, status=422)
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [{"location": "body", "name": "buyers", "description": ["Please provide no more than 1 item."]}],
        },
    )


def create_plan_with_breakdown(self):
    data = deepcopy(self.initial_data)
    breakdown_item = dict(id="f" * 32, title="state", value=dict(amount=1500, currency="UAH"))
    data["budget"]["breakdown"] = [breakdown_item]

    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(plan["budget"]["breakdown"], [breakdown_item])

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], response.json["access"]["token"]),
        {"data": {"budget": {"breakdown": [dict(description="Get to the choppa")]}}},
    )
    self.assertEqual(response.status, "200 OK")
    breakdown_item["description"] = "Get to the choppa"
    self.assertEqual(response.json["data"]["budget"]["breakdown"][0], breakdown_item)


def create_plan_with_breakdown_required(self):
    data = deepcopy(self.initial_data)
    data["tender"]["procurementMethodType"] = "aboveThresholdUA"
    del data["budget"]["breakdown"]

    response = self.app.post_json("/plans", {"data": data}, status=422)

    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"breakdown": [u"This field is required."]}, u"location": u"body", u"name": u"budget"}],
    )


@mock.patch("openprocurement.planning.api.models.BUDGET_BREAKDOWN_REQUIRED_FROM", get_now() + timedelta(days=1))
def create_plan_with_breakdown_not_required(self):
    data = deepcopy(self.initial_data)
    data["tender"]["procurementMethodType"] = "aboveThresholdUA"
    del data["budget"]["breakdown"]

    response = self.app.post_json("/plans", {"data": data})

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertNotIn("breakdown", plan["budget"])


def patch_plan_with_breakdown(self):
    data = deepcopy(self.initial_data)
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]

    breakdown_item = dict(
        id="f" * 32, title="state", description="Breakdown state description.", value=dict(amount=1500, currency="UAH")
    )

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], response.json["access"]["token"]),
        {"data": {"budget": {"breakdown": [breakdown_item]}}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["budget"]["breakdown"][0], breakdown_item)


def fail_create_plan_with_breakdown_invalid_title(self):
    data = deepcopy(self.initial_data)
    breakdown_item = dict(id="f" * 32, title="test", value=dict(amount=1500, currency="UAH"))
    data["budget"]["breakdown"] = [breakdown_item]

    response = self.app.post_json("/plans", {"data": data}, status=422)

    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {
                    u"breakdown": [
                        {
                            u"title": [
                                u"Value must be one of ['state', 'crimea', 'local', 'own', 'fund', 'loan', 'other']."
                            ]
                        }
                    ]
                },
                u"location": u"body",
                u"name": u"budget",
            }
        ],
    )


def create_plan_with_breakdown_other_title(self):
    data = deepcopy(self.initial_data)
    breakdown_item = dict(
        id="f" * 32,
        title="other",
        description="For a moment, nothing happened. Then, after a second or so, nothing continued to happen.",
        value=dict(amount=1500, currency="UAH"),
    )
    data["budget"]["breakdown"] = [breakdown_item]

    response = self.app.post_json("/plans", {"data": data})

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(plan["budget"]["breakdown"][0], breakdown_item)


def fail_create_plan_with_breakdown_other_title(self):
    data = deepcopy(self.initial_data)
    breakdown_item = dict(id="f" * 32, title="other", value=dict(amount=1500, currency="UAH"))
    data["budget"]["breakdown"] = [breakdown_item]

    response = self.app.post_json("/plans", {"data": data}, status=422)

    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": {u"breakdown": [{u"description": [u"This field is required."]}]},
                u"location": u"body",
                u"name": u"budget",
            }
        ],
    )


def fail_create_plan_with_diff_breakdown_currencies(self):
    data = deepcopy(self.initial_data)
    del data["budget"]["currency"]
    breakdown_item_1 = dict(id="f" * 32, title="state", value=dict(amount=1500, currency="UAH"))
    breakdown_item_2 = dict(id="0" * 32, title="state", value=dict(amount=1500, currency="USD"))
    data["budget"]["breakdown"] = [breakdown_item_1, breakdown_item_2]

    response = self.app.post_json("/plans", {"data": data}, status=422)

    expected_errors = [
        {
            u"description": {
                u"breakdown": [u"Currency should be identical for all budget breakdown values and budget"]
            },
            u"location": u"body",
            u"name": u"budget",
        }
    ]

    self.assertEqual(response.json["errors"], expected_errors)

    breakdown_item_2["value"]["currency"] = "UAH"

    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan_id = response.json["data"]["id"]
    plan_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, plan_token), {"data": {"budget": {"currency": "USD"}}}, status=422
    )

    self.assertEqual(response.json["errors"], expected_errors)

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, plan_token), {"data": {"budget": {"currency": "UAH"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.assertEqual(response.json["data"]["budget"]["currency"], "UAH")


def fail_create_plan_with_amounts_sum_greater(self):
    data = deepcopy(self.initial_data)
    data["budget"]["breakdown"] = [
        dict(id="0" * 31 + str(i), title="state", value=dict(amount=1500, currency="UAH")) for i in xrange(10)
    ]

    response = self.app.post_json("/plans", {"data": data}, status=422)

    expected_errors = [
        {
            u"description": {
                u"breakdown": [u"Sum of the breakdown values amounts can't be greater than budget amount"]
            },
            u"location": u"body",
            u"name": u"budget",
        }
    ]

    self.assertEqual(response.json["errors"], expected_errors)

    data["tender"]["procurementMethodType"] = "esco"

    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def plan_token_invalid(self):
    response = self.app.post_json("/plans", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.plan_id = response.json["data"]["id"]

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(self.plan_id, "fake token"), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Forbidden", u"location": u"url", u"name": u"permission"}]
    )

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(self.plan_id, "токен з кирилицею"), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Forbidden", u"location": u"url", u"name": u"permission"}]
    )
