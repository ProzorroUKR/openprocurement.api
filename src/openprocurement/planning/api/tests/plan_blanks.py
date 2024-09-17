import uuid
from copy import deepcopy
from datetime import datetime, timedelta
from unittest import mock

from freezegun import freeze_time

from openprocurement.api.constants import ROUTE_PREFIX, TZ
from openprocurement.api.context import set_now
from openprocurement.api.database import MongodbResourceConflict
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.planning.api.constants import PROCEDURES

# PlanTest
from openprocurement.tender.core.tests.utils import change_auth


def concurrent_plan_update(self):
    """
    Checking that only valid _id and _rev can update the document
    otherwise the whole request should be repeated to pass all validations again in case anything's been changed
    """
    set_now()

    u = deepcopy(self.initial_data)
    u["dateModified"] = get_now().isoformat()
    u["planID"] = "UA-P-X"
    u["_id"] = uuid.uuid4().hex

    self.mongodb.plans.save(u, insert=True)
    first_rev = u["_rev"]

    u["status"] = "scheduled"

    u["_rev"] = None
    with self.assertRaises(MongodbResourceConflict):
        self.mongodb.plans.save(u)

    u["_rev"] = first_rev
    self.mongodb.plans.save(u)
    second_rev = u["_rev"]

    u["_rev"] = first_rev
    with self.assertRaises(MongodbResourceConflict):
        self.mongodb.plans.save(u)

    u["_rev"] = second_rev
    self.mongodb.plans.save(u)
    self.assertGreater(u["_rev"], second_rev)

    from_db = self.mongodb.plans.get(u["_id"])
    self.assertEqual(from_db["_rev"], u["_rev"])

    self.mongodb.plans.flush()


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
    self.assertNotIn('{\n    "', response.body.decode())
    self.assertNotIn("callback({", response.body.decode())
    self.assertEqual(response.json["next_page"]["offset"], "")
    self.assertNotIn("prev_page", response.json)

    response = self.app.get("/plans?opt_jsonp=callback")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertNotIn('{\n    "', response.body.decode())
    self.assertIn("callback({", response.body.decode())

    response = self.app.get("/plans?opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body.decode())
    self.assertNotIn("callback({", response.body.decode())

    response = self.app.get("/plans?opt_jsonp=callback&opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('{\n    "', response.body.decode())
    self.assertIn("callback({", response.body.decode())

    response = self.app.get("/plans?offset=latest&descending=1&limit=10", status=404)
    self.assertEqual(
        response.json,
        {
            "status": "error",
            "errors": [{"location": "querystring", "name": "offset", "description": "Invalid offset provided: latest"}],
        },
    )

    response = self.app.get("/plans?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])

    response = self.app.get(
        f"/plans?offset={datetime.fromisoformat('2015-01-01T00:00:00+02:00').timestamp()}&descending=1&limit=10"
    )
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
        response = self.app.post_json("/plans", {"data": self.initial_data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        plans.append(response.json["data"])

    ids = ",".join([i["id"] for i in plans])

    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in plans})
    self.assertEqual({i["dateModified"] for i in response.json["data"]}, {i["dateModified"] for i in plans})
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in plans]))

    response = self.app.get("/plans?limit=1")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("prev_page", response.json)
    self.assertEqual(len(response.json["data"]), 1)
    offset = response.json["next_page"]["offset"]

    response = self.app.get(f"/plans?offset={offset}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)

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
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    modified = datetime.fromisoformat(response.json["data"][0]["dateModified"])
    self.assertIsNotNone(modified.tzinfo)
    self.assertNotIn("opt_fields=budget", response.json["next_page"]["uri"])

    response = self.app.get("/plans", params=[("opt_fields", "planID")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "planID"})
    self.assertIn("opt_fields=planID", response.json["next_page"]["uri"])

    response = self.app.get("/plans?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in plans})
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]],
        sorted([i["dateModified"] for i in plans], reverse=True),
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

    response = self.app.get("/plans?mode=test")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/plans?mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def listing_moves_from_dts(self):
    """
    test ensures that feed is built by timestamp
    (or by any other time representation that always sorts dates right)
    See example why sorting isoformat strings wouldn't work here
    2021-10-31T03:58:00+03:00
    2021-10-31T03:59:00+03:00
    2021-10-31T03:00:00+02:00 -> this time is actually bigger than previous, but the string repr isn't
    2021-10-31T03:01:00+02:00
    :param self:
    :return:
    """
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    plans = []
    dt = TZ.localize(datetime(2021, 10, 31, 2, 30))
    for i in range(4):
        dt += timedelta(seconds=60 * 30)
        with freeze_time(dt):
            response = self.app.post_json("/plans", {"data": self.initial_data})
            self.assertEqual(response.status, "201 Created")
            plans.append(response.json["data"])

    self.assertEqual(
        [
            "2021-10-31T03:00:00+03:00",
            "2021-10-31T03:30:00+03:00",
            "2021-10-31T03:00:00+02:00",
            "2021-10-31T03:30:00+02:00",
        ],
        [p["dateModified"] for p in plans],
    )

    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)
    result = response.json["data"]
    self.assertEqual(
        [
            "2021-10-31T03:00:00+03:00",
            "2021-10-31T03:30:00+03:00",
            "2021-10-31T03:00:00+02:00",
            "2021-10-31T03:30:00+02:00",
        ],
        [p["dateModified"] for p in result],
    )

    response = self.app.get("/plans?limit=1")
    self.assertEqual(len(response.json["data"]), 1)
    self.assertEqual(response.json["data"][0]["dateModified"], "2021-10-31T03:00:00+03:00")

    offset = response.json["next_page"]["offset"]
    response = self.app.get(f"/plans?limit=1&offset={offset}")
    self.assertEqual(len(response.json["data"]), 1)
    self.assertEqual(response.json["data"][0]["dateModified"], "2021-10-31T03:30:00+03:00")

    offset = response.json["next_page"]["offset"]
    response = self.app.get(f"/plans?limit=1&offset={offset}")
    self.assertEqual(len(response.json["data"]), 1)
    self.assertEqual(response.json["data"][0]["dateModified"], "2021-10-31T03:00:00+02:00")

    offset = response.json["next_page"]["offset"]
    response = self.app.get(f"/plans?limit=1&offset={offset}")
    self.assertEqual(len(response.json["data"]), 1)
    self.assertEqual(response.json["data"][0]["dateModified"], "2021-10-31T03:30:00+02:00")


