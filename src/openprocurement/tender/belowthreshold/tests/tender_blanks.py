import mock
from uuid import uuid4
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.utils import get_now, parse_date
from openprocurement.api.constants import (
    TZ,
    ROUTE_PREFIX,
    CPV_BLOCK_FROM,
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM,
    RELEASE_2020_04_19,
    CPV_ITEMS_CLASS_FROM,
    GUARANTEE_ALLOWED_TENDER_TYPES,
)
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
    test_tender_below_cancellation,
    test_tender_below_claim,
    test_tender_below_draft_claim,
)
from openprocurement.tender.belowthreshold.tests.utils import (
    set_tender_lots,
    set_bid_lotvalues,
)

from openprocurement.tender.core.tests.base import (
    test_exclusion_criteria,
    test_language_criteria,
    test_contract_guarantee_criteria,
    test_tender_guarantee_criteria,
)
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.core.utils import calculate_tender_business_date
from openprocurement.tender.core.tests.criteria_utils import add_criteria


def listing(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []

    for i in range(3):
        offset = get_now().timestamp()
        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.set_initial_status(response.json)
        tenders.append(response.json["data"])

    ids = ",".join([i["id"] for i in tenders])

    while True:
        response = self.app.get("/tenders")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in tenders]))
    self.assertEqual(set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in tenders]))
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders]))

    response = self.app.get("/tenders?offset={}".format(offset))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?limit=2")
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

    response = self.app.get("/tenders", params=[("opt_fields", "status")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "status"})
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders", params=[("opt_fields", "status,enquiryPeriod")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "status"})
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in tenders]))
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders], reverse=True)
    )

    response = self.app.get("/tenders?descending=1&limit=2")
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

    test_tender_data2 = self.initial_data.copy()
    test_tender_data2["mode"] = "test"
    response = self.app.post_json("/tenders", {"data": test_tender_data2, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender_id = response.json["data"]["id"]
    tender_token = response.json["access"]["token"]
    add_criteria(self, tender_id, tender_token)
    self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={tender_token}",
        {"data": {"status": self.primary_tender_status}}
    )

    response = self.app.get("/tenders?mode=test")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)

    for i in range(6):
        offset = get_now().timestamp()
        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.set_initial_status(response.json)
        tenders.append(response.json["data"])

    response = self.app.get("/tenders?descending=1&limit=9")
    self.assertEqual(response.status, "200 OK")

    ids = [i["id"] for i in response.json["data"]]
    latest_ids = ids[:3]
    middle_ids = ids[3:6]
    earliest_ids = ids[6:]

    response = self.app.get("/tenders?descending=1&limit=3")
    self.assertEqual(response.status, "200 OK")
    self.assertListEqual([i["id"] for i in response.json["data"]], latest_ids)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertListEqual([i["id"] for i in response.json["data"]], middle_ids)

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertListEqual([i["id"] for i in response.json["data"]], earliest_ids)

    response = self.app.get(response.json["prev_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertListEqual([i["id"] for i in response.json["data"]], list(reversed(middle_ids)))

    response = self.app.get(response.json["next_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertListEqual([i["id"] for i in response.json["data"]], list(reversed(latest_ids)))

    response = self.app.get(response.json["prev_page"]["path"].replace(ROUTE_PREFIX, ""))
    self.assertEqual(response.status, "200 OK")
    self.assertListEqual([i["id"] for i in response.json["data"]], middle_ids)


def listing_changes(self):
    response = self.app.get("/tenders?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []

    for i in range(3):
        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.set_initial_status(response.json)
        tenders.append(response.json["data"])

    ids = ",".join([i["id"] for i in tenders])

    response = self.app.get("/tenders?feed=changes")
    self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))

    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in tenders]))
    self.assertEqual(set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in tenders]))
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders]))

    response = self.app.get("/tenders?feed=changes&limit=2")
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

    response = self.app.get("/tenders?feed=changes", params=[("opt_fields", "status")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders?feed=changes", params=[("opt_fields", "status,enquiryPeriod")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in tenders]))
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders], reverse=True)
    )

    response = self.app.get("/tenders?feed=changes&descending=1&limit=2")
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

    test_tender_data2 = self.initial_data.copy()
    test_tender_data2["mode"] = "test"
    response = self.app.post_json("/tenders", {"data": test_tender_data2, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    response = self.set_initial_status(response.json)

    while True:
        response = self.app.get("/tenders?feed=changes&mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?feed=changes&mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def listing_draft(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []
    data = self.initial_data.copy()
    data.update({"status": "draft"})

    for i in range(3):
        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        response = self.set_initial_status(response.json)
        tenders.append(response.json["data"])
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    ids = ",".join([i["id"] for i in tenders])

    while True:
        response = self.app.get("/tenders")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in tenders]))
    self.assertEqual(set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in tenders]))
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders]))