def create_plan_invalid(self):
    response = self.app.post("/plans", "data", status=415)
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

    response = self.app.post("/plans", "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Expecting value: line 1 column 1 (char 0)", "location": "body", "name": "data"}],
    )

    response = self.app.post_json("/plans", "data", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json("/plans", {"not_data": {}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json("/plans", {"data": []}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Data not available", "location": "body", "name": "data"}]
    )

    response = self.app.post_json("/plans", {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json("/plans", {"data": {"budget": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Please use a mapping for this field or Budget instance instead of str."],
                "location": "body",
                "name": "budget",
            }
        ],
    )

    response = self.app.post_json(
        "/plans",
        {"data": {"tender": {"procurementMethod": "invalid_value"}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "procuringEntity"},
        response.json["errors"],
    )
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "classification"},
        response.json["errors"],
    )

    initial_data = deepcopy(self.initial_data)
    initial_data["tender"] = {
        "procurementMethod": "open",
        "procurementMethodType": "reporting",
        "tenderPeriod": initial_data["tender"]["tenderPeriod"],
    }
    response = self.app.post_json("/plans", {"data": initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {
            "description": {"procurementMethodType": ["Value must be one of {!r}.".format(PROCEDURES["open"])]},
            "location": "body",
            "name": "tender",
        },
        response.json["errors"],
    )

    initial_data = deepcopy(self.initial_data)
    initial_data["tender"] = {
        "procurementMethod": "limited",
        "procurementMethodType": "belowThreshold",
        "tenderPeriod": initial_data["tender"]["tenderPeriod"],
    }
    response = self.app.post_json("/plans", {"data": initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {
            "description": {"procurementMethodType": ["Value must be one of {!r}.".format(PROCEDURES["limited"])]},
            "location": "body",
            "name": "tender",
        },
        response.json["errors"],
    )

    response = self.app.post_json(
        "/plans",
        {"data": {"tender": {"tenderPeriod": {"startDate": "invalid_value"}}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"tenderPeriod": {"startDate": ["Could not parse invalid_value. Should be ISO8601."]}},
                "location": "body",
                "name": "tender",
            }
        ],
    )

    response = self.app.post_json(
        "/plans",
        {"data": {"tender": {"tenderPeriod": {"startDate": "9999-12-31T23:59:59.999999"}}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"tenderPeriod": {"startDate": ["date value out of range"]}},
                "location": "body",
                "name": "tender",
            }
        ],
    )

    initial_data = deepcopy(self.initial_data)
    additionalClassifications = [i.pop("additionalClassifications") for i in initial_data["items"]]
    cpv_code = initial_data["classification"]["id"]
    cpv_codes = [i["classification"]["id"] for i in initial_data["items"]]
    initial_data["classification"]["id"] = "99999999-9"
    for index, cpv_code in enumerate(cpv_codes):
        initial_data["items"][index]["classification"]["id"] = "99999999-9"
    for index, additionalClassification in enumerate(additionalClassifications):
        initial_data["items"][index]["additionalClassifications"] = additionalClassification
    initial_data["classification"]["id"] = cpv_code

    for index, cpv_code in enumerate(cpv_codes):
        initial_data["items"][index]["classification"]["id"] = cpv_code

    additionalClassifications = [i["additionalClassifications"][0]["scheme"] for i in initial_data["items"]]
    for index, _ in enumerate(additionalClassifications):
        initial_data["items"][index]["additionalClassifications"][0]["scheme"] = "Не ДКПП"
    cpv_code = initial_data["classification"]["id"]
    cpv_codes = [i["classification"]["id"] for i in initial_data["items"]]
    initial_data["classification"]["id"] = "99999999-9"
    for index, cpv_code in enumerate(cpv_codes):
        initial_data["items"][index]["classification"]["id"] = "99999999-9"
    response = self.app.post_json("/plans", {"data": initial_data}, status=422)

    for index, data in enumerate(additionalClassifications):
        initial_data["items"][index]["additionalClassifications"][0]["scheme"] = data
    initial_data["classification"]["id"] = cpv_code
    for index, cpv_code in enumerate(cpv_codes):
        initial_data["items"][index]["classification"]["id"] = cpv_code
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    {
                        "additionalClassifications": [
                            "One of additional classifications should be one of [ДК003, ДК015, ДК018, specialNorms]."
                        ]
                    }
                    for _ in additionalClassifications
                ],
                "location": "body",
                "name": "items",
            }
        ],
    )

    initial_data = deepcopy(self.initial_data)
    del initial_data["procuringEntity"]["name"]
    response = self.app.post_json("/plans", {"data": initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": {"name": ["This field is required."]}, "location": "body", "name": "procuringEntity"}],
    )

    initial_data = deepcopy(self.initial_data)
    del initial_data["budget"]
    initial_data["tender"]["procurementMethodType"] = "belowThreshold"
    response = self.app.post_json("/plans", {"data": initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "budget"}],
    )

    initial_data = deepcopy(self.initial_data)
    initial_data["items"] = [
        deepcopy(initial_data["items"][0]),
        deepcopy(initial_data["items"][0]),
    ]
    initial_data["classification"]["id"] = "33600000-6"
    initial_data["items"][0]["classification"]["id"] = "33600000-6"
    initial_data["items"][1]["classification"]["id"] = "31519200-9"
    response = self.app.post_json("/plans", {"data": initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["CPV group of items should be identical"],
                "location": "body",
                "name": "items",
            }
        ],
    )

    initial_data = deepcopy(self.initial_data)
    initial_data["items"] = [
        deepcopy(initial_data["items"][0]),
        deepcopy(initial_data["items"][0]),
    ]
    initial_data["classification"]["id"] = "33600000-6"
    initial_data["items"][0]["classification"]["id"] = "31519200-9"
    initial_data["items"][1]["classification"]["id"] = "31519200-9"
    response = self.app.post_json("/plans", {"data": initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["CPV group of items should be identical to root cpv"],
                "location": "body",
                "name": "items",
            }
        ],
    )

    initial_data = deepcopy(self.initial_data)
    initial_data["items"] = [
        deepcopy(initial_data["items"][0]),
        deepcopy(initial_data["items"][0]),
    ]
    initial_data["classification"]["id"] = "31519200-9"
    initial_data["items"][0]["classification"]["id"] = "03222321-9"
    initial_data["items"][1]["classification"]["id"] = "31519200-9"
    response = self.app.post_json("/plans", {"data": initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["CPV class of items should be identical"],
                "location": "body",
                "name": "items",
            }
        ],
    )

    initial_data = deepcopy(self.initial_data)
    initial_data["items"] = [
        deepcopy(initial_data["items"][0]),
        deepcopy(initial_data["items"][0]),
    ]
    initial_data["classification"]["id"] = "31519200-9"
    initial_data["items"][0]["classification"]["id"] = "03222321-9"
    initial_data["items"][1]["classification"]["id"] = "03222321-9"
    response = self.app.post_json("/plans", {"data": initial_data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["CPV class of items should be identical to root cpv"],
                "location": "body",
                "name": "items",
            }
        ],
    )


def create_plan_invalid_procurement_method_type(self):
    request_path = "/plans"
    initial_data = deepcopy(self.initial_data)
    response = self.app.post_json(request_path, {"data": initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    plan = response.json["data"]
    acc_token = response.json["access"]["token"]

    tender = deepcopy(initial_data["tender"])
    tender["procurementMethod"] = ""
    tender["procurementMethodType"] = ""

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": {"tender": tender}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {'procurementMethodType': ["Value must be one of ('centralizedProcurement',)."]},
                "location": "body",
                "name": "tender",
            }
        ],
    )

    data = deepcopy(initial_data)
    data["tender"]["procurementMethod"] = ""
    data["tender"]["procurementMethodType"] = ""
    response = self.app.post_json(request_path, {"data": data}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {'procurementMethodType': ["Value must be one of ('centralizedProcurement',)."]},
                "location": "body",
                "name": "tender",
            }
        ],
    )

    with mock.patch(
        'openprocurement.planning.api.procedure.models.tender.PLAN_ADDRESS_KIND_REQUIRED_FROM',
        get_now() + timedelta(seconds=1000),
    ):
        with mock.patch(
            'openprocurement.planning.api.procedure.state.plan.PLAN_ADDRESS_KIND_REQUIRED_FROM',
            get_now() + timedelta(seconds=1000),
        ):
            response = self.app.post_json('/plans', {"data": initial_data})
            self.assertEqual(response.content_type, 'application/json')
            self.assertEqual(response.status, "201 Created")

            initial_data = deepcopy(self.initial_data)
            response = self.app.post_json(request_path, {"data": initial_data})
            self.assertEqual(response.status, "201 Created")
            self.assertEqual(response.content_type, "application/json")

            plan = response.json["data"]
            acc_token = response.json["access"]["token"]

            tender = deepcopy(initial_data["tender"])
            tender["procurementMethod"] = ""
            tender["procurementMethodType"] = ""

            response = self.app.patch_json(
                "/plans/{}?acc_token={}".format(plan["id"], acc_token),
                {"data": {"tender": tender}},
            )
            self.assertEqual(response.status, "200 OK")
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["data"]["tender"]["procurementMethodType"], "")

    tender = deepcopy(initial_data["tender"])
    tender["procurementMethod"] = "open"
    tender["procurementMethodType"] = "aboveThresholdUA"

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"tender": tender}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["tender"]["procurementMethodType"], "aboveThresholdUA")


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
                "description": {'address': ['This field is required.']},
                "location": "body",
                "name": "procuringEntity",
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
                "description": {'address': {'countryName': ['This field is required.']}},
                "location": "body",
                "name": "procuringEntity",
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
                "description": {'address': {'invalid_field': 'Rogue field'}},
                "location": "body",
                "name": "procuringEntity",
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
                'description': {'kind': ['This field is required.']},
                "location": "body",
                "name": "procuringEntity",
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
                "description": {
                    'kind': [
                        "Value must be one of ('authority', 'central', 'defense', 'general', 'other', 'social', 'special')."
                    ]
                },
                "location": "body",
                "name": "procuringEntity",
            }
        ],
    )
    initial_data["procuringEntity"]["kind"] = "general"
    initial_data["tender"]["procurementMethod"] = "open"
    initial_data["tender"]["procurementMethodType"] = "aboveThresholdUA.defense"

    with mock.patch(
        "openprocurement.planning.api.procedure.state.plan.RELEASE_SIMPLE_DEFENSE_FROM", get_now() + timedelta(days=1)
    ):
        response = self.app.post_json(request_path, {"data": initial_data}, status=403)

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": (
                    "procuringEntity with general kind cannot publish this type of procedure. Procurement "
                    "method types allowed for this kind: centralizedProcurement, belowThreshold, aboveThreshold, "
                    "aboveThresholdUA, aboveThresholdEU, competitiveDialogueUA, competitiveDialogueEU, esco, "
                    "closeFrameworkAgreementUA, priceQuotation, reporting, negotiation, negotiation.quick."
                ),
                'location': 'body',
                'name': 'kind',
            }
        ],
    )

    initial_data["procuringEntity"]["kind"] = "defense"
    with mock.patch(
        "openprocurement.planning.api.procedure.state.plan.RELEASE_SIMPLE_DEFENSE_FROM", get_now() + timedelta(days=1)
    ):
        response = self.app.post_json(request_path, {"data": initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    initial_data["procuringEntity"]["kind"] = "authority"
    initial_data["tender"]["procurementMethod"] = "open"
    initial_data["tender"]["procurementMethodType"] = "competitiveDialogueUA"

    response = self.app.post_json(request_path, {"data": initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    initial_data["procuringEntity"]["kind"] = "other"
    initial_data["tender"]["procurementMethod"] = ""
    initial_data["tender"]["procurementMethodType"] = "centralizedProcurement"

    response = self.app.post_json(request_path, {"data": initial_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': 'procuringEntity with other kind cannot publish this type of procedure. '
                'Procurement method types allowed for this kind: '
                'belowThreshold, reporting, priceQuotation.',
                'location': 'body',
                'name': 'kind',
            }
        ],
    )

    # ignore address, kind validation for old plans
    with mock.patch(
        'openprocurement.planning.api.procedure.models.tender.PLAN_ADDRESS_KIND_REQUIRED_FROM',
        get_now() + timedelta(seconds=1000),
    ):
        with mock.patch(
            'openprocurement.planning.api.procedure.models.organization.PLAN_ADDRESS_KIND_REQUIRED_FROM',
            get_now() + timedelta(seconds=1000),
        ):
            with mock.patch(
                'openprocurement.planning.api.procedure.state.plan.PLAN_ADDRESS_KIND_REQUIRED_FROM',
                get_now() + timedelta(seconds=1000),
            ):
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

                name = initial_data["procuringEntity"].pop("name")
                address = initial_data["procuringEntity"].pop("address")
                kind = initial_data["procuringEntity"].pop("kind")
                initial_data["procuringEntity"]["name"] = "new_name123"
                response = self.app.patch_json(
                    "/plans/{}?acc_token={}".format(plan["id"], acc_token),
                    {"data": {"procuringEntity": initial_data["procuringEntity"]}},
                )
                initial_data["procuringEntity"]["name"] = name
                initial_data["procuringEntity"]["address"] = address
                initial_data["procuringEntity"]["kind"] = kind

                self.assertEqual(response.status, "200 OK")
                self.assertEqual(response.content_type, "application/json")
                procuring_entity = response.json['data']['procuringEntity']
                procuring_entity.pop("id")
                self.assertEqual(
                    procuring_entity,
                    {
                        "identifier": {
                            "scheme": "UA-EDR",
                            "id": "111983",
                            "legalName": "ДП Державне Управління Справами",
                        },
                        "name": "new_name123",
                    },
                )

                name = initial_data["procuringEntity"].pop("name")
                address = initial_data["procuringEntity"].pop("address")
                kind = initial_data["procuringEntity"].pop("kind")
                initial_data["procuringEntity"]["address"] = {"countryName": "Ірландія"}
                initial_data["procuringEntity"]["kind"] = "defense"
                initial_data["procuringEntity"]["name"] = "new_name123"
                response = self.app.patch_json(
                    "/plans/{}?acc_token={}".format(plan["id"], acc_token),
                    {"data": {"procuringEntity": initial_data["procuringEntity"]}},
                )
                initial_data["procuringEntity"]["name"] = name
                initial_data["procuringEntity"]["address"] = address
                initial_data["procuringEntity"]["kind"] = kind
                self.assertEqual(response.status, "200 OK")
                self.assertEqual(response.content_type, "application/json")
                procuring_entity = response.json['data']['procuringEntity']
                procuring_entity.pop("id")
                self.assertEqual(
                    procuring_entity,
                    {
                        "identifier": {
                            "scheme": "UA-EDR",
                            "id": "111983",
                            "legalName": "ДП Державне Управління Справами",
                        },
                        "name": "new_name123",
                        "address": {"countryName": "Ірландія"},
                        "kind": "defense",
                    },
                )

    initial_data["procuringEntity"]["kind"] = "other"
    initial_data["tender"]["procurementMethod"] = "limited"
    initial_data["tender"]["procurementMethodType"] = "reporting"

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
                "description": [{'address': ['This field is required.']}],
                "location": "body",
                "name": "buyers",
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
                "description": [{'address': {'countryName': ['This field is required.']}}],
                "location": "body",
                "name": "buyers",
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
                "description": {'address': {'invalid_field': 'Rogue field'}},
                "location": "body",
                "name": "buyers",
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
                'description': [{'kind': ['This field is required.']}],
                "location": "body",
                "name": "buyers",
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
                "description": [
                    {
                        'kind': [
                            "Value must be one of ('authority', 'central', 'defense', 'general', 'other', 'social', 'special')."
                        ]
                    }
                ],
                "location": "body",
                "name": "buyers",
            }
        ],
    )

    with mock.patch(
        'openprocurement.planning.api.procedure.models.organization.PLAN_ADDRESS_KIND_REQUIRED_FROM',
        get_now() + timedelta(seconds=1000),
    ):
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

        name = initial_data["buyers"][0].pop("name")
        address = initial_data["buyers"][0].pop("address")
        kind = initial_data["buyers"][0].pop("kind")
        initial_data["buyers"][0]["name"] = "new_name123"
        response = self.app.patch_json(
            "/plans/{}?acc_token={}".format(plan["id"], acc_token),
            {"data": {"buyers": initial_data["buyers"]}},
        )
        initial_data["buyers"][0]["name"] = name
        initial_data["buyers"][0]["address"] = address
        initial_data["buyers"][0]["kind"] = kind

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        buyers = response.json['data']['buyers'][0]
        buyers.pop("id")
        self.assertEqual(
            buyers,
            {
                "identifier": {
                    "scheme": "UA-EDR",
                    "id": "111983",
                    "legalName": "ДП Державне Управління Справами",
                },
                "name": "new_name123",
                "contactPoint": {"name": "Державне управління справами", "telephone": "+0440000000"},
            },
        )

        name = initial_data["buyers"][0].pop("name")
        address = initial_data["buyers"][0].pop("address")
        kind = initial_data["buyers"][0].pop("kind")
        initial_data["buyers"][0]["address"] = {"countryName": "Ірландія"}
        initial_data["buyers"][0]["kind"] = "defense"
        initial_data["buyers"][0]["name"] = "new_name123"
        response = self.app.patch_json(
            "/plans/{}?acc_token={}".format(plan["id"], acc_token),
            {"data": {"buyers": initial_data["buyers"]}},
        )
        initial_data["buyers"][0]["name"] = name
        initial_data["buyers"][0]["address"] = address
        initial_data["buyers"][0]["kind"] = kind
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        buyers = response.json['data']['buyers'][0]
        buyers.pop("id")
        self.assertEqual(
            buyers,
            {
                "identifier": {
                    "scheme": "UA-EDR",
                    "id": "111983",
                    "legalName": "ДП Державне Управління Справами",
                },
                "name": "new_name123",
                "address": {"countryName": "Ірландія"},
                "contactPoint": {"name": "Державне управління справами", "telephone": "+0440000000"},
                "kind": "defense",
            },
        )

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.post_json(request_path, {"data": initial_data})
    self.assertEqual(response.status, "201 Created")