@mock.patch(
    "openprocurement.tender.belowthreshold.models.RELEASE_2020_04_19",
    get_now() + timedelta(days=1)
)
def create_tender_invalid(self):
    request_path = "/tenders"
    # TODO: spent a hour trying find out why this does not work after refactoring
    # response = self.app.post(request_path, "data", status=415)
    # self.assertEqual(response.status, "415 Unsupported Media Type")
    # self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["status"], "error")
    # self.assertEqual(
    #     response.json["errors"],
    #     [
    #         {
    #             "description": "Content-Type header should be one of ['application/json']",
    #             "location": "header",
    #             "name": "Content-Type",
    #         }
    #     ],
    # )

    response = self.app.post(request_path, "data", content_type="application/json", status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": 'Expecting value: line 1 column 1 (char 0)', "location": "body", "name": "data"}],
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

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"value": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Please use a mapping for this field or Value instance instead of str."],
                "location": "body",
                "name": "value",
            }
        ],
    )

    response = self.app.post_json(request_path, {"data": {"procurementMethod": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    self.assertIn(
        {
            "description": ["Value must be one of ['open', 'selective', 'limited']."],
            "location": "body",
            "name": "procurementMethod",
        },
        response.json["errors"],
    )

    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "tenderPeriod"},
        response.json["errors"],
    )

    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "items"}, response.json["errors"]
    )

    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "enquiryPeriod"},
        response.json["errors"],
    )

    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "value"}, response.json["errors"]
    )

    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "items"}, response.json["errors"]
    )

    response = self.app.post_json(request_path, {"data": {"enquiryPeriod": {"endDate": "invalid_value"}}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"endDate": ["Could not parse invalid_value. Should be ISO8601."]},
                "location": "body",
                "name": "enquiryPeriod",
            }
        ],
    )

    response = self.app.post_json(
        request_path, {"data": {"enquiryPeriod": {"endDate": "9999-12-31T23:59:59.999999"}}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": {"endDate": ["date value out of range"]}, "location": "body", "name": "enquiryPeriod"}],
    )

    data = self.initial_data["tenderPeriod"]
    self.initial_data["tenderPeriod"] = {"startDate": "2014-10-31T00:00:00", "endDate": "2014-10-01T00:00:00"}
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["tenderPeriod"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"startDate": ["period should begin before its end"]},
                "location": "body",
                "name": "tenderPeriod",
            }
        ],
    )

    data = self.initial_data["tenderPeriod"]
    self.initial_data["tenderPeriod"] = {"startDate": "2014-10-31T00:00:00", "endDate": "2015-10-01T00:00:00"}
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["tenderPeriod"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["period should begin after enquiryPeriod"],
                "location": "body",
                "name": "tenderPeriod",
            }
        ],
    )

    now = get_now()
    self.initial_data["awardPeriod"] = {"startDate": now.isoformat(), "endDate": now.isoformat()}
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["period should begin after tenderPeriod"], "location": "body", "name": "awardPeriod"}],
    )

    self.initial_data["auctionPeriod"] = {
        "startDate": (now + timedelta(days=14)).isoformat(),
        "endDate": (now + timedelta(days=14)).isoformat(),
    }
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["period should begin after auctionPeriod"], "location": "body", "name": "awardPeriod"}],
    )
    del self.initial_data["awardPeriod"]
    del self.initial_data["auctionPeriod"]

    data = self.initial_data["minimalStep"]
    del self.initial_data["minimalStep"]
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["minimalStep"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "minimalStep"},
        response.json["errors"],
    )

    data = self.initial_data["minimalStep"]
    self.initial_data["minimalStep"] = {"amount": "1000.0"}
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["minimalStep"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["value should be less than value of tender"],
                "location": "body",
                "name": "minimalStep",
            }
        ],
    )

    data = self.initial_data["minimalStep"]
    self.initial_data["minimalStep"] = {"amount": "100.0", "valueAddedTaxIncluded": False}
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["minimalStep"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    "valueAddedTaxIncluded should be identical to valueAddedTaxIncluded of value of tender"
                ],
                "location": "body",
                "name": "minimalStep",
            }
        ],
    )

    data = self.initial_data["minimalStep"]
    self.initial_data["minimalStep"] = {"amount": "100.0", "currency": "USD"}
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["minimalStep"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["currency should be identical to currency of value of tender"],
                "location": "body",
                "name": "minimalStep",
            }
        ],
    )

    data = self.initial_data["items"][0].pop("additionalClassifications")
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = self.initial_data["items"][0]["classification"]["id"]
        self.initial_data["items"][0]["classification"]["id"] = "99999999-9"

    status = 422 if get_now() < NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM else 201
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=status)
    self.initial_data["items"][0]["additionalClassifications"] = data
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.initial_data["items"][0]["classification"]["id"] = cpv_code
    if status == 201:
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.status, "201 Created")
    else:
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": [{"additionalClassifications": ["This field is required."]}],
                    "location": "body",
                    "name": "items",
                }
            ],
        )

    data = self.initial_data["items"][0]["additionalClassifications"][0]["scheme"]
    self.initial_data["items"][0]["additionalClassifications"][0]["scheme"] = "Не ДКПП"
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = self.initial_data["items"][0]["classification"]["id"]
        self.initial_data["items"][0]["classification"]["id"] = "99999999-9"
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["items"][0]["additionalClassifications"][0]["scheme"] = data
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.initial_data["items"][0]["classification"]["id"] = cpv_code
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": [
                        {
                            "additionalClassifications": [
                                "One of additional classifications should be "
                                "one of [ДК003, ДК015, ДК018, specialNorms]."
                            ]
                        }
                    ],
                    "location": "body",
                    "name": "items",
                }
            ],
        )
    else:
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": [
                        {
                            "additionalClassifications": [
                                "One of additional classifications should be "
                                "one of [ДКПП, NONE, ДК003, ДК015, ДК018]."
                            ]
                        }
                    ],
                    "location": "body",
                    "name": "items",
                }
            ],
        )

    data = self.initial_data["procuringEntity"]["contactPoint"]["telephone"]
    del self.initial_data["procuringEntity"]["contactPoint"]["telephone"]
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["procuringEntity"]["contactPoint"]["telephone"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"contactPoint": {"email": ["telephone or email should be present"]}},
                "location": "body",
                "name": "procuringEntity",
            }
        ],
    )
    correct_phone = self.initial_data["procuringEntity"]["contactPoint"]["telephone"]
    self.initial_data["procuringEntity"]["contactPoint"]["telephone"] = "++223"
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["procuringEntity"]["contactPoint"]["telephone"] = correct_phone
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u'description': {u'contactPoint': {u'telephone': [u'wrong telephone format (could be missed +)']}},
                u'location': u'body',
                u'name': u'procuringEntity'
            }
        ]
    )

    data = self.initial_data["items"][0].copy()
    classification = data["classification"].copy()
    classification["id"] = "19212310-1"
    data["classification"] = classification
    self.initial_data["items"] = [self.initial_data["items"][0], data]
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["items"] = self.initial_data["items"][:1]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.assertEqual(
            response.json["errors"],
            [{"description": ["CPV class of items should be identical"], "location": "body", "name": "items"}],
        )
    else:
        self.assertEqual(
            response.json["errors"],
            [{"description": ["CPV group of items be identical"], "location": "body", "name": "items"}],
        )

    cpv = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "160173000-1"
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["items"][0]["classification"]["id"] = cpv
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("classification", response.json["errors"][0]["description"][0])
    self.assertIn("id", response.json["errors"][0]["description"][0]["classification"])
    self.assertIn("Value must be one of", response.json["errors"][0]["description"][0]["classification"]["id"][0])

    cpv = self.initial_data["items"][0]["classification"]["id"]
    if get_now() < CPV_BLOCK_FROM:
        self.initial_data["items"][0]["classification"]["scheme"] = "CPV"
    self.initial_data["items"][0]["classification"]["id"] = "00000000-0"
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    if get_now() < CPV_BLOCK_FROM:
        self.initial_data["items"][0]["classification"]["scheme"] = "CPV"
    self.initial_data["items"][0]["classification"]["id"] = cpv
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("classification", response.json["errors"][0]["description"][0])
    self.assertIn("id", response.json["errors"][0]["description"][0]["classification"])
    self.assertIn("Value must be one of", response.json["errors"][0]["description"][0]["classification"]["id"][0])

    procuringEntity = self.initial_data["procuringEntity"]
    data = self.initial_data["procuringEntity"].copy()
    data["kind"] = "bla"
    self.initial_data["procuringEntity"] = data
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["procuringEntity"] = procuringEntity
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "procuringEntity",
                "description": {
                    "kind": [
                        "Value must be one of ('authority', 'central', 'defense', 'general', 'other', 'social', 'special')."
                    ]
                }
            }
        ],
    )


@mock.patch(
    "openprocurement.tender.belowthreshold.procedure.models.tender.RELEASE_2020_04_19",
    get_now() - timedelta(days=1)
)
def validate_enquiryTender(self):
    self.initial_data.pop("procurementMethodDetails", None)

    request_path = "/tenders"
    data = self.initial_data["enquiryPeriod"]
    now = get_now()

    valid_start_date = now + timedelta(days=7)
    valid_end_date = calculate_tender_business_date(
        valid_start_date, timedelta(days=3), self.initial_data, True).isoformat()
    invalid_end_date = calculate_tender_business_date(
        valid_start_date, timedelta(days=2), self.initial_data, True).isoformat()
    tender_valid_end_date = calculate_tender_business_date(
        valid_start_date, timedelta(days=8), self.initial_data, True).isoformat()

    valid_start_date = valid_start_date.isoformat()

    self.initial_data["enquiryPeriod"] = {
        "startDate": valid_start_date,
        "endDate": invalid_end_date,
    }

    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["enquiryPeriod"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["the enquiryPeriod cannot end earlier than 3 business days after the start"],
                "location": "body",
                "name": "enquiryPeriod",
            }
        ],
    )

    self.initial_data["enquiryPeriod"] = {
        "startDate": valid_start_date,
        "endDate": valid_end_date,
    }
    self.initial_data["tenderPeriod"] = {
        "endDate": tender_valid_end_date,
    }

    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    period = tender["enquiryPeriod"]
    period["endDate"] = invalid_end_date
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"enquiryPeriod": period}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["the enquiryPeriod cannot end earlier than 3 business days after the start"],
                "location": "body",
                "name": "enquiryPeriod",
            }
        ],
    )

    period["endDate"] = valid_end_date
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"enquiryPeriod": period}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(tender["enquiryPeriod"]["endDate"], valid_end_date)


@mock.patch(
    "openprocurement.tender.belowthreshold.procedure.models.tender.RELEASE_2020_04_19",
    get_now() - timedelta(days=1)
)
def validate_tenderPeriod(self):
    now = get_now()

    enquiry_start_date = now + timedelta(days=7)
    enquiry_end_date = calculate_tender_business_date(
       enquiry_start_date, timedelta(days=3), self.initial_data, True)

    valid_start_date = enquiry_end_date
    valid_end_date = calculate_tender_business_date(
        valid_start_date, timedelta(days=2), self.initial_data, True).isoformat()
    invalid_end_date = calculate_tender_business_date(
        valid_start_date, timedelta(days=1), self.initial_data, True).isoformat()

    enquiry_start_date = enquiry_start_date.isoformat()
    enquiry_end_date = enquiry_end_date.isoformat()
    valid_start_date = valid_start_date.isoformat()

    request_path = "/tenders"
    data = self.initial_data["tenderPeriod"]
    self.initial_data["tenderPeriod"] = {
        "startDate": valid_start_date,
        "endDate": invalid_end_date,
    }
    self.initial_data["enquiryPeriod"] = {
        "startDate": enquiry_start_date,
        "endDate": enquiry_end_date,
    }

    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["tenderPeriod"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["tenderPeriod must be at least 2 full business days long"],
                "location": "body",
                "name": "tenderPeriod",
            }
        ],
    )

    self.initial_data["tenderPeriod"] = {
        "startDate": valid_start_date,
        "endDate": valid_end_date
    }
    self.initial_data["enquiryPeriod"] = {
        "startDate": enquiry_start_date,
        "endDate": enquiry_end_date,
    }
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    period = tender["tenderPeriod"]
    period["endDate"] = invalid_end_date
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"tenderPeriod": period}},
        status=422
    )

    self.initial_data["tenderPeriod"] = data
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["tenderPeriod must be at least 2 full business days long"],
                "location": "body",
                "name": "tenderPeriod",
            }
        ],
    )

    period["endDate"] = valid_end_date
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"tenderPeriod": period}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    tender = response.json["data"]
    self.assertEqual(tender["tenderPeriod"]["endDate"], valid_end_date)


def create_tender_with_inn(self):
    from openprocurement.tender.core.procedure.models.item import CPV_336_INN_FROM
    request_path = "/tenders"

    addit_classif = [
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
    ]
    data = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "33600000-6"
    orig_addit_classif = self.initial_data["items"][0]["additionalClassifications"]
    self.initial_data["items"][0]["additionalClassifications"] = addit_classif
    if get_now() > CPV_336_INN_FROM:
        response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "items",
                    "description": [
                        "Item with classification.id=33600000-6 have to contain "
                        "exactly one additionalClassifications with scheme=INN"
                    ],
                }
            ],
        )
    else:
        response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
    self.initial_data["items"][0]["additionalClassifications"] = orig_addit_classif
    self.initial_data["items"][0]["classification"]["id"] = data

    addit_classif = [
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
    ]
    data = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "33611000-6"
    orig_addit_classif = self.initial_data["items"][0]["additionalClassifications"]
    self.initial_data["items"][0]["additionalClassifications"] = addit_classif
    if get_now() > CPV_336_INN_FROM:
        response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "items",
                    "description": [
                        "Item with classification.id that starts with 336 and contains "
                        "additionalClassification objects have to contain no more than "
                        "one additionalClassifications with scheme=INN"
                    ],
                }
            ],
        )
    else:
        response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
    self.initial_data["items"][0]["additionalClassifications"] = orig_addit_classif
    self.initial_data["items"][0]["classification"]["id"] = data

    addit_classif = [
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"}
    ]
    data = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "33611000-6"
    orig_addit_classif = self.initial_data["items"][0]["additionalClassifications"]
    self.initial_data["items"][0]["additionalClassifications"] = addit_classif
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config})
    self.initial_data["items"][0]["additionalClassifications"] = orig_addit_classif
    self.initial_data["items"][0]["classification"]["id"] = data
    self.assertEqual(response.status, "201 Created")

    addit_classif = [
        {"scheme": "NotINN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
        {"scheme": "NotINN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
    ]
    data = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "33652000-5"
    orig_addit_classif = self.initial_data["items"][0]["additionalClassifications"]
    self.initial_data["items"][0]["additionalClassifications"] = addit_classif
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config})
    self.initial_data["items"][0]["additionalClassifications"] = orig_addit_classif
    self.initial_data["items"][0]["classification"]["id"] = data
    self.assertEqual(response.status, "201 Created")


@mock.patch("openprocurement.tender.core.procedure.models.item.CPV_336_INN_FROM", get_now() + timedelta(days=1))
def create_tender_with_inn_before(self):
    create_tender_with_inn(self)


@mock.patch("openprocurement.tender.core.procedure.models.item.UNIT_PRICE_REQUIRED_FROM", get_now() + timedelta(days=1))
@mock.patch("openprocurement.tender.core.procedure.models.item.UNIT_CODE_REQUIRED_FROM", get_now() - timedelta(days=1))
def create_tender_with_earlier_non_required_unit(self):
    # can be removed later

    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)
    tender_data = deepcopy(self.initial_data)

    _unit = tender_data["items"][0].pop("unit")
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{'description': [{'unit': ['This field is required.']}],
          'location': 'body',
          'name': 'items'}]

    )

    tender_data = deepcopy(self.initial_data)
    _quantity = tender_data["items"][0].pop("quantity")
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("quantity", response.json["data"]['items'][0])


@mock.patch("openprocurement.tender.core.procedure.models.item.UNIT_PRICE_REQUIRED_FROM", get_now() + timedelta(days=1))
@mock.patch("openprocurement.tender.core.procedure.models.item.UNIT_CODE_REQUIRED_FROM", get_now() - timedelta(days=1))
def create_tender_with_required_unit(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)
    tender_data = deepcopy(self.initial_data)

    _unit = tender_data["items"][0].pop("unit")
    _quantity = tender_data["items"][0].pop("quantity")
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [
                    {
                        'unit': ['This field is required.'],
                    }
                ],
                'location': 'body', 'name': 'items'
            }
        ]
    )
    tender_data["items"][0]['quantity'] = _quantity
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [{'unit': ['This field is required.']}],
                'location': 'body', 'name': 'items'
            }
        ]
    )
    tender_data["items"][0]['unit'] = _unit
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertIn("quantity", response.json["data"]['items'][0])
    self.assertIn("unit", response.json["data"]['items'][0])

    _unit_code = tender_data["items"][0]["unit"].pop("code")
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [{'unit': {'code': ['This field is required.']}}],
                'location': 'body', 'name': 'items'
            }
        ]
    )
    tender_data["items"][0]['unit']['code'] = _unit_code
    tender_data["items"][0]['unit']['value'] = {
        "currency": "USD",  # should be ignored during serializable
        "valueAddedTaxIncluded": False
    }
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json['errors'],
        [
            {
                'description': [
                    {'unit': {'value': {'amount': ['This field is required.']}}}
                ],
                'location': 'body', 'name': 'items'
            }
        ]
    )
    tender_data["items"][0]['unit']['value']['amount'] = 100

    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    for item in response.json["data"]["items"]:
        self.assertEqual(item['unit']['value']['currency'], "UAH")
        self.assertEqual(item['unit']['value']['valueAddedTaxIncluded'], True)

    tender_data["items"][0]["unit"]["code"] = "unknown_code"
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json['errors'],
        [
            {
                'description': [
                    {u'unit': {u'code': [u'Code should be one of valid unit codes.']}}
                ],
                'location': 'body', 'name': 'items'
            }
        ]
    )

    tender_data["items"][0]["unit"]["code"] = "KGM"
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    resp = response.json["data"]
    self.assertEqual("KGM", resp["items"][0]["unit"]["code"])


def create_tender_generated(self):
    data = self.initial_data.copy()
    data.update({"id": "hash", "title": "$1000"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    fields = [
        "procurementMethodType",
        "id",
        "date",
        "dateModified",
        "dateCreated",
        "tenderID",
        "status",
        "criteria",
        "enquiryPeriod",
        "tenderPeriod",
        "minimalStep",
        "items",
        "value",
        "procuringEntity",
        "next_check",
        "procurementMethod",
        "awardCriteria",
        "submissionMethod",
        "title",
        "owner",
        "mainProcurementCategory",
        "milestones",
    ]
    if "procurementMethodDetails" in tender:
        fields.append("procurementMethodDetails")
    self.assertEqual(set(tender), set(fields))
    self.assertNotEqual(data["id"], tender["id"])


def create_tender_draft(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    add_criteria(self, tender["id"], token)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"status": self.primary_tender_status}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], self.primary_tender_status)

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], self.primary_tender_status)


def patch_tender_draft(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})
    is_cfaselectionua = data["procurementMethodType"] == "closeFrameworkAgreementSelectionUA"
    if is_cfaselectionua:
        data.update({"enquiryPeriod": {"endDate": (get_now() + timedelta(days=1)).isoformat()}})

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    if not is_cfaselectionua:
        tender_period = tender["tenderPeriod"]
        tender_period["startDate"] = (parse_date(tender_period["startDate"]) + timedelta(days=1)).isoformat()
        tender_period["endDate"] = (parse_date(tender_period["endDate"]) + timedelta(days=1)).isoformat()
    else:
        tender_period = {
            "startDate": (get_now() + timedelta(days=2)).isoformat(),
            "endDate": (get_now() + timedelta(days=6)).isoformat(),
        }

    item = deepcopy(tender["items"][0])
    item.update(description="test item", quantity=20, id="0" * 32)
    tender_patch_data = {
        "items": [item],
        "features": [
            {
                "title": "test feature",
                "relatedItem": "0" * 32,
                "enum": [{"value": 0.1, "title": "test feature value"}],
            }
        ],
        "tenderPeriod": tender_period,
    }

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": tender_patch_data
        }
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertIn("items", tender)
    self.assertEqual(len(tender["items"]), 1)
    self.assertEqual(tender["items"][0]["description"], "test item")
    if not is_cfaselectionua:
        self.assertEqual(tender["tenderPeriod"], tender_period)
        self.assertEqual(len(tender["features"]), 1)
        self.assertEqual(tender["features"][0]["title"], "test feature")
        self.assertEqual(tender["features"][0]["enum"][0]["value"], 0.1)