def create_plan_generated(self):
    data = self.initial_data.copy()
    data.update({"id": "hash", "doc_id": "hash2", "planID": "hash3"})
    response = self.app.post_json("/plans", {"data": data}, status=422)
    self.assertEqual(len(response.json["errors"]), 2)
    self.assertIn(
        {'description': 'Rogue field', 'location': 'body', 'name': 'doc_id'},
        response.json["errors"],
    )
    self.assertIn(
        {'description': 'Rogue field', 'location': 'body', 'name': 'planID'},
        response.json["errors"],
    )

    data = self.initial_data.copy()
    # FIXME: shouldn't be ignored
    data.update({"id": "hash"})
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(
        set(plan),
        {
            "id",
            "dateCreated",
            "dateModified",
            "datePublished",
            "planID",
            "budget",
            "tender",
            "buyers",
            "classification",
            "additionalClassifications",
            "items",
            "procuringEntity",
            "owner",
            "status",
            "project",
        },
    )
    self.assertEqual(
        datetime.fromisoformat(plan["dateCreated"]),
        datetime.fromisoformat(plan["dateModified"]),
    )

    self.assertNotEqual(data["id"], plan["id"])

    response = self.app.get(f"/plans/{plan['id']}")
    g_plan = response.json["data"]
    self.assertEqual(g_plan["dateCreated"], plan["dateCreated"])
    self.assertEqual(g_plan["dateModified"], plan["dateModified"])