def create_tender_central(self):
    data = deepcopy(self.initial_data)

    data["procuringEntity"]["kind"] = "central"
    data["buyers"] = [{
        "id": uuid4().hex,
        "name": test_tender_below_organization["name"],
        "identifier": test_tender_below_organization["identifier"]
    }]

    for item in data["items"]:
        item["relatedBuyer"] = data["buyers"][0]["id"]

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")


def create_tender_central_invalid(self):
    data = deepcopy(self.initial_data)

    with change_auth(self.app, ("Basic", ("broker13", ""))):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    data["procuringEntity"]["kind"] = "central"
    data["buyers"] = [{  # accreditation check gous after model validation now, since "mode" field from data required
        "id": uuid4().hex,
        "name": test_tender_below_organization["name"],
        "identifier": test_tender_below_organization["identifier"]
    }]

    with change_auth(self.app, ("Basic", ("broker13", ""))):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Broker Accreditation level does not permit tender creation"
    )


def create_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(set(response.json["data"]), set(tender))
    self.assertEqual(response.json["data"], tender)

    response = self.app.post_json("/tenders?opt_jsonp=callback", {
        "data": self.initial_data,
        "config": self.initial_config,
    })
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"', response.body.decode())

    response = self.app.post_json("/tenders?opt_pretty=1", {
        "data": self.initial_data,
        "config": self.initial_config,
    })
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body.decode())

    response = self.app.post_json("/tenders", {
        "data": self.initial_data,
        "config": self.initial_config,
        "options": {"pretty": True},
    })
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body.decode())

    tender_data = deepcopy(self.initial_data)
    tender_data["guarantee"] = {"amount": 100500, "currency": "USD"}
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    data = response.json["data"]
    self.assertIn("guarantee", data)
    self.assertEqual(data["guarantee"]["amount"], 100500)
    self.assertEqual(data["guarantee"]["currency"], "USD")

    data = deepcopy(self.initial_data)
    del data["items"][0]["deliveryAddress"]["postalCode"]
    del data["items"][0]["deliveryAddress"]["locality"]
    del data["items"][0]["deliveryAddress"]["streetAddress"]
    del data["items"][0]["deliveryAddress"]["region"]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("postalCode", response.json["data"]["items"][0]["deliveryAddress"])
    self.assertNotIn("locality", response.json["data"]["items"][0]["deliveryAddress"])
    self.assertNotIn("streetAddress", response.json["data"]["items"][0]["deliveryAddress"])
    self.assertNotIn("region", response.json["data"]["items"][0]["deliveryAddress"])

    data = deepcopy(self.initial_data)
    data["items"] = [data["items"][0]]
    data["items"][0]["classification"]["id"] = "33600000-6"

    additional_classification_0 = {
        "scheme": "INN",
        "id": "sodium oxybate",
        "description": "папір і картон гофровані, паперова й картонна тара",
    }
    data["items"][0]["additionalClassifications"] = [additional_classification_0]

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["items"][0]["classification"]["id"], "33600000-6")
    self.assertEqual(response.json["data"]["items"][0]["classification"]["scheme"], "ДК021")
    self.assertEqual(response.json["data"]["items"][0]["additionalClassifications"][0], additional_classification_0)

    additional_classification_1 = {
        "scheme": "ATC",
        "id": "A02AF",
        "description": "папір і картон гофровані, паперова й картонна тара",
    }
    data["items"][0]["additionalClassifications"].append(additional_classification_1)
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["items"][0]["classification"]["id"], "33600000-6")
    self.assertEqual(response.json["data"]["items"][0]["classification"]["scheme"], "ДК021")
    self.assertEqual(
        response.json["data"]["items"][0]["additionalClassifications"],
        [additional_classification_0, additional_classification_1],
    )

    initial_data = deepcopy(self.initial_data)
    initial_data["items"][0]["classification"]["id"] = "99999999-9"
    additional_classification = initial_data["items"][0].pop("additionalClassifications")
    additional_classification[0]["scheme"] = "specialNorms"
    if get_now() > NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM:
        response = self.app.post_json("/tenders", {"data": initial_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]
        self.assertEqual(tender["items"][0]["classification"]["id"], "99999999-9")
        self.assertNotIn("additionalClassifications", tender["items"][0])
    initial_data["items"][0]["additionalClassifications"] = additional_classification
    response = self.app.post_json("/tenders", {"data": initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["items"][0]["classification"]["id"], "99999999-9")
    self.assertEqual(tender["items"][0]["additionalClassifications"], additional_classification)


def create_tender_config_test(self):
    initial_config = deepcopy(self.initial_config)
    initial_config["test"] = True
    response = self.app.post_json("/tenders", {
        "data": self.initial_data,
        "config": initial_config,
    })
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    token = response.json["access"]["token"]

    tender = response.json["data"]
    self.assertNotIn("config", tender)
    self.assertEqual(tender["mode"], "test")
    self.assertTrue(tender["title"].startswith("[ТЕСТУВАННЯ]"))
    self.assertTrue(tender["title_en"].startswith("[TESTING]"))
    self.assertEqual(response.json["config"], initial_config)

    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token), {
        "data": {"title": "changed"},
    })
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    tender = response.json["data"]
    self.assertNotIn("config", tender)
    self.assertEqual(tender["mode"], "test")
    self.assertTrue(tender["title"].startswith("[ТЕСТУВАННЯ]"))
    self.assertTrue(tender["title_en"].startswith("[TESTING]"))
    self.assertEqual(response.json["config"], initial_config)

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    tender = response.json["data"]
    self.assertNotIn("config", tender)
    self.assertEqual(tender["mode"], "test")
    self.assertTrue(tender["title"].startswith("[ТЕСТУВАННЯ]"))
    self.assertTrue(tender["title_en"].startswith("[TESTING]"))
    self.assertEqual(response.json["config"], initial_config)


def tender_funders(self):
    tender_data = deepcopy(self.initial_data)
    tender_data["funders"] = [deepcopy(test_tender_below_organization)]
    tender_data["funders"][0]["identifier"]["id"] = "44000"
    tender_data["funders"][0]["identifier"]["scheme"] = "XM-DAC"
    del tender_data["funders"][0]["scale"]
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("funders", response.json["data"])
    self.assertEqual(response.json["data"]["funders"][0]["identifier"]["id"], "44000")
    self.assertEqual(response.json["data"]["funders"][0]["identifier"]["scheme"], "XM-DAC")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    tender_data["funders"].append(deepcopy(test_tender_below_organization))
    tender_data["funders"][1]["identifier"]["id"] = "44000"
    tender_data["funders"][1]["identifier"]["scheme"] = "XM-DAC"
    del tender_data["funders"][1]["scale"]
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["Funders' identifier should be unique"], "location": "body", "name": "funders"}],
    )

    tender_data["funders"][0]["identifier"]["id"] = "some id"
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Funder identifier should be one of the values allowed"],
                "location": "body",
                "name": "funders",
            }
        ],
    )

    # Can't test different funders for now 'cause we have only one funder in list
    # tender_data['funders'][0]['identifier']['id'] = '11111111'
    # response = self.app.post_json('/tenders', {'data': tender_data})
    # self.assertEqual(response.status, '201 Created')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertIn('funders', response.json['data'])
    # self.assertEqual(len(response.json['data']['funders']), 2)
    # tender = response.json['data']
    # token = response.json['access']['token']

    # response = self.app.patch_json('/tenders/{}?acc_token={}'.format(tender['id'], token), {'data': {'funders': [{
    #     "identifier": {'id': '22222222'}}, {}]}})
    # self.assertEqual(response.status, '200 OK')
    # self.assertIn('funders', response.json['data'])
    # self.assertEqual(len(response.json['data']['funders']), 2)
    # self.assertEqual(response.json['data']['funders'][0]['identifier']['id'], '22222222')

    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token),
                                   {"data": {"funders": None}})
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("funders", response.json["data"])


def tender_fields(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = self.set_initial_status(response.json).json["data"]
    self.assertEqual(
        set(tender) - set(self.initial_data),
        {
            "id",
            "dateModified",
            "dateCreated",
            "criteria",
            "tenderID",
            "date",
            "status",
            "procurementMethod",
            "awardCriteria",
            "submissionMethod",
            "next_check",
            "owner",
        },
    )
    self.assertIn(tender["id"], response.headers["Location"])


def tender_items_float_quantity(self):
    data = deepcopy(self.initial_data)
    quantity = 5.4999999
    data["items"][0]["quantity"] = quantity
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["items"][0]["quantity"], quantity)


def tender_items_zero_quantity(self):
    data = deepcopy(self.initial_data)
    quantity = 0
    data["items"][0]["quantity"] = quantity
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["items"][0]["quantity"], quantity)


def tender_items_negative_quantity(self):
    data = deepcopy(self.initial_data)
    quantity = -1
    data["items"][0]["quantity"] = quantity
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{
            "description": [{"quantity": ["Float value should be greater than 0."]}], 
            "location": "body", 
            "name": "items"
        }],
    )


def get_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], tender)

    response = self.app.get("/tenders/{}?opt_jsonp=callback".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"data": {"', response.body.decode())

    response = self.app.get("/tenders/{}?opt_pretty=1".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "data": {\n        "', response.body.decode())


def tender_features_invalid(self):
    data = self.initial_data.copy()
    item = data["items"][0].copy()
    item["id"] = "1"
    data["items"] = [item, item.copy()]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["Item id should be uniq for all items"], "location": "body", "name": "items"}],
    )
    data["items"][0]["id"] = "0"
    data["features"] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "lot",
            "title": "Потужність всмоктування",
            "enum": [{"value": 0.1, "title": "До 1000 Вт"}, {"value": 0.15, "title": "Більше 1000 Вт"}],
        }
    ]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedItem": ["This field is required."]}],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][0]["relatedItem"] = "2"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedItem": ["relatedItem should be one of lots"]}],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][0]["featureOf"] = "item"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedItem": ["relatedItem should be one of items"]}],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][0]["relatedItem"] = "1"
    data["features"][0]["enum"][0]["value"] = 0.5
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"enum": [{"value": ["Float value should be less than 0.3."]}]}],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][0]["enum"][0]["value"] = 0.15
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"enum": ["Feature value should be uniq for feature"]}],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][0]["enum"][0]["value"] = 0.1
    data["features"].append(data["features"][0].copy())
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Feature code should be uniq for all features"],
                "location": "body",
                "name": "features",
            }
        ],
    )
    data["features"][1]["code"] = "OCDS-123454-YEARS"
    data["features"][1]["enum"][0]["value"] = 0.2
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    if self.initial_lots:
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": ["Sum of max value of all features for lot should be less then or equal to 30%"],
                    "location": "body",
                    "name": "features",
                }
            ],
        )
    else:
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "description": ["Sum of max value of all features should be less then or equal to 30%"],
                    "location": "body",
                    "name": "features",
                }
            ],
        )


def tender_features(self):
    data = self.initial_data.copy()
    data["procuringEntity"]["contactPoint"]["faxNumber"] = "+0440000000"
    item = data["items"][0].copy()
    item["id"] = "1"
    data["items"] = [item]
    data["features"] = [
        {
            "code": "OCDS-123454-AIR-INTAKE",
            "featureOf": "item",
            "relatedItem": "1",
            "title": "Потужність всмоктування",
            "title_en": "Air Intake",
            "description": "Ефективна потужність всмоктування пилососа, в ватах (аероватах)",
            "enum": [{"value": 0.05, "title": "До 1000 Вт"}, {"value": 0.1, "title": "Більше 1000 Вт"}],
        },
        {
            "code": "OCDS-123454-YEARS",
            "featureOf": "tenderer",
            "title": "Років на ринку",
            "title_en": "Years trading",
            "description": "Кількість років, які організація учасник працює на ринку",
            "enum": [{"value": 0.05, "title": "До 3 років"}, {"value": 0.1, "title": "Більше 3 років"}],
        },
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": "Відстрочка платежу",
            "title_en": "Postponement of payment",
            "description": "Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": "До 90 днів"}, {"value": 0.1, "title": "Більше 90 днів"}],
        },
    ]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["features"], data["features"])

    features = tender["features"]
    features[0]["featureOf"] = "tenderer"
    features[0]["relatedItem"] = None
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"features": features}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("features", response.json["data"])
    self.assertNotIn("relatedItem", response.json["data"]["features"][0])

    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token),
                                   {"data": {"features": None}})
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("features", response.json["data"])


def patch_tender_jsonpatch(self):  # TODO: delete this ?
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    import random

    item = tender["items"][0]
    item["additionalClassifications"] = [
        {"scheme": "ДКПП", "id": "{}".format(i), "description": "description #{}".format(i)}
        for i in random.sample(list(range(30)), 25)
    ]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": {"items": [item]}
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    item["additionalClassifications"] = [
        {"scheme": "ДКПП", "id": "{}".format(i), "description": "description #{}".format(i)}
        for i in random.sample(list(range(30)), 20)
    ]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": {
                "items": [item]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


def patch_tender(self):
    data = self.initial_data.copy()
    data["procuringEntity"]["contactPoint"]["faxNumber"] = "+0440000000"
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    owner_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    dateModified = tender.pop("dateModified")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"status": "cancelled"}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "status",
            "description": [
                "Value must be one of ['draft', 'active.enquiries']."
            ]
        }],
    )

    pq_entity = deepcopy(tender["procuringEntity"])
    pq_entity["kind"] = "defense"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": pq_entity}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "procuringEntity",
          "description": "Can't change procuringEntity.kind in a public tender"}]
    )

    pq_entity = deepcopy(tender["procuringEntity"])
    pq_entity["contactPoint"]["faxNumber"] = None
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": pq_entity}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("faxNumber", response.json["data"]["procuringEntity"]["contactPoint"])

    pq_entity = deepcopy(tender["procuringEntity"])
    pq_entity["contactPoint"]["faxNumber"] = "+0440000000"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": pq_entity}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("startDate", response.json["data"]["tenderPeriod"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"procurementMethodRationale": "Open"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_tender = response.json["data"]
    new_dateModified = new_tender.pop("dateModified")
    tender["procurementMethodRationale"] = "Open"
    self.assertEqual(tender, new_tender)
    self.assertNotEqual(dateModified, new_dateModified)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"dateModified": new_dateModified}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "dateModified", "description": "Rogue field"}]
    )

    revisions = self.mongodb.tenders.get(tender["id"]).get("revisions")
    self.assertEqual(revisions[-1]["changes"][0]["op"], "remove")
    self.assertEqual(revisions[-1]["changes"][0]["path"], "/procurementMethodRationale")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"items": [data["items"][0]]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [data["items"][0], data["items"][0]]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    item0 = response.json["data"]["items"][0]
    item1 = response.json["data"]["items"][1]
    self.assertNotEqual(item0.pop("id"), item1.pop("id"))
    self.assertEqual(item0, item1)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item0]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)

    date_modified = response.json["data"]["dateModified"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"enquiryPeriod": {
            "startDate": calculate_tender_business_date(
                parse_date(date_modified), -timedelta(3), None, True
            ).isoformat(),
            "endDate": date_modified
        }}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_tender = response.json["data"]
    self.assertIn("startDate", new_tender["enquiryPeriod"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"amount": 12, "valueAddedTaxIncluded": True}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0],
        {"description": {"valueAddedTaxIncluded": "Rogue field"}, "location": "body", "name": "guarantee"},
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"amount": 12, "currency": "UAH"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 12)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")

    patch_guarantee = deepcopy(response.json["data"]["guarantee"])
    patch_guarantee["currency"] = "USD"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"guarantee": patch_guarantee}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    # response = self.app.patch_json('/tenders/{}'.format(tender['id']), {'data': {'status': 'active.auction'}})
    # self.assertEqual(response.status, '200 OK')

    # response = self.app.get('/tenders/{}'.format(tender['id']))
    # self.assertEqual(response.status, '200 OK')
    # self.assertEqual(response.content_type, 'application/json')
    # self.assertIn('auctionUrl', response.json['data'])

    tender_data = self.mongodb.tenders.get(tender["id"])
    tender_data["status"] = "complete"
    self.mongodb.tenders.save(tender_data)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.auction"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


@mock.patch("openprocurement.tender.core.procedure.models.period.CANT_DELETE_PERIOD_START_DATE_FROM",
            get_now() - timedelta(days=1))
def required_field_deletion(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    period = tender["enquiryPeriod"]
    period["startDate"] = None
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"enquiryPeriod": period}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"startDate": ["This field cannot be deleted"]},
                "location": "body",
                "name": "enquiryPeriod",
            }
        ],
    )

    period = tender["tenderPeriod"]
    period["startDate"] = None
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"tenderPeriod": period}},
    )
    result = response.json["data"]
    self.assertEqual(result["tenderPeriod"]["startDate"], tender["enquiryPeriod"]["endDate"])


def dateModified_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    dateModified = tender["dateModified"]

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["dateModified"], dateModified)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"procurementMethodRationale": "Open"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotEqual(response.json["data"]["dateModified"], dateModified)
    tender = response.json["data"]
    dateModified = tender["dateModified"]

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], tender)
    self.assertEqual(response.json["data"]["dateModified"], dateModified)