def create_plan(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/plans", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(
        set(plan) - set(self.initial_data),
        {"id", "dateCreated", "dateModified", "datePublished", "planID", "owner", "status"},
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
    self.assertIn('callback({"', response.body.decode())

    response = self.app.post_json("/plans?opt_pretty=1", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body.decode())

    response = self.app.post_json("/plans", {"data": self.initial_data, "options": {"pretty": True}})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body.decode())

    response = self.app.post_json("/plans", {"data": self.initial_data_with_year}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"year": ["Can't use year field, use period field instead"]},
                "location": "body",
                "name": "budget",
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
    self.assertIn('callback({"data": {"', response.body.decode())

    response = self.app.get("/plans/{}?opt_pretty=1".format(plan["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "data": {\n        "', response.body.decode())


def patch_plan(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    data = self.initial_data
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    plan = response.json["data"]
    acc_token = response.json["access"]["token"]
    dateModified = plan.pop("dateModified")

    budget = deepcopy(plan["budget"])
    budget["id"] = "12303111000-3"

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"budget": budget}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_plan = response.json["data"]
    new_dateModified = new_plan.pop("dateModified")
    plan["budget"]["id"] = "12303111000-3"
    self.assertEqual(plan, new_plan)
    self.assertNotEqual(dateModified, new_dateModified)

    revisions = self.mongodb.plans.get(plan["id"]).get("revisions")
    self.assertEqual(revisions[-1]["changes"][0]["op"], "replace")
    self.assertEqual(revisions[-1]["changes"][0]["path"], "/budget/id")

    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.get("/plans/{}/revisions".format(plan["id"]))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["revisions"], revisions)

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": {"items": [data["items"][0]]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"items": [data["items"][0], data["items"][0]]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    item0 = response.json["data"]["items"][0]
    item1 = response.json["data"]["items"][1]
    self.assertNotEqual(item0.pop("id"), item1.pop("id"))
    self.assertEqual(item0, item1)

    response = self.app.patch_json("/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": {"items": [item0]}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)

    items = deepcopy(data["items"])
    items[0]["classification"] = {
        "scheme": "ДК021",
        "id": "03117140-7",
        "description": "Послуги з харчування у школах",
    }

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    items[0]["additionalClassifications"] = [plan["items"][0]["additionalClassifications"][0] for i in range(3)]

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    items[0]["additionalClassifications"] = plan["items"][0]["additionalClassifications"]

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    tender = deepcopy(data["tender"])
    tender["tenderPeriod"] = {"startDate": new_dateModified}

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"tender": tender}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_plan = response.json["data"]
    self.assertIn("startDate", new_plan["tender"]["tenderPeriod"])

    budget = deepcopy(data["budget"])
    budget["period"] = {
        "startDate": new_plan["tender"]["tenderPeriod"]["startDate"],
        "endDate": datetime(
            year=datetime.now().year + 2,
            month=12,
            day=31,
        ).isoformat(),
    }

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"budget": budget}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Period startDate and endDate must be within one year for belowThreshold."],
                "location": "body",
                "name": "budget",
            }
        ],
    )

    # delete items
    response = self.app.patch_json("/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": {"items": []}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("items", response.json["data"])


@mock.patch(
    "openprocurement.planning.api.procedure.state.plan.RELEASE_SIMPLE_DEFENSE_FROM", get_now() - timedelta(days=1)
)
def patch_plan_to_simpledefense(self):
    data = self.initial_data
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    plan = response.json["data"]
    acc_token = response.json["access"]["token"]

    tender = deepcopy(data["tender"])
    tender["procurementMethodType"] = "aboveThresholdUA.defense"

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"tender": tender}},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Plan tender.procurementMethodType can not be changed from 'belowThreshold' to 'aboveThresholdUA.defense'",
                'location': 'body',
                'name': 'tender',
            }
        ],
    )

    tender["procurementMethodType"] = "simple.defense"

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"tender": tender}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["tender"]["procurementMethodType"], "simple.defense")