def tender_not_found(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/tenders/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.patch_json("/tenders/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def guarantee(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertNotIn("guarantee", response.json["data"])
    tender = response.json["data"]
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"guarantee": {"amount": 55, "currency": "UAH"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 55)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")

    with mock.patch("openprocurement.tender.core.procedure.validation.CRITERION_REQUIREMENT_STATUSES_FROM",
                    get_now() - timedelta(days=1)):
        if data["procurementMethodType"] in GUARANTEE_ALLOWED_TENDER_TYPES:
            self.app.post_json(
                "/tenders/{}/criteria?acc_token={}".format(tender["id"], token),
                {"data": test_exclusion_criteria + test_language_criteria + test_tender_guarantee_criteria},
                status=201
            )

            try:
                self.app.patch_json(
                    "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"status": "active.tendering"}},
                )
            except Exception as e:
                self.app.patch_json(
                    "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"status": "active.enquiries"}},
                )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"guarantee": {"amount": 55, "currency": "USD"}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"guarantee": {"amount": 100500, "currency": "USD"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 100500)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"guarantee": None}}
    )
    self.assertEqual(response.status, "200 OK")

    # WTF ???
    # self.assertIn("guarantee", response.json["data"])
    # self.assertEqual(response.json["data"]["guarantee"]["amount"], 100500)
    # self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")
    self.assertNotIn("guarantee", response.json["data"])

    data["guarantee"] = {"amount": 100, "currency": "USD"}
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 100)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "USD")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"guarantee": {"valueAddedTaxIncluded": True, "amount": 100500, "currency": "USD"}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0],
        {"description": {"valueAddedTaxIncluded": "Rogue field"}, "location": "body", "name": "guarantee"},
    )


def patch_not_author(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]

    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.post_json(
            "/tenders/{}/documents".format(tender["id"]),
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
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(tender["id"], doc_id, owner_token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")


# TenderProcessTest


def invalid_tender_conditions(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = self.tender_token = response.json["access"]["token"]
    # switch to active.tendering
    self.set_status(self.primary_tender_status)
    # create compaint
    response = self.app.post_json(
        "/tenders/{}/complaints".format(tender_id),
        {
            "data": test_tender_below_claim
        },
    )
    complaint_id = response.json["data"]["id"]
    complaint_owner_token = response.json["access"]["token"]
    # answering claim
    self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(tender_id, complaint_id, owner_token),
        {"data": {"status": "answered", "resolutionType": "resolved", "resolution": "I will cancel the tender"}},
    )
    # satisfying resolution
    self.app.patch_json(
        "/tenders/{}/complaints/{}?acc_token={}".format(tender_id, complaint_id, complaint_owner_token),
        {"data": {"satisfied": True, "status": "resolved"}},
    )

    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if get_now() > RELEASE_2020_04_19 and set_complaint_period_end:
        set_complaint_period_end()

    # cancellation
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "reason": "invalid conditions",
        "status": "active"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]

    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    # check status
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def one_valid_bid_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # switch to active.tendering
    response = self.set_status(
        "active.tendering", {"auctionPeriod": {"startDate": (get_now() + timedelta(days=10)).isoformat()}}
    )
    self.assertIn("auctionPeriod", response.json["data"])
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {"tenderers": [test_tender_below_organization], "value": {"amount": 500}}
    self.create_bid(self.tender_id, bid_data)
    # switch to active.qualification
    self.set_status("active.auction", {"status": "active.tendering"})
    response = self.check_chronograph()
    self.assertNotIn("auctionPeriod", response.json["data"])
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    award_date = [i["date"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )
    self.assertNotEqual(response.json["data"]["date"], award_date)

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand slill period
    self.app.authorization = ("Basic", ("chronograph", ""))
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def one_invalid_bid_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # switch to active.tendering
    self.set_status("active.tendering")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {"tenderers": [test_tender_below_organization], "value": {"amount": 500}}
    self.create_bid(self.tender_id, bid_data)
    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    response = self.check_chronograph()
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)
    # set tender status after stand slill period
    response = self.check_chronograph()
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def first_bid_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # switch to active.tendering
    self.set_status("active.tendering")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {"tenderers": [test_tender_below_organization], "value": {"amount": 450}}
    bid, bid_token = self.create_bid(self.tender_id, bid_data)
    bid_id = bid["id"]
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {"tenderers": [test_tender_below_organization], "value": {"amount": 475}}
    self.create_bid(self.tender_id, bid_data)
    # switch to active.auction
    self.set_status("active.auction")

    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction urls
    self.app.patch_json(
        "/tenders/{}/auction".format(tender_id),
        {
            "data": {
                "auctionUrl": "https://tender.auction.url",
                "bids": [
                    {"id": i["id"], "participationUrl": "https://tender.auction.url/for_bid/{}".format(i["id"])}
                    for i in auction_bids_data
                ],
            }
        },
    )
    # view bid participationUrl
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))
    self.assertEqual(response.json["data"]["participationUrl"], "https://tender.auction.url/for_bid/{}".format(bid_id))

    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    self.app.post_json("/tenders/{}/auction".format(tender_id),
                       {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}})
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award2_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    self.assertNotEqual(award_id, award2_id)
    # create first award complaint
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(tender_id, award_id, bid_token),
        {
            "data": test_tender_below_claim
        },
    )
    complaint_id = response.json["data"]["id"]
    complaint_owner_token = response.json["access"]["token"]
    # create first award complaint #2
    self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(tender_id, award_id, bid_token),
        {"data": test_tender_below_draft_claim},
    )
    # answering claim
    self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(tender_id, award_id, complaint_id, owner_token),
        {"data": {"status": "answered", "resolutionType": "resolved", "resolution": "resolution text " * 2}},
    )
    # satisfying resolution
    self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            tender_id, award_id, complaint_id, complaint_owner_token
        ),
        {"data": {"satisfied": True, "status": "resolved"}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # create tender contract document for test
    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=201,
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    # after stand slill period
    self.app.authorization = ("Basic", ("chronograph", ""))
    self.set_status("complete", {"status": "active.awarded"})
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")

    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add document in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(tender_id, contract_id, doc_id, owner_token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
    )

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(tender_id, contract_id, doc_id, owner_token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update document in current (complete) tender status"
    )


def lost_contract_for_active_award(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # switch to active.tendering
    self.set_status("active.tendering")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {"tenderers": [test_tender_below_organization], "value": {"amount": 500}}
    self.create_bid(self.tender_id, bid_data)
    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    response = self.check_chronograph()
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )
    # TBH, doesn't look like a case
    # lost contract
    # tender = self.mongodb.tenders.get(tender_id)
    # del tender["contracts"]
    # self.mongodb.tenders.save(tender)
    # # check tender
    # response = self.app.get("/tenders/{}".format(tender_id))
    # self.assertEqual(response.json["data"]["status"], "active.awarded")
    # self.assertNotIn("contracts", response.json["data"])
    # self.assertIn("next_check", response.json["data"])
    # create lost contract
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    self.assertIn("contracts", response.json["data"])
    self.assertNotIn("next_check", response.json["data"])
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def tender_with_main_procurement_category(self):
    data = dict(**self.initial_data)

    # test fail creation
    data["mainProcurementCategory"] = "whiskey,tango,foxtrot"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "mainProcurementCategory",
                "description": ["Value must be one of ['goods', 'services', 'works']."],
            }
        ],
    )

    # test success creation
    data["mainProcurementCategory"] = "goods"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "goods")

    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.tender_id = tender["id"]

    # test success update tender in active.enquiries status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"mainProcurementCategory": "services"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "services")

    # test fail update mainProcurementCategory in active.tendering status
    self.set_status("active.tendering")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"mainProcurementCategory": "works"}},
        status=403
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update tender in current (active.tendering) status"
            }
        ]
    )