@mock.patch(
    "openprocurement.planning.api.procedure.state.plan.RELEASE_SIMPLE_DEFENSE_FROM", get_now() + timedelta(days=1)
)
def patch_plan_to_openuadefense(self):
    data = self.initial_data
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    plan = response.json["data"]
    acc_token = response.json["access"]["token"]

    tender = deepcopy(data["tender"])
    tender["procurementMethodType"] = "simple.defense"

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"tender": tender}},
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Plan tender.procurementMethodType can not be changed from 'belowThreshold' to 'simple.defense'",
                'location': 'body',
                'name': 'tender',
            }
        ],
    )

    tender["procurementMethodType"] = "aboveThresholdUA.defense"

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], acc_token),
        {"data": {"tender": tender}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["tender"]["procurementMethodType"], "aboveThresholdUA.defense")


def patch_plan_with_token(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    data = self.initial_data

    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    plan = response.json["data"]
    acc_token = response.json["access"]["token"]
    date_modified = plan.pop("dateModified")

    budget = deepcopy(plan["budget"])
    budget["id"] = "12303111000-3"
    self.app.patch_json("/plans/{}".format(plan["id"]), {"data": {"budget": budget}}, status=403)

    self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], uuid.uuid4().hex),
        {"data": {"budget": budget}},
        status=403,
    )

    response = self.app.patch_json("/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": {"budget": budget}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_plan = response.json["data"]
    new_date_modified = new_plan.pop("dateModified")
    plan["budget"]["id"] = "12303111000-3"
    self.assertEqual(plan, new_plan)
    self.assertNotEqual(date_modified, new_date_modified)


def patch_plan_item_quantity(self):
    data = self.initial_data
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    acc_token = response.json["access"]["token"]

    quantities = [1, 1.999999, "9999.999999"]
    items = deepcopy(data["items"])
    for index, quantity in enumerate(quantities):
        items[index]["quantity"] = quantity

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(response.json["data"]["id"], acc_token),
        {"data": {"items": items}},
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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "plan_id"}])

    response = self.app.patch_json("/plans/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "plan_id"}])


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
        set(plan) - set(self.initial_data),
        {"id", "dateCreated", "dateModified", "datePublished", "planID", "owner", "status"},
    )
    self.assertNotIn("budget", plan)
    self.assertIn(plan["id"], response.headers["Location"])

    data["budget"] = budget
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(
        set(plan) - set(self.initial_data),
        {"id", "dateCreated", "dateModified", "datePublished", "planID", "owner", "status"},
    )
    self.assertIn("budget", plan)
    self.assertIn(plan["id"], response.headers["Location"])


def cfaua_plan(self):
    response = self.app.get("/plans")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    data = deepcopy(self.initial_data)
    data["tender"]["procurementMethodType"] = "closeFrameworkAgreementUA"
    data["budget"]["period"]["endDate"] = datetime(
        year=datetime.now().year + 2,
        month=12,
        day=31,
    ).isoformat()
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(
        set(plan) - set(self.initial_data),
        {"id", "dateCreated", "dateModified", "datePublished", "planID", "owner", "status"},
    )
    self.assertIn("budget", plan)
    period = plan["budget"]["period"]
    self.assertNotEqual(
        parse_date(period["startDate"]).year,
        parse_date(period["endDate"]).year,
    )
    self.assertIn(plan["id"], response.headers["Location"])

    budget = deepcopy(data["budget"])
    budget["period"]["endDate"] = datetime(
        year=datetime.now().year + 5,
        month=12,
        day=31,
    ).isoformat()

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], response.json["access"]["token"]),
        {"data": {"budget": budget}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    "Period startDate and endDate must be within 5 budget years for closeFrameworkAgreementUA."
                ],
                "location": "body",
                "name": "budget",
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
                "description": {"period": ["Can't use period field, use year field instead"]},
                "location": "body",
                "name": "budget",
            }
        ],
    )

    response = self.app.post_json("/plans", {"data": self.initial_data_with_year})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(
        set(plan) - set(self.initial_data_with_year),
        {"id", "dateCreated", "dateModified", "datePublished", "planID", "owner", "status"},
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

    with mock.patch(
        "openprocurement.planning.api.procedure.models.budget.BUDGET_PERIOD_FROM", get_now() - timedelta(days=1)
    ):
        data = deepcopy(self.initial_data)
        data["budget"]["year"] = None
        response = self.app.patch_json("/plans/{}?acc_token={}".format(plan["id"], acc_token), {"data": data})
        plan = response.json["data"]
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("year", plan["budget"])


def create_plan_without_buyers(self):
    response = self.app.post_json("/plans", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def fail_create_plan_without_buyers(self):
    with mock.patch(
        "openprocurement.planning.api.procedure.models.plan.PLAN_BUYERS_REQUIRED_FROM", get_now() - timedelta(seconds=1)
    ):
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
                "errors": [{"location": "body", "name": "buyers", "description": ["Please provide at least 1 item."]}],
            },
        )

        data["buyers"] = [None]
        response = self.app.post_json("/plans", {"data": data}, status=422)
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json,
            {
                "status": "error",
                "errors": [{"description": [["This field is required."]], "location": "body", "name": "buyers"}],
            },
        )