def tender_finance_milestones(self):
    data = dict(**self.initial_data)

    # test creation
    data["milestones"] = [
        {
            "id": "a" * 32,
            "title": "signingTheContract",
            "code": "prepayment",
            "type": "financing",
            "duration": {"days": 2, "type": "banking"},
            "sequenceNumber": 0,
            "percentage": 45.55,
        },
        {
            "title": "deliveryOfGoods",
            "code": "postpayment",
            "type": "financing",
            "duration": {"days": 999, "type": "calendar"},
            "sequenceNumber": 0,
            "percentage": 54.45,
        },
    ]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.assertIn("milestones", tender)
    self.assertEqual(len(tender["milestones"]), 2)
    for milestone in tender["milestones"]:
        self.assertEqual(
            set(milestone.keys()), {"id", "code", "duration", "percentage", "type", "sequenceNumber", "title"}
        )
    self.assertEqual(data["milestones"][0]["id"], tender["milestones"][0]["id"])
    token = response.json["access"]["token"]
    self.tender_id = tender["id"]

    # test success update tender in active.enquiries status
    new_title = "endDateOfTheReportingPeriod"
    patch_milestones = deepcopy(tender["milestones"])
    patch_milestones[1]["title"] = new_title
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"milestones": patch_milestones}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("milestones", response.json["data"])
    milestones = response.json["data"]["milestones"]
    self.assertEqual(len(milestones), 2)
    self.assertEqual(milestones[0]["title"], tender["milestones"][0]["title"])
    self.assertEqual(milestones[1]["title"], new_title)

    # test fail update milestones in active.tendering status
    self.set_status("active.tendering")
    patch_milestones[0]["title"] = new_title
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"milestones": patch_milestones}},
        status=403
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "data",
            "description": "Can't update tender in current (active.tendering) status"
        }]
    )


def tender_milestones_required(self):
    data = dict(**self.initial_data)
    data["milestones"] = []

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": ["Tender should contain at least one milestone"],
            }
        ],
    )


def tender_milestones_not_required(self):
    data = dict(**self.initial_data)
    data["milestones"] = []

    self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=201)


def patch_tender_lots_none(self):
    data = deepcopy(self.initial_data)

    set_tender_lots(data, self.test_lots_data)

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.tender_id = response.json["data"]["id"]
    self.token_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.token_token),
        {"data": {"lots": [None]}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json,
        {'status': 'error', 'errors': [
            {'location': 'body', 'name': 'lots', 'description': [['This field is required.']]}]}
    )


def tender_token_invalid(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.tender_id = response.json["data"]["id"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, "fake token"), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}]
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, "токен з кирилицею"), {"data": {}}, status=422
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


def tender_minimalstep_validation(self):
    data = deepcopy(self.initial_data)
    data["minimalStep"]["amount"] = 35
    # invalid minimalStep validated on tender level
    with mock.patch("openprocurement.tender.core.validation.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() - timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [{"description": ["minimalstep must be between 0.5% and 3% of value (with 2 digits precision)."],
              "location": "body", "name": "minimalStep"}],
        )
    with mock.patch("openprocurement.tender.core.procedure.models.lot.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() + timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=201)
        self.assertEqual(response.status, "201 Created")


def tender_lot_minimalstep_validation(self):
    data = deepcopy(self.initial_data)
    # invalid minimalStep validated on lots level
    test_lots_data = deepcopy(self.test_lots_data)
    test_lots_data.append({
        "title": "invalid lot title",
        "description": "invalid lot description",
        "value": {"amount": 500},
        "minimalStep": {"amount": 35},
    })
    set_tender_lots(data, test_lots_data)
    with mock.patch("openprocurement.tender.core.procedure.models.lot.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() - timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"],
            [{'description':
                  [{'minimalStep': ['minimalstep must be between 0.5% and 3% of value (with 2 digits precision).']}],
              'location': 'body', 'name': 'lots'}
             ]
        )
    with mock.patch("openprocurement.tender.core.procedure.models.lot.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() + timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=201)
        self.assertEqual(response.status, "201 Created")

    # valid minimalStep on lots level
    test_lots_data[1]["minimalStep"]["amount"] = 15
    set_tender_lots(data, test_lots_data)
    with mock.patch("openprocurement.tender.core.procedure.models.lot.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() - timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.json["data"]["value"]["amount"], 1000.0)
        self.assertEqual(response.json["data"]["minimalStep"]["amount"], 15.0)


def patch_tender_minimalstep_validation(self):
    data = deepcopy(self.initial_data)
    lots = deepcopy(self.test_lots_data)
    lots.append({
        "title": "invalid lot title",
        "description": "invalid lot description",
        "value": {"amount": 500},
        "minimalStep": {"amount": 15},
    })
    set_tender_lots(data, lots)

    # tender created before MINIMAL_STEP_VALIDATION_FROM
    with mock.patch("openprocurement.tender.core.procedure.models.lot.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() + timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
        self.tender_id = response.json["data"]["id"]
        self.token_token = response.json["access"]["token"]

        lots = deepcopy(response.json["data"]["lots"])
        lots[0]["minimalStep"]["amount"] = 123
        response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.token_token), {"data": {"lots": lots}}, status=200)
        self.assertEqual(response.status, "200 OK")

    # tender created after MINIMAL_STEP_VALIDATION_FROM
    with mock.patch("openprocurement.tender.core.validation.MINIMAL_STEP_VALIDATION_FROM",
                    get_now() - timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
        self.tender_id = response.json["data"]["id"]
        self.token_token = response.json["access"]["token"]

        lots[0]["minimalStep"]["amount"] = 123
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.token_token), {"data": {"lots": lots}}, status=422)
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"],
            [{'description':
                  [{'minimalStep': ['minimalstep must be between 0.5% and 3% of value (with 2 digits precision).']}],
              'location': 'body', 'name': 'lots'}
             ],
        )

        lots[0]["minimalStep"]["amount"] = 15
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.token_token), {"data": {"lots": lots}}, status=200)
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")


@mock.patch("openprocurement.tender.core.procedure.state.tender_details.RELEASE_ECRITERIA_ARTICLE_17",
            get_now() + timedelta(days=1))
@mock.patch("openprocurement.tender.core.validation.CRITERION_REQUIREMENT_STATUSES_FROM", get_now() - timedelta(days=1))
@mock.patch("openprocurement.tender.core.models.CRITERION_REQUIREMENT_STATUSES_FROM", get_now() - timedelta(days=1))
def patch_item_with_zero_quantity(self):
    self.create_tender()
    response = self.app.get("/tenders/{}".format(self.tender_id))
    item = response.json["data"]["items"][0]
    item["quantity"] = 0
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
                                   {"data": {"items": [item]}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["items"][0]["quantity"], 0)
    item = response.json["data"]["items"][0]
    item["quantity"] = 5
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
                                   {"data": {"items": [item]}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["items"][0]["quantity"], 5)
    criteria = deepcopy(test_exclusion_criteria)
    criteria[0]["relatesTo"] = "item"
    criteria[0]["relatedItem"] = item["id"]
    add_criteria(self, criteria=criteria)
    item["quantity"] = 0
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
                                   {"data": {"items": [item]}},
                                   status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{'description': "Can't set to 0 quantity of {} item while related criterion "
                          "has active requirements".format(item["id"]),
          'location': 'body', 'name': 'data'}])


def patch_items_related_buyer_id(self):
    # create tender with two buyers
    data = deepcopy(self.initial_data)
    test_organization1 = deepcopy(test_tender_below_organization)
    test_organization2 = deepcopy(test_tender_below_organization)
    test_organization2["name"] = "Управління міжнародних справ"
    test_organization2["identifier"]["id"] = "00055555"

    data["status"] = "draft"
    data["buyers"] = [
        {"name": test_organization1["name"], "identifier": test_organization1["identifier"]},
        {"name": test_organization2["name"], "identifier": test_organization2["identifier"]},
    ]

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "draft")

    tender = response.json["data"]

    tender_id = response.json["data"]["id"]
    tender_token = response.json["access"]["token"]

    buyer1_id = response.json["data"]["buyers"][0]["id"]
    buyer2_id = response.json["data"]["buyers"][1]["id"]

    self.assertEqual(len(response.json["data"]["buyers"]), 2)
    self.assertEqual(len(response.json["data"]["items"]), 1)


    if tender["procurementMethodType"] != "priceQuotation":
        add_criteria(self, tender_id, tender_token)

    patch_request_path = "/tenders/{}?acc_token={}".format(tender_id, tender_token)

    response = self.app.patch_json(
        patch_request_path,
        {"data": {"status": self.primary_tender_status}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {'description': [
                {'relatedBuyer': ['This field is required.']}
            ],
            'location': 'body',
            'name': 'items'}
        ],
    )
    items = deepcopy(tender["items"])
    items[0]["relatedBuyer"] = buyer1_id
    response = self.app.patch_json(
        patch_request_path,
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["relatedBuyer"], buyer1_id)

    response = self.app.patch_json(
        patch_request_path,
        {"data": {"status": self.primary_tender_status}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], self.primary_tender_status)

    if tender["procurementMethodType"] == "priceQuotation":
        return

    # adding new unassigned items
    second_item = deepcopy(self.initial_data["items"][0])
    second_item["description"] = "телевізори"
    third_item = deepcopy(self.initial_data["items"][0])
    third_item["description"] = "ноутбуки"

    response = self.app.patch_json(
        patch_request_path,
        {"data": {"items": [items[0], second_item, third_item]}},
        status=422
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{'description': [{'relatedBuyer': ['This field is required.']}],
          'location': 'body',
          'name': 'items'}],
    )

    # assign items
    second_item["relatedBuyer"] = buyer2_id
    third_item["relatedBuyer"] = buyer2_id

    response = self.app.patch_json(
        patch_request_path,
        {"data": {"items": [items[0], second_item, third_item]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][1]["relatedBuyer"], buyer2_id)
    self.assertEqual(response.json["data"]["items"][2]["relatedBuyer"], buyer2_id)

    self.assertEqual(response.json["data"]["items"][1]["description"], "телевізори")
    self.assertEqual(response.json["data"]["items"][2]["description"], "ноутбуки")
    self.assertEqual(len(response.json["data"]["items"]), 3)


@mock.patch("openprocurement.tender.core.validation.RELEASE_GUARANTEE_CRITERION_FROM", get_now() - timedelta(days=1))
def tender_with_guarantee(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]
    self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_exclusion_criteria + test_language_criteria},
        status=201
    )

    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"guarantee": {"amount": 0, "currency": "UAH"}}},
        status=200)

    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"guarantee": {"amount": 1, "currency": "UAH"}}},
        status=200)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"status": "active.tendering"}},
        status=403)
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Should be specified CRITERION.OTHER.BID.GUARANTEE and 'guarantee.amount' more than 0"
            }
        ]
    )

    self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_tender_guarantee_criteria},
        status=201
    )
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"status": "active.tendering"}},
        status=200)


@mock.patch("openprocurement.tender.core.validation.RELEASE_GUARANTEE_CRITERION_FROM", get_now() - timedelta(days=1))
def tender_with_guarantee_multilot(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"
    lots = deepcopy(self.test_lots_data)
    lots.append({
        "title": "invalid lot title",
        "description": "invalid lot description",
        "value": {"amount": 500},
        "minimalStep": {"amount": 15},
    })
    set_tender_lots(data, lots)

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    related_lot_id = response.json["data"]["lots"][0]["id"]
    tender_lot_guarantee_criteria = deepcopy(test_tender_guarantee_criteria)
    tender_lot_guarantee_criteria[0]["relatesTo"] = "lot"
    tender_lot_guarantee_criteria[0]["relatedItem"] = related_lot_id
    self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_exclusion_criteria + test_language_criteria + tender_lot_guarantee_criteria},
        status=201
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"status": "active.tendering"}},
        status=403
    )
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Should be specified 'guarantee.amount' more than 0 to lot"
            }
        ]
    )

    self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, related_lot_id, self.tender_token),
        {"data": {"guarantee": {"amount": 1, "currency": "UAH"}}},
        status=200
    )
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"status": "active.tendering"}},
        status=200
    )


@mock.patch("openprocurement.tender.core.validation.RELEASE_GUARANTEE_CRITERION_FROM", get_now() - timedelta(days=1))
def activate_bid_guarantee_multilot(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"
    lots = deepcopy(self.test_lots_data)
    lots.append({
        "title": "invalid lot title",
        "description": "invalid lot description",
        "value": {"amount": 500},
        "minimalStep": {"amount": 15},
        "guarantee": {"amount": 1, "currency": "UAH"}
    })
    set_tender_lots(data, lots)

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]
    lots = response.json["data"]["lots"]

    tender_lot_guarantee_criteria = deepcopy(test_tender_guarantee_criteria)
    tender_lot_guarantee_criteria[0]["relatesTo"] = "lot"
    tender_lot_guarantee_criteria[0]["relatedItem"] = response.json["data"]["lots"][1]["id"]

    contract_lot_guarantee_criteria = deepcopy(test_contract_guarantee_criteria)
    contract_lot_guarantee_criteria[0]["relatesTo"] = "lot"
    contract_lot_guarantee_criteria[0]["relatedItem"] = response.json["data"]["lots"][1]["id"]
    self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": test_exclusion_criteria + test_language_criteria + tender_lot_guarantee_criteria + contract_lot_guarantee_criteria},
        status=201
    )
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"status": "active.tendering"}},
        status=200
    )

    bid = deepcopy(self.test_bids_data)[0]
    set_bid_lotvalues(bid, lots)
    bid["status"] = "draft"
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid})
    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]

    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    criteria = response.json["data"]

    rrs = []
    lot_req = None
    winner_req = None
    for criterion in criteria:
        for req in criterion["requirementGroups"][0]["requirements"]:
            if criterion["source"] == "tenderer" and criterion["relatesTo"] != "lot":
                rrs.append(
                    {
                        "title": "Requirement response",
                        "description": "some description",
                        "requirement": {
                            "id": req["id"],
                            "title": req["title"],
                        },
                        "value": True,
                    },
                )
            elif criterion["source"] == "tenderer" and criterion["relatesTo"] == "lot":
                lot_req = req
            elif criterion["source"] == "winner" and criterion["relatesTo"] == "lot":
                winner_req = req
    response = self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": rrs},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": {"status": "pending"}},
        status=422
    )
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{u'description': [u'Must be answered on all criteria with source `tenderer` and GUARANTEE if declared'],
          u'location': u'body',
          u'name': u'requirementResponses'}]
    )

    lot_rr = [{
        "title": "Requirement response",
        "description": "some description",
        "requirement": {
            "id": lot_req["id"],
            "title": lot_req["title"],
        },
        "value": True,
    }]
    self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": lot_rr},
        status=201
    )

    self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": {"status": "pending"}},
        status=422
    )
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{u'description': [u'Must be answered on all criteria with source `tenderer` and GUARANTEE if declared'],
          u'location': u'body',
          u'name': u'requirementResponses'}]
    )

    lot_rr = [{
        "title": "Requirement response",
        "description": "some description",
        "requirement": {
            "id": winner_req["id"],
            "title": winner_req["title"],
        },
        "value": True,
    }]
    self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": lot_rr},
        status=201
    )
    self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": {"status": "pending"}},
        status=200
    )


def patch_enquiry_tender_periods(self):
    self.create_tender()

    resp = self.app.get(f"/tenders/{self.tender_id}")
    tender = resp.json["data"]

    self.assertEqual(tender["status"], "active.enquiries")
    enq_p = tender["enquiryPeriod"]
    tender_p = tender["tenderPeriod"]

    # check enquiryPeriod:endDate>= enquiryPeriod.startDate + 3 робочі дні
    if get_now() > RELEASE_2020_04_19:
        end_data = calculate_tender_business_date(parse_date(enq_p["startDate"], TZ), timedelta(days=2), tender, True)
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {"enquiryPeriod": {
                "startDate": enq_p["startDate"],
                "endDate": end_data.isoformat(),
            }}},
            status=422
        )
        self.assertEqual(
            response.json["errors"],
            [{
                "location": "body",
                "name": "enquiryPeriod",
                "description": [
                    "the enquiryPeriod cannot end earlier than 3 business days after the start"
                ]
            }],
        )

    # check tenderPeriod:startDate більше ніж enquiryPeriod:endDate
    end_data = calculate_tender_business_date(parse_date(enq_p["startDate"], TZ), timedelta(days=10), tender, True)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"enquiryPeriod": {
            "startDate": enq_p["startDate"],
            "endDate": end_data.isoformat(),
        }}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "tenderPeriod",
            "description": [
                "period should begin after enquiryPeriod"
            ]
        }],
    )

    # tenderPeriod:endDate>= tenderPeriod.startDate + 2 робочі дні
    if get_now() > RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {"data": {
                "enquiryPeriod": {
                    "startDate": enq_p["startDate"],
                    "endDate": end_data.isoformat(),
                },
                "tenderPeriod": {
                    "startDate": end_data.isoformat(),
                    "endDate": end_data.isoformat(),
                }
            }},
            status=422
        )
        self.assertEqual(
            response.json["errors"],
            [{
                "location": "body",
                "name": "tenderPeriod",
                "description": [
                    "tenderPeriod must be at least 2 full business days long"
                ]
            }],
        )

    # all fine
    tender_end = calculate_tender_business_date(end_data, timedelta(days=2), tender, True)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {
            "enquiryPeriod": {
                "startDate": enq_p["startDate"],
                "endDate": end_data.isoformat(),
            },
            "tenderPeriod": {
                "startDate": end_data.isoformat(),
                "endDate": tender_end.isoformat(),
            }
        }},
        status=200
    )