def create_plan_with_buyers(self):
    data = deepcopy(self.initial_data)
    data["buyers"] = [
        {
            "id": uuid.uuid4().hex,
            "name": "",
            "name_en": "",
            "identifier": {"scheme": "UA-EDR", "id": "111983", "legalName": "ДП Державне Управління Справами"},
            "address": {"countryName": "Україна", "postalCode": "01220", "locality": "м. Київ"},
            "kind": "general",
        }
    ]
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(plan["buyers"], data["buyers"])

    # edit
    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], response.json["access"]["token"]),
        {
            "data": {
                "buyers": [
                    {
                        "id": plan["buyers"][0]["id"],
                        "name": "Hello",
                        "name_en": "",
                        "identifier": {"scheme": "UA-EDR", "id": "666", "legalName": "ДП Державне Управління Справами"},
                        "address": {"countryName": "Україна", "postalCode": "01220", "locality": "м. Київ"},
                        "kind": "general",
                    }
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    data["buyers"][0]["name"] = "Hello"
    data["buyers"][0]["identifier"]["id"] = "666"
    self.assertEqual(response.json["data"]["buyers"], data["buyers"])


def create_plan_with_two_buyers(self):
    data = deepcopy(self.initial_data)
    data["buyers"] = [
        {
            "name": "1",
            "name_en": "1",
            "identifier": {"scheme": "UA-EDR", "id": "111983", "legalName": "ДП Державне Управління Справами"},
            "address": {"countryName": "Україна", "postalCode": "01220", "locality": "м. Київ"},
            "kind": "general",
        },
        {
            "name": "2",
            "name_en": "2",
            "identifier": {"scheme": "UA-EDR", "id": "111983", "legalName": "ДП Державне Управління Справами"},
            "address": {"countryName": "Україна", "postalCode": "01220", "locality": "м. Київ"},
            "kind": "other",
        },
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
    breakdown_item = {"id": "f" * 32, "title": "state", "value": {"amount": 1500, "currency": "UAH"}}
    data["budget"]["breakdown"] = [breakdown_item]

    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(plan["budget"]["breakdown"], [breakdown_item])

    budget = deepcopy(data["budget"])
    budget["breakdown"][0]["description"] = "Get to the choppa"

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], response.json["access"]["token"]),
        {"data": {"budget": budget}},
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
        [{"description": ["Breakdown field is required."], "location": "body", "name": "budget"}],
    )


@mock.patch(
    "openprocurement.planning.api.procedure.models.plan.BUDGET_BREAKDOWN_REQUIRED_FROM", get_now() + timedelta(days=1)
)
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

    breakdown_item = {
        "id": "f" * 32,
        "title": "state",
        "description": "Breakdown state description.",
        "value": {"amount": 1500, "currency": "UAH"},
    }
    budget = deepcopy(data["budget"])
    budget["breakdown"] = [breakdown_item]

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan["id"], response.json["access"]["token"]),
        {"data": {"budget": budget}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["budget"]["breakdown"][0], breakdown_item)


def fail_create_plan_with_breakdown_invalid_title(self):
    data = deepcopy(self.initial_data)
    breakdown_item = {"id": "f" * 32, "title": "test", "value": {"amount": 1500, "currency": "UAH"}}
    data["budget"]["breakdown"] = [breakdown_item]

    response = self.app.post_json("/plans", {"data": data}, status=422)

    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {
                    "breakdown": [
                        {
                            "title": [
                                "Value must be one of ['state', 'crimea', 'local', 'own', 'fund', 'loan', 'other']."
                            ]
                        }
                    ]
                },
                "location": "body",
                "name": "budget",
            }
        ],
    )


def create_plan_with_breakdown_other_title(self):
    data = deepcopy(self.initial_data)
    breakdown_item = {
        "id": "f" * 32,
        "title": "other",
        "description": "For a moment, nothing happened. Then, after a second or so, nothing continued to happen.",
        "value": {"amount": 1500, "currency": "UAH"},
    }
    data["budget"]["breakdown"] = [breakdown_item]

    response = self.app.post_json("/plans", {"data": data})

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan = response.json["data"]
    self.assertEqual(plan["budget"]["breakdown"][0], breakdown_item)


def fail_create_plan_with_breakdown_other_title(self):
    data = deepcopy(self.initial_data)
    breakdown_item = {"id": "f" * 32, "title": "other", "value": {"amount": 1500, "currency": "UAH"}}
    data["budget"]["breakdown"] = [breakdown_item]

    response = self.app.post_json("/plans", {"data": data}, status=422)

    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"breakdown": [{"description": ["This field is required."]}]},
                "location": "body",
                "name": "budget",
            }
        ],
    )


def fail_create_plan_with_diff_breakdown_currencies(self):
    data = deepcopy(self.initial_data)
    del data["budget"]["currency"]
    breakdown_item_1 = {"id": "f" * 32, "title": "state", "value": {"amount": 1500, "currency": "UAH"}}
    breakdown_item_2 = {"id": "0" * 32, "title": "state", "value": {"amount": 1500, "currency": "USD"}}
    data["budget"]["breakdown"] = [breakdown_item_1, breakdown_item_2]

    response = self.app.post_json("/plans", {"data": data}, status=422)

    expected_errors = [
        {
            "description": {"breakdown": ["Currency should be identical for all budget breakdown values and budget"]},
            "location": "body",
            "name": "budget",
        }
    ]

    self.assertEqual(response.json["errors"], expected_errors)

    breakdown_item_2["value"]["currency"] = "UAH"

    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    plan_id = response.json["data"]["id"]
    plan_token = response.json["access"]["token"]

    budget = deepcopy(data["budget"])
    budget["currency"] = "USD"
    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(plan_id, plan_token), {"data": {"budget": budget}}, status=422
    )

    self.assertEqual(response.json["errors"], expected_errors)

    budget["currency"] = "UAH"
    response = self.app.patch_json("/plans/{}?acc_token={}".format(plan_id, plan_token), {"data": {"budget": budget}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    self.assertEqual(response.json["data"]["budget"]["currency"], "UAH")


def fail_create_plan_with_amounts_sum_greater(self):
    data = deepcopy(self.initial_data)
    data["budget"]["breakdown"] = [
        {"id": "0" * 31 + str(i), "title": "state", "value": {"amount": 1500, "currency": "UAH"}} for i in range(10)
    ]

    response = self.app.post_json("/plans", {"data": data}, status=422)

    expected_errors = [
        {
            "description": ["Sum of the breakdown values amounts can't be greater than budget amount"],
            "location": "body",
            "name": "budget",
        }
    ]

    self.assertEqual(response.json["errors"], expected_errors)

    data["tender"]["procurementMethodType"] = "esco"

    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def create_plan_with_delivery_address(self):
    data = deepcopy(self.initial_data)
    delivery_address = {
        "countryName": "Україна",
        "postalCode": "01221",
        "region": "Київська область",
        "locality": "Київська область",
        "streetAddress": "вул. Банкова, 11, корпус 2",
    }
    item = data["items"][0]
    item["deliveryAddress"] = delivery_address
    data["items"] = [item]

    response = self.app.post_json("/plans", {"data": data})

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["items"][0]["deliveryAddress"], delivery_address)


def create_plan_with_delivery_address_required_fields(self):
    data = deepcopy(self.initial_data)
    delivery_address = {}
    item = data["items"][0]
    item["deliveryAddress"] = delivery_address
    data["items"] = [item]

    response = self.app.post_json("/plans", {"data": data}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "items",
                "description": [{"deliveryAddress": {"countryName": ["This field is required."]}}],
            }
        ],
    )


def create_plan_with_delivery_address_validations(self):
    data = deepcopy(self.initial_data)
    item = data["items"][0]
    item["deliveryAddress"] = {}
    data["items"] = [item]

    data["items"][0]["deliveryAddress"]["countryName"] = "Ukraine"

    response = self.app.post_json("/plans", {"data": data}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "items",
                "description": [
                    {"deliveryAddress": {"countryName": ["field address:countryName not exist in countries catalog"]}}
                ],
            }
        ],
    )

    data["items"][0]["deliveryAddress"]["countryName"] = "Україна"

    response = self.app.post_json("/plans", {"data": data})

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    data["items"][0]["deliveryAddress"]["countryName"] = "Україна"
    data["items"][0]["deliveryAddress"]["region"] = "State of New York"

    response = self.app.post_json("/plans", {"data": data}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "items",
                "description": [
                    {"deliveryAddress": {"region": ["field address:region not exist in ua_regions catalog"]}}
                ],
            }
        ],
    )

    data["items"][0]["deliveryAddress"]["countryName"] = "Сполучені Штати Америки"
    data["items"][0]["deliveryAddress"]["region"] = "State of New York"

    response = self.app.post_json("/plans", {"data": data})

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def create_plan_with_profile(self):
    data = deepcopy(self.initial_data)
    item = data["items"][0]
    item["profile"] = "test"
    data["items"] = [item]

    response = self.app.post_json("/plans", {"data": data}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [{'profile': ["The profile value doesn't match id pattern"]}],
                'location': 'body',
                'name': 'items',
            }
        ],
    )

    profile = "908221-15510000-980777-40996564"
    item["profile"] = profile

    response = self.app.post_json("/plans", {"data": data})

    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["items"][0]["profile"], profile)


def plan_token_invalid(self):
    response = self.app.post_json("/plans", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.plan_id = response.json["data"]["id"]

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(self.plan_id, "fake token"), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}])

    response = self.app.patch_json(
        "/plans/{}?acc_token={}".format(self.plan_id, "токен з кирилицею"), {"data": {}}, status=422
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


def plan_rationale(self):
    fake_date = "2022-02-24T05:00:00+02:00"
    data = dict(self.initial_data)
    data["status"] = "draft"
    response = self.app.post_json("/plans", {"data": data})
    self.assertEqual(response.status, "201 Created")
    plan_data = response.json["data"]
    plan_id = plan_data["id"]
    plan_token = response.json["access"]["token"]

    # add rationale
    dt = datetime.fromisoformat(response.json["data"]["dateModified"])
    dt += timedelta(seconds=60 * 30)
    with freeze_time(dt):
        response = self.app.patch_json(
            f"/plans/{plan_id}?acc_token={plan_token}",
            {"data": {"rationale": {"description": "test 1", "date": fake_date}}},  # try to change it
        )
    self.assertEqual(response.status, "200 OK")
    rationale = response.json["data"]["rationale"]
    self.assertEqual("test 1", rationale["description"])
    rationale_date_added = rationale["date"]
    self.assertNotEqual(fake_date, rationale["date"])
    self.assertGreater(rationale_date_added, plan_data["dateModified"])

    # update plan
    dt = datetime.fromisoformat(response.json["data"]["dateModified"])
    dt += timedelta(seconds=60 * 60 * 30)
    with freeze_time(dt):
        response = self.app.patch_json(
            f"/plans/{plan_id}?acc_token={plan_token}",
            {
                "data": {
                    "status": "scheduled",
                    "rationale": {"description": "test 1", "date": fake_date},  # the same  # try to change it
                }
            },
        )
    self.assertEqual(response.status, "200 OK")
    result = response.json["data"]
    self.assertEqual("scheduled", result["status"])
    self.assertEqual("test 1", result["rationale"]["description"])
    self.assertEqual(rationale_date_added, result["rationale"]["date"])

    # update rationale
    dt = datetime.fromisoformat(response.json["data"]["dateModified"])
    dt += timedelta(seconds=60 * 60 * 30)
    with freeze_time(dt):
        response = self.app.patch_json(
            f"/plans/{plan_id}?acc_token={plan_token}",
            {"data": {"rationale": {"description": "test 2", "date": fake_date}}},  # new  # try to change it
        )
    self.assertEqual(response.status, "200 OK")
    result = response.json["data"]
    self.assertEqual("test 2", result["rationale"]["description"])
    rationale_date_changed = result["rationale"]["date"]
    self.assertGreater(rationale_date_changed, rationale_date_added)

    # get history
    response = self.app.get(f"/history/plans/{plan_id}?opt_fields=rationale")
    changes = response.json["data"]["changes"]
    self.assertEqual(2, len(changes))

    self.assertEqual(rationale_date_added, changes[0]["date"])
    self.assertEqual(rationale_date_added, changes[0]["data"]["rationale"]["date"])
    self.assertEqual("test 1", changes[0]["data"]["rationale"]["description"])

    self.assertEqual(rationale_date_changed, changes[1]["date"])
    self.assertEqual(rationale_date_changed, changes[1]["data"]["rationale"]["date"])
    self.assertEqual("test 2", changes[1]["data"]["rationale"]["description"])
