import random
from copy import deepcopy
from datetime import timedelta
from unittest import mock
from uuid import uuid4

from openprocurement.api.constants import (
    DEFAULT_CONTRACT_TEMPLATE_KEY,
    GUARANTEE_ALLOWED_TENDER_TYPES,
    MILESTONE_CODES,
    MILESTONE_TITLES,
    ROUTE_PREFIX,
    TZ,
)
from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.tests.base import test_signer_info
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_base_organization,
    test_tender_below_buyer,
    test_tender_below_cancellation,
    test_tender_below_claim,
    test_tender_below_data,
    test_tender_below_draft_claim,
    test_tender_below_supplier,
)
from openprocurement.tender.core.tests.base import (
    test_contract_guarantee_criteria,
    test_default_criteria,
    test_tender_guarantee_criteria,
)
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)
from openprocurement.tender.core.tests.criteria_utils import add_criteria
from openprocurement.tender.core.tests.utils import (
    activate_contract,
    change_auth,
    generate_criterion_responses,
    get_contract_data,
    get_contract_template_name,
    set_bid_items,
    set_bid_lotvalues,
    set_tender_criteria,
    set_tender_lots,
)
from openprocurement.tender.core.utils import calculate_tender_full_date


def listing(self):
    response = self.app.get("/tenders")
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

    while True:
        response = self.app.get("/tenders")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in tenders})
    self.assertEqual({i["dateModified"] for i in response.json["data"]}, {i["dateModified"] for i in tenders})
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders]))

    response = self.app.get("/tenders?limit=1")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("prev_page", response.json)
    self.assertEqual(len(response.json["data"]), 1)
    offset = response.json["next_page"]["offset"]

    response = self.app.get(f"/tenders?offset={offset}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)

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
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in tenders})
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
    self.add_sign_doc(tender_id, tender_token)
    self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={tender_token}", {"data": {"status": self.primary_tender_status}}
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
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in tenders})
    self.assertEqual({i["dateModified"] for i in response.json["data"]}, {i["dateModified"] for i in tenders})
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
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "status"})
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders?feed=changes", params=[("opt_fields", "status,enquiryPeriod")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "status"})
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in tenders})
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
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in tenders})
    self.assertEqual({i["dateModified"] for i in response.json["data"]}, {i["dateModified"] for i in tenders})
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders]))


@mock.patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() + timedelta(days=1))
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
                "description": ["Please use a mapping for this field or EstimatedValue instance instead of str."],
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
                "description": "Tender minimal step valueAddedTaxIncluded should be identical to tender valueAddedTaxIncluded",
                "location": "body",
                "name": "minimalStep.valueAddedTaxIncluded",
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
                "description": "Tender minimal step currency should be identical to tender currency",
                "location": "body",
                "name": "minimalStep.currency",
            }
        ],
    )

    data = self.initial_data["items"][0].pop("additionalClassifications")
    cpv_code = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "99999999-9"

    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=201)
    self.initial_data["items"][0]["additionalClassifications"] = data
    self.initial_data["items"][0]["classification"]["id"] = cpv_code
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "201 Created")

    data = self.initial_data["items"][0]["additionalClassifications"][0]["scheme"]
    self.initial_data["items"][0]["additionalClassifications"][0]["scheme"] = "Не ДКПП"
    cpv_code = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "99999999-9"
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["items"][0]["additionalClassifications"][0]["scheme"] = data
    self.initial_data["items"][0]["classification"]["id"] = cpv_code
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
                'description': {'contactPoint': {'telephone': ['wrong telephone format (could be missed +)']}},
                'location': 'body',
                'name': 'procuringEntity',
            }
        ],
    )

    data = self.initial_data["items"][0].copy()
    classification = data["classification"].copy()
    classification["id"] = "19212310-1"
    data["classification"] = classification
    item = deepcopy(self.initial_data["items"][0])
    self.initial_data["items"] = [item, data]
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["items"] = self.initial_data["items"][:1]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["CPV class of items (1921, 4461) should be identical"], "location": "body", "name": "items"}],
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
    self.initial_data["items"][0]["classification"]["id"] = "00000000-0"
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
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
                },
            }
        ],
    )
    data = deepcopy(self.initial_data)
    config = deepcopy(self.initial_config)
    config.pop("hasAuction", None)
    response = self.app.post_json(
        request_path,
        {"data": data, "config": config},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "config.hasAuction", "description": "This field is required."}],
    )
    data = deepcopy(self.initial_data)
    config = deepcopy(self.initial_config)
    config["nonExistantConfig"] = True
    response = self.app.post_json(
        request_path,
        {"data": data, "config": config},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "config",
                "description": "Additional properties are not allowed ('nonExistantConfig' was unexpected)",
            }
        ],
    )


def create_tender_invalid_config(self):
    request_path = "/tenders"
    config = deepcopy(self.initial_config)
    config.update({"minBidsNumber": 0})
    response = self.app.post_json(
        request_path,
        {
            "data": self.initial_data,
            "config": config,
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "0 is less than the minimum of 1", "location": "body", "name": "config.minBidsNumber"}],
    )
    config.update({"minBidsNumber": 10})
    response = self.app.post_json(
        request_path,
        {
            "data": self.initial_data,
            "config": config,
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "10 is greater than the maximum of 1", "location": "body", "name": "config.minBidsNumber"}],
    )


@mock.patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def validate_enquiry_period(self):
    self.initial_data.pop("procurementMethodDetails", None)

    request_path = "/tenders"
    data = self.initial_data["enquiryPeriod"]
    now = get_now()

    valid_start_date = now + timedelta(days=7)
    valid_end_date = calculate_tender_full_date(
        valid_start_date, timedelta(days=3), tender=self.initial_data, working_days=True
    ).isoformat()
    invalid_end_date = calculate_tender_full_date(
        valid_start_date, timedelta(days=2), tender=self.initial_data, working_days=True
    ).isoformat()
    tender_valid_end_date = calculate_tender_full_date(
        valid_start_date, timedelta(days=8), tender=self.initial_data, working_days=True
    ).isoformat()

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
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"enquiryPeriod": period}}, status=422
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


@mock.patch("openprocurement.tender.core.procedure.utils.RELEASE_2020_04_19", get_now() - timedelta(days=1))
def validate_tender_period(self):
    now = get_now()

    enquiry_start_date = now + timedelta(days=7)
    enquiry_end_date = calculate_tender_full_date(
        enquiry_start_date, timedelta(days=3), tender=self.initial_data, working_days=True
    )

    valid_start_date = enquiry_end_date
    valid_end_date = calculate_tender_full_date(
        valid_start_date, timedelta(days=2), tender=self.initial_data, working_days=True
    ).isoformat()
    invalid_end_date = calculate_tender_full_date(
        valid_start_date, timedelta(days=1), tender=self.initial_data, working_days=True
    ).isoformat()

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

    self.initial_data["tenderPeriod"] = {"startDate": valid_start_date, "endDate": valid_end_date}
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
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"tenderPeriod": period}}, status=422
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
    request_path = "/tenders"

    addit_classif = [
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
    ]
    data = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "33600000-6"
    orig_addit_classif = self.initial_data["items"][0]["additionalClassifications"]
    self.initial_data["items"][0]["additionalClassifications"] = addit_classif

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

    self.initial_data["items"][0]["additionalClassifications"] = orig_addit_classif
    self.initial_data["items"][0]["classification"]["id"] = data

    addit_classif = [
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"}
    ]
    data = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "33611000-6"
    if "contractTemplateName" in self.initial_data:
        self.initial_data["contractTemplateName"] = get_contract_template_name(self.initial_data)
    if self.agreement_id:
        agreement = self.mongodb.agreements.get(self.agreement_id)
        agreement["classification"] = {"id": "33611000-6", "scheme": "ДК021"}
        self.mongodb.agreements.save(agreement)
    orig_addit_classif = self.initial_data["items"][0]["additionalClassifications"]
    self.initial_data["items"][0]["additionalClassifications"] = addit_classif
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config})
    self.initial_data["items"][0]["additionalClassifications"] = orig_addit_classif
    self.initial_data["items"][0]["classification"]["id"] = data
    if "contractTemplateName" in self.initial_data:
        self.initial_data["contractTemplateName"] = get_contract_template_name(self.initial_data)
    self.assertEqual(response.status, "201 Created")

    addit_classif = [
        {"scheme": "NotINN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
        {"scheme": "NotINN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
    ]
    data = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "33652000-5"
    if "contractTemplateName" in self.initial_data:
        self.initial_data["contractTemplateName"] = get_contract_template_name(self.initial_data)
    if self.agreement_id:
        agreement = self.mongodb.agreements.get(self.agreement_id)
        agreement["classification"] = {"id": "33652000-5", "scheme": "ДК021"}
        self.mongodb.agreements.save(agreement)
    orig_addit_classif = self.initial_data["items"][0]["additionalClassifications"]
    self.initial_data["items"][0]["additionalClassifications"] = addit_classif
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config})
    self.initial_data["items"][0]["additionalClassifications"] = orig_addit_classif
    self.initial_data["items"][0]["classification"]["id"] = data
    if "contractTemplateName" in self.initial_data:
        self.initial_data["contractTemplateName"] = get_contract_template_name(self.initial_data)
    self.assertEqual(response.status, "201 Created")


def create_tender_with_estimated_value(self):
    data = deepcopy(self.initial_data)
    config = deepcopy(self.initial_config)

    # To ensure that tender has estimated value
    config["hasValueEstimation"] = True

    # Minimal step validation if hasAuction is True
    lot_min_step = data["lots"][0].pop("minimalStep")
    response = self.app.post_json("/tenders", {"data": data, "config": config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': ['This field is required.'],
                'location': 'body',
                'name': 'minimalStep',
            }
        ],
    )
    data["lots"][0]["minimalStep"] = lot_min_step

    # Tender amount validation
    tender_value_amount = data["value"].pop("amount")
    response = self.app.post_json("/tenders", {"data": data, "config": config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': 'This field is required',
                'location': 'body',
                'name': 'value.amount',
            }
        ],
    )
    data["value"]["amount"] = tender_value_amount

    # Lot amount validation
    lot_value_amount = data["lots"][0]["value"].pop("amount")
    response = self.app.post_json("/tenders", {"data": data, "config": config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{'description': 'This field is required', 'location': 'body', 'name': 'lots.value.amount'}],
    )
    data["lots"][0]["value"]["amount"] = lot_value_amount

    # Set lot minimal step 0
    data["lots"][0]["value"]["amount"] = 0
    response = self.app.post_json("/tenders", {"data": data, "config": config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': 'Minimal step value should be less than lot value',
                'location': 'body',
                'name': 'lots',
            }
        ],
    )
    data["lots"][0]["value"]["amount"] = lot_value_amount

    # Set lot minimal step amount too high
    data["lots"][0]["minimalStep"]["amount"] = 50
    response = self.app.post_json("/tenders", {"data": data, "config": config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': 'Minimal step value must be between 0.5% and 3% of value (with 2 digits precision).',
                'location': 'body',
                'name': 'data',
            }
        ],
    )
    data["lots"][0]["minimalStep"]["amount"] = 15

    # Try to tender amount 0
    data["value"]["amount"] = 0
    data["minimalStep"]["amount"] = 0
    response = self.app.post_json("/tenders", {"data": data, "config": config})
    self.assertEqual(response.status, "201 Created")

    # Check it was recalculated and set to sum of lots value
    self.assertEqual(
        response.json["data"]["value"]["amount"],
        sum(lot["value"]["amount"] for lot in data["lots"]),
    )

    # Try to set tender minimal step amount too high
    data["minimalStep"]["amount"] = tender_value_amount - 1
    response = self.app.post_json("/tenders", {"data": data, "config": config})
    self.assertEqual(response.status, "201 Created")

    # Check it was recalculated and set to min of lots minimal step
    self.assertEqual(
        response.json["data"]["minimalStep"]["amount"],
        min(lot["minimalStep"]["amount"] for lot in data["lots"]),
    )


@mock.patch("openprocurement.tender.core.procedure.models.item.UNIT_PRICE_REQUIRED_FROM", get_now() + timedelta(days=1))
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
                'location': 'body',
                'name': 'items',
            }
        ],
    )
    tender_data["items"][0]['quantity'] = _quantity
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{'description': [{'unit': ['This field is required.']}], 'location': 'body', 'name': 'items'}],
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
        [{'description': [{'unit': {'code': ['This field is required.']}}], 'location': 'body', 'name': 'items'}],
    )
    tender_data["items"][0]['unit']['code'] = _unit_code
    tender_data["items"][0]['unit']['value'] = {
        "currency": "USD",  # should be ignored during serializable
        "valueAddedTaxIncluded": False,
    }
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json['errors'],
        [
            {
                'description': [{'unit': {'value': {'amount': ['This field is required.']}}}],
                'location': 'body',
                'name': 'items',
            }
        ],
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
                'description': [{'unit': {'code': ['Code should be one of valid unit codes.']}}],
                'location': 'body',
                'name': 'items',
            }
        ],
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
        "lots",
        "documents",
        "noticePublicationDate",
        "contractTemplateName",
    ]
    if self.tender_for_funders:
        fields.append("funders")
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
    self.add_sign_doc(tender["id"], token)
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

    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token), {"data": tender_patch_data})

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


def tender_notice_documents(self):
    data = self.initial_data.copy()

    # try to add tender with two notice documents
    data.update(
        {
            "status": "draft",
            "documents": [
                {
                    "id": "e4d7216f28dc4a1cbf18c5e4ee2cd1c5",
                    "title": "sign.p7s",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "notice",
                },
                {
                    "title": "notice.p7s",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "notice",
                },
            ],
        }
    )
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.json["errors"][0]["description"], "notice document in tender should be only one")

    data["documents"] = [
        {
            "id": "e4d7216f28dc4a1cbf18c5e4ee2cd1c5",
            "title": "sign.p7s",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
            "documentType": "notice",
        },
    ]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    # try to patch documents and add another notice document
    invalid_data_patch = {
        "documents": [
            {
                "id": "e4d7216f28dc4a1cbf18c5e4ee2cd1c5",
                "title": "sign.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentType": "notice",
            },
            {
                "title": "notice.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentType": "notice",
            },
        ],
    }

    response = self.app.patch_json(
        f"/tenders/{tender['id']}?acc_token={token}",
        {"data": invalid_data_patch},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.json["errors"][0]["description"], "notice document in tender should be only one")


def create_tender_central(self):
    data = deepcopy(self.initial_data)

    buyer = deepcopy(test_tender_below_buyer)
    buyer["id"] = uuid4().hex

    data["procuringEntity"]["kind"] = "central"
    data["buyers"] = [buyer]

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

    buyer = deepcopy(test_tender_below_buyer)
    buyer["id"] = uuid4().hex

    data["procuringEntity"]["kind"] = "central"
    data["buyers"] = [buyer]

    for item in data["items"]:
        item["relatedBuyer"] = data["buyers"][0]["id"]

    with change_auth(self.app, ("Basic", ("broker13", ""))):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Broker Accreditation level does not permit tender creation"
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

    response = self.app.post_json(
        "/tenders?opt_jsonp=callback",
        {
            "data": self.initial_data,
            "config": self.initial_config,
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"', response.body.decode())

    response = self.app.post_json(
        "/tenders?opt_pretty=1",
        {
            "data": self.initial_data,
            "config": self.initial_config,
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body.decode())

    response = self.app.post_json(
        "/tenders",
        {
            "data": self.initial_data,
            "config": self.initial_config,
            "options": {"pretty": True},
        },
    )
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
    if "contractTemplateName" in self.initial_data:
        data["contractTemplateName"] = get_contract_template_name(data)

    additional_classification_0 = {
        "scheme": "INN",
        "id": "sodium oxybate",
        "description": "папір і картон гофровані, паперова й картонна тара",
    }
    data["items"][0]["additionalClassifications"] = [additional_classification_0]

    if self.agreement_id:
        agreement = self.mongodb.agreements.get(self.agreement_id)
        agreement["classification"] = {"id": "33600000-6", "scheme": "ДК021"}
        self.mongodb.agreements.save(agreement)

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

    if self.agreement_id:
        agreement = self.mongodb.agreements.get(self.agreement_id)
        agreement["classification"] = {"id": "99999999-9", "scheme": "ДК021"}
        self.mongodb.agreements.save(agreement)

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


def tender_funders(self):
    tender_data = deepcopy(self.initial_data)
    tender_data["funders"] = [deepcopy(test_tender_below_base_organization)]
    tender_data["funders"][0]["identifier"]["id"] = "44000"
    tender_data["funders"][0]["identifier"]["scheme"] = "XM-DAC"
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("funders", response.json["data"])
    self.assertEqual(response.json["data"]["funders"][0]["identifier"]["id"], "44000")
    self.assertEqual(response.json["data"]["funders"][0]["identifier"]["scheme"], "XM-DAC")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    tender_data["funders"].append(deepcopy(test_tender_below_base_organization))
    tender_data["funders"][1]["identifier"]["id"] = "44000"
    tender_data["funders"][1]["identifier"]["scheme"] = "XM-DAC"
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

    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"funders": None}})
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
            "documents",
            "noticePublicationDate",
        },
    )
    self.assertIn(tender["id"], response.headers["Location"])


def tender_inspector(self):
    tender_data = deepcopy(self.initial_data)
    organization = deepcopy(test_tender_below_base_organization)
    funder_organization = deepcopy(organization)
    funder_organization["identifier"]["id"] = "44000"
    funder_organization["identifier"]["scheme"] = "XM-DAC"

    tender_data["inspector"] = organization
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "inspector", "description": ["Inspector couldn't exist without funders"]}],
    )

    tender_data["funders"] = [funder_organization]
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("funders", response.json["data"])
    self.assertIn("inspector", response.json["data"])

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("funders", response.json["data"])
    tender_id = response.json["data"]["id"]
    tender_token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={tender_token}",
        {"data": {"inspector": organization}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "inspector", "description": ["Inspector couldn't exist without funders"]}],
    )

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={tender_token}",
        {"data": {"funders": [funder_organization], "inspector": organization}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("funders", response.json["data"])
    self.assertIn("inspector", response.json["data"])


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
        [
            {
                "description": [{"quantity": ["Float value should be greater than 0."]}],
                "location": "body",
                "name": "items",
            }
        ],
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

    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"features": None}})
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("features", response.json["data"])


def patch_tender_jsonpatch(self):  # TODO: delete this ?
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    item = tender["items"][0]
    item["additionalClassifications"] = [
        {"scheme": "ДКПП", "id": "{}".format(i), "description": "description #{}".format(i)}
        for i in random.sample(list(range(30)), 25)
    ]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"items": [item]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    item["additionalClassifications"] = [
        {"scheme": "ДКПП", "id": "{}".format(i), "description": "description #{}".format(i)}
        for i in random.sample(list(range(30)), 20)
    ]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"items": [item]}},
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
    item_id = tender["items"][0]["id"]
    dateModified = tender.pop("dateModified")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "cancelled"}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "status",
                "description": [
                    "Value must be one of ['draft', 'active.enquiries', 'active.pre-qualification', "
                    "'active.pre-qualification.stand-still']."
                ],
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"plans": []}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "plans", "description": "Rogue field"}],
    )

    pq_entity = deepcopy(tender["procuringEntity"])
    pq_entity["kind"] = "defense"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": pq_entity}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "procuringEntity",
                "description": "Can't change procuringEntity.kind in a public tender",
            }
        ],
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
        status=422,
    )
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "dateModified", "description": "Rogue field"}]
    )

    revisions = self.mongodb.tenders.get(tender["id"]).get("revisions")
    self.assertEqual(revisions[-1]["changes"][0]["op"], "remove")
    self.assertEqual(revisions[-1]["changes"][0]["path"], "/procurementMethodRationale")

    item = deepcopy(data["items"][0])
    item["id"] = item_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {"items": [item]},
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    item = deepcopy(data["items"][0])
    item["id"] = item_id
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [{**item, "id": item_id}, {**item, "id": uuid4().hex}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    item0 = response.json["data"]["items"][0]
    item1 = response.json["data"]["items"][1]
    self.assertNotEqual(item0.pop("id"), item1.pop("id"))
    self.assertEqual(item0, item1)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"items": [{**item0, "id": item_id}]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)

    date_modified = response.json["data"]["dateModified"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "enquiryPeriod": {
                    "startDate": calculate_tender_full_date(
                        parse_date(date_modified), -timedelta(3), tender=None, working_days=True
                    ).isoformat(),
                    "endDate": date_modified,
                }
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_tender = response.json["data"]
    self.assertIn("startDate", new_tender["enquiryPeriod"])
    self.assertIn("clarificationsUntil", new_tender["enquiryPeriod"])

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
        {"data": {"guarantee": {"amount": 12, "currency": "UAH"}}},
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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.patch_json("/tenders/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


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
        {"data": {"guarantee": {"amount": 55, "currency": "UAH"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("guarantee", response.json["data"])
    self.assertEqual(response.json["data"]["guarantee"]["amount"], 55)
    self.assertEqual(response.json["data"]["guarantee"]["currency"], "UAH")

    with mock.patch(
        "openprocurement.tender.core.procedure.validation.CRITERION_REQUIREMENT_STATUSES_FROM",
        get_now() - timedelta(days=1),
    ):
        if data["procurementMethodType"] in GUARANTEE_ALLOWED_TENDER_TYPES:
            test_tender_guarantee_criteria_modified = deepcopy(test_tender_guarantee_criteria)
            # FIXME: hack, should be lot criteria, rewrite for lot
            test_tender_guarantee_criteria_modified[0]["relatesTo"] = "tender"
            criteria = []
            criteria.extend(test_default_criteria)
            set_tender_criteria(criteria, tender["lots"], tender["items"])
            self.app.post_json(
                "/tenders/{}/criteria?acc_token={}".format(tender["id"], token),
                {
                    "data": criteria,
                },
                status=201,
            )
            self.add_sign_doc(tender["id"], token)

            try:
                self.app.patch_json(
                    "/tenders/{}?acc_token={}".format(tender["id"], token),
                    {"data": {"status": "active.tendering"}},
                )
            except Exception as e:
                self.app.patch_json(
                    "/tenders/{}?acc_token={}".format(tender["id"], token),
                    {"data": {"status": "active.enquiries"}},
                )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"guarantee": {"amount": 55, "currency": "USD"}}},
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
    data = dict(self.initial_data)
    data["documents"] = [
        {  # pass documents with the tender post request
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }
    ]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]

    document = tender["documents"][0]
    self.assertEqual(document["author"], "tender_owner")  # TODO: add author here

    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(tender["id"], document["id"], owner_token),
        {"data": {"description": "document description"}},
    )
    self.assertEqual("document description", response.json["data"]["description"])

    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        self.app.patch_json(
            "/tenders/{}/documents/{}".format(tender["id"], document["id"]),
            {"data": {"description": "bot description"}},
            status=403,
        )

    response = self.app.post_json(
        "/tenders/{}/documents?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )
    self.assertEqual(response.json["data"]["author"], "tender_owner")

    with change_auth(self.app, ("Basic", ("bot", "bot"))):
        response = self.app.post_json(
            "/tenders/{}/documents".format(tender["id"]),
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
        self.assertEqual(response.json["data"]["author"], "bots")
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

    # cancellation
    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reason": "invalid conditions", "status": "active"})
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
    bid_data = {"tenderers": [test_tender_below_supplier], "value": {"amount": 500}}
    _, bid_token = self.create_bid(self.tender_id, bid_data)
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
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertNotEqual(response.json["data"]["date"], award_date)

    # get contract id
    contract = get_contract_data(self, tender_id)
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
    activate_contract(self, tender_id, contract_id, owner_token, bid_token)
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
    bid_data = {"tenderers": [test_tender_below_supplier], "value": {"amount": 500}}
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
        {"data": {"status": "unsuccessful", "qualified": False}},
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
    bid_data = {"tenderers": [test_tender_below_supplier], "value": {"amount": 450}}
    bid, bid_token = self.create_bid(self.tender_id, bid_data)
    bid_id = bid["id"]
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {"tenderers": [test_tender_below_supplier], "value": {"amount": 475}}
    _, bid2_token = self.create_bid(self.tender_id, bid_data)
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
    self.app.post_json(
        "/tenders/{}/auction".format(tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
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
        {"data": test_tender_below_claim},
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
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True}},
    )
    # get contract id
    contract = get_contract_data(self, tender_id)
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
    activate_contract(self, tender_id, contract_id, owner_token, bid2_token)
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def lost_contract_for_active_award(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    items = response.json["data"]["items"]
    second_item = deepcopy(items[0])
    second_item["id"] = uuid4().hex
    second_item["description"] = "телевізори"
    second_item["quantity"] = 0
    second_item["unit"]["value"]["amount"] = 0
    items.append(second_item)
    self.app.patch_json(f"/tenders/{tender_id}?acc_token={owner_token}", {"data": {"items": items}})
    # switch to active.tendering
    self.set_status("active.tendering")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = {"tenderers": [test_tender_below_supplier], "value": {"amount": 500}}

    keys_to_remove = {"deliveryDate", "deliveryAddress", "classification", "additionalClassifications"}

    for item in items:
        for key in list(item.keys()):
            if key in keys_to_remove:
                item.pop(key, None)
        item["unit"]["value"]["valueAddedTaxIncluded"] = False

    bid_data["items"] = items
    _, bid_token = self.create_bid(self.tender_id, bid_data)
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
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True}},
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
    contract = get_contract_data(self, tender_id)
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid_token)
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")

    response = self.app.get("/contracts/{}".format(contract_id))
    self.assertEqual(len(response.json["data"]["items"]), 1)  # item with quantity 0 not in contract


def tender_with_main_procurement_category(self):
    data = deepcopy(self.initial_data)

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

    # test fail mainProcurementCategory in active.tendering status
    self.set_status("active.tendering")
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"mainProcurementCategory": "works"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update tender in current (active.tendering) status",
            }
        ],
    )


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.MILESTONES_SEQUENCE_NUMBER_VALIDATION_FROM",
    get_now() + timedelta(days=1),
)
def tender_finance_milestones(self):
    data = deepcopy(self.initial_data)

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
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Can't update tender in current (active.tendering) status",
            }
        ],
    )


def tender_milestones_required(self):
    data = deepcopy(self.initial_data)
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
    data = deepcopy(self.initial_data)
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
        "/tenders/{}?acc_token={}".format(self.tender_id, self.token_token), {"data": {"lots": [None]}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json,
        {
            'status': 'error',
            'errors': [{'location': 'body', 'name': 'lots', 'description': [['This field is required.']]}],
        },
    )


def tender_token_invalid(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.tender_id = response.json["data"]["id"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, "fake token"), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, "токен з кирилицею"), {"data": {}}, status=422
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


def tender_minimalstep_validation(self):
    data = deepcopy(self.initial_data)
    data["minimalStep"]["amount"] = 500
    del data["lots"]
    for field in ("items", "milestones"):
        for item in data[field]:
            del item["relatedLot"]
    # invalid minimalStep validated on tender level
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0],
        {
            "description": "Minimal step value must be between 0.5% and 3% of value (with 2 digits precision).",
            "location": "body",
            "name": "data",
        },
    )
    with mock.patch(
        "openprocurement.tender.core.procedure.state.tender_details.MINIMAL_STEP_VALIDATION_FROM",
        get_now() + timedelta(days=1),
    ):
        data["lots"] = self.initial_lots
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=201)
        self.assertEqual(response.status, "201 Created")


def tender_item_related_lot_validation(self):
    data = deepcopy(self.initial_data)
    data["minimalStep"]["amount"] = 10
    del data["lots"]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {"location": "body", "name": "milestones", "description": ["relatedLot should be one of the lots."]},
            {
                "location": "body",
                "name": "items",
                "description": [{"relatedLot": ["relatedLot should be one of lots"]}],
            },
        ],
    )


def tender_lot_minimalstep_validation(self):
    data = deepcopy(self.initial_data)
    # invalid minimalStep validated on lots level
    test_lots_data = deepcopy(self.test_lots_data)
    test_lots_data.append(
        {
            "title": "invalid lot title",
            "description": "invalid lot description",
            "value": {"amount": 500},
            "minimalStep": {"amount": 35},
        }
    )
    set_tender_lots(data, test_lots_data)
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Minimal step value must be between 0.5% and 3% of value (with 2 digits precision).",
                'location': 'body',
                'name': 'data',
            }
        ],
    )
    with mock.patch(
        "openprocurement.tender.core.procedure.state.tender_details.MINIMAL_STEP_VALIDATION_FROM",
        get_now() + timedelta(days=1),
    ):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=201)
        self.assertEqual(response.status, "201 Created")

    # valid minimalStep on lots level
    test_lots_data[1]["minimalStep"]["amount"] = 15
    set_tender_lots(data, test_lots_data)

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["value"]["amount"], 1000.0)
    self.assertEqual(response.json["data"]["minimalStep"]["amount"], 15.0)


def patch_tender_minimalstep_validation(self):
    data = deepcopy(self.initial_data)
    lots = deepcopy(self.test_lots_data)
    lots.append(
        {
            "title": "invalid lot title",
            "description": "invalid lot description",
            "value": {"amount": 500},
            "minimalStep": {"amount": 15},
        }
    )
    set_tender_lots(data, lots)

    # tender created before MINIMAL_STEP_VALIDATION_FROM
    with mock.patch(
        "openprocurement.tender.core.procedure.state.tender_details.MINIMAL_STEP_VALIDATION_FROM",
        get_now() + timedelta(days=1),
    ):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
        self.tender_id = response.json["data"]["id"]
        self.token_token = response.json["access"]["token"]

        lots = deepcopy(response.json["data"]["lots"])
        lots[0]["minimalStep"]["amount"] = 123
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.token_token), {"data": {"lots": lots}}, status=200
        )
        self.assertEqual(response.status, "200 OK")

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.token_token = response.json["access"]["token"]

    lots[0]["minimalStep"]["amount"] = 123
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.token_token), {"data": {"lots": lots}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Minimal step value must be between 0.5% and 3% of value (with 2 digits precision).",
                'location': 'body',
                'name': 'data',
            }
        ],
    )

    lots[0]["minimalStep"]["amount"] = 15
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.token_token), {"data": {"lots": lots}}, status=200
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_criteria_rules",
    mock.Mock(return_value={}),
)
def patch_item_with_zero_quantity(self):
    self.create_tender()
    response = self.app.get("/tenders/{}".format(self.tender_id))
    tender = response.json["data"]
    item = tender["items"][0]
    item["quantity"] = 0
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"items": [item]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["items"][0]["quantity"], 0)
    item = response.json["data"]["items"][0]
    item["quantity"] = 5
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"items": [item]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["items"][0]["quantity"], 5)
    criteria = deepcopy(test_default_criteria)
    criteria[0]["relatesTo"] = "item"
    criteria[0]["relatedItem"] = item["id"]
    set_tender_criteria(criteria, tender["lots"], tender["items"])
    add_criteria(self, criteria=criteria)
    item["quantity"] = 0
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), {"data": {"items": [item]}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Can't set to 0 quantity of {} item while related criterion "
                "has active requirements".format(item["id"]),
                'location': 'body',
                'name': 'data',
            }
        ],
    )


def patch_items_related_buyer_id(self):
    # create tender with two buyers
    data = deepcopy(self.initial_data)
    test_buyer1 = deepcopy(test_tender_below_buyer)
    test_buyer2 = deepcopy(test_tender_below_buyer)
    test_buyer2["name"] = "Управління міжнародних справ"
    test_buyer2["identifier"]["id"] = "00055555"

    data["status"] = "draft"
    data["buyers"] = [
        test_buyer1,
        test_buyer2,
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

    response = self.app.patch_json(patch_request_path, {"data": {"status": self.primary_tender_status}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{'description': [{'relatedBuyer': ['This field is required.']}], 'location': 'body', 'name': 'items'}],
    )
    items = deepcopy(tender["items"])
    items[0]["relatedBuyer"] = buyer1_id
    response = self.app.patch_json(
        patch_request_path,
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["relatedBuyer"], buyer1_id)

    self.add_sign_doc(tender_id, tender_token)

    response = self.app.patch_json(patch_request_path, {"data": {"status": self.primary_tender_status}})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], self.primary_tender_status)

    if tender["procurementMethodType"] == "priceQuotation":
        return

    # adding new unassigned items
    second_item = deepcopy(self.initial_data["items"][0])
    second_item["id"] = uuid4().hex
    second_item["description"] = "телевізори"
    third_item = deepcopy(self.initial_data["items"][0])
    third_item["id"] = uuid4().hex
    third_item["description"] = "ноутбуки"

    response = self.app.patch_json(
        patch_request_path, {"data": {"items": [items[0], second_item, third_item]}}, status=422
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [{'description': [{'relatedBuyer': ['This field is required.']}], 'location': 'body', 'name': 'items'}],
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


def tender_with_guarantee_multilot(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"
    lots = deepcopy(self.test_lots_data)
    lots.append(
        {
            "title": "invalid lot title",
            "description": "invalid lot description",
            "value": {"amount": 500},
            "minimalStep": {"amount": 15},
        }
    )
    set_tender_lots(data, lots)

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    tender = response.json["data"]
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    related_lot_id = response.json["data"]["lots"][0]["id"]

    criteria = []
    criteria.extend(test_default_criteria)
    criteria.extend(test_tender_guarantee_criteria)
    set_tender_criteria(criteria, tender["lots"], tender["items"])

    for criterion in criteria:
        if criterion["classification"]["id"] == "CRITERION.OTHER.BID.GUARANTEE":
            criterion["relatesTo"] = "lot"
            criterion["relatedItem"] = related_lot_id

    self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": criteria,
        },
        status=201,
    )
    self.add_sign_doc(self.tender_id, self.tender_token)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.tendering"}},
        status=403,
    )
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Should be specified 'guarantee.amount' more than 0 to lot",
            }
        ],
    )

    self.app.patch_json(
        "/tenders/{}/lots/{}?acc_token={}".format(self.tender_id, related_lot_id, self.tender_token),
        {"data": {"guarantee": {"amount": 1, "currency": "UAH"}}},
        status=200,
    )
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.tendering"}},
        status=200,
    )


def activate_bid_guarantee_multilot(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"
    lots = deepcopy(self.test_lots_data)
    lots.append(
        {
            "title": "invalid lot title",
            "description": "invalid lot description",
            "value": {"amount": 500},
            "minimalStep": {"amount": 15},
            "guarantee": {"amount": 1, "currency": "UAH"},
        }
    )
    set_tender_lots(data, lots)

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    tender = response.json["data"]
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]
    lots = response.json["data"]["lots"]

    related_lot_id = response.json["data"]["lots"][1]["id"]

    criteria = []
    criteria.extend(test_default_criteria)
    criteria.extend(test_tender_guarantee_criteria)
    criteria.extend(test_contract_guarantee_criteria)
    set_tender_criteria(criteria, tender["lots"], tender["items"])

    for criterion in criteria:
        if criterion["classification"]["id"] == "CRITERION.OTHER.BID.GUARANTEE":
            criterion["relatesTo"] = "lot"
            criterion["relatedItem"] = related_lot_id
        if criterion["classification"]["id"] == "CRITERION.OTHER.CONTRACT.GUARANTEE":
            criterion["relatesTo"] = "lot"
            criterion["relatedItem"] = related_lot_id

    self.app.post_json(
        "/tenders/{}/criteria?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": criteria,
        },
        status=201,
    )
    self.add_sign_doc(self.tender_id, self.tender_token)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active.tendering"}},
        status=200,
    )
    tender = response.json["data"]

    bid = deepcopy(self.test_bids_data)[0]
    set_bid_lotvalues(bid, lots)
    set_bid_items(self, bid, tender["items"])
    bid["status"] = "draft"
    response = self.app.post_json("/tenders/{}/bids".format(self.tender_id), {"data": bid})
    bid_id = response.json["data"]["id"]
    bid_token = response.json["access"]["token"]

    response = self.app.get("/tenders/{}/criteria".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    criteria = response.json["data"]

    rrs = []
    lot_req = None
    lot_criteria = None
    winner_req = None
    winner_criteria = None
    for criterion in criteria:
        if criterion["source"] in ("tenderer", "winner") and criterion["relatesTo"] != "lot":
            rrs.extend(generate_criterion_responses(criterion))
        elif criterion["source"] == "tenderer" and criterion["relatesTo"] == "lot":
            lot_criteria = criterion
            lot_req = criterion["requirementGroups"][0]["requirements"]
        elif criterion["source"] == "winner" and criterion["relatesTo"] == "lot":
            winner_criteria = criterion
            winner_req = criterion["requirementGroups"][0]["requirements"]
    response = self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": rrs},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": {"status": "pending"}},
        status=422,
    )
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [
                    'Responses are required for all criteria with source tenderer/winner, '
                    f'failed for criteria {lot_criteria["id"]}, {winner_criteria["id"]}'
                ],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    lot_rrs = generate_criterion_responses(lot_criteria)
    self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": lot_rrs},
        status=201,
    )

    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": {"status": "pending"}},
        status=422,
    )
    self.assertIn("errors", response.json)
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [
                    'Responses are required for all criteria with source tenderer/winner, '
                    f'failed for criteria {winner_criteria["id"]}'
                ],
                'location': 'body',
                'name': 'requirementResponses',
            }
        ],
    )

    lot_rrs = generate_criterion_responses(winner_criteria)
    self.app.post_json(
        "/tenders/{}/bids/{}/requirement_responses?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": lot_rrs},
        status=201,
    )
    self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(self.tender_id, bid_id, bid_token),
        {"data": {"status": "pending"}},
        status=200,
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
        end_data = calculate_tender_full_date(
            parse_date(enq_p["startDate"], TZ),
            timedelta(days=2),
            tender=tender,
            working_days=True,
        )
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "enquiryPeriod": {
                        "startDate": enq_p["startDate"],
                        "endDate": end_data.isoformat(),
                    }
                }
            },
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "enquiryPeriod",
                    "description": ["the enquiryPeriod cannot end earlier than 3 business days after the start"],
                }
            ],
        )

    # check tenderPeriod:startDate більше ніж enquiryPeriod:endDate
    end_data = calculate_tender_full_date(
        parse_date(enq_p["startDate"], TZ), timedelta(days=10), tender=tender, working_days=True
    )
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "enquiryPeriod": {
                    "startDate": enq_p["startDate"],
                    "endDate": end_data.isoformat(),
                }
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "tenderPeriod", "description": ["period should begin after enquiryPeriod"]}],
    )

    # tenderPeriod:endDate>= tenderPeriod.startDate + 2 робочі дні
    if get_now() > RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
            {
                "data": {
                    "enquiryPeriod": {
                        "startDate": enq_p["startDate"],
                        "endDate": end_data.isoformat(),
                    },
                    "tenderPeriod": {
                        "startDate": end_data.isoformat(),
                        "endDate": end_data.isoformat(),
                    },
                }
            },
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "tenderPeriod",
                    "description": ["tenderPeriod must be at least 2 full business days long"],
                }
            ],
        )

    # all fine
    tender_end = calculate_tender_full_date(end_data, timedelta(days=2), tender=tender, working_days=True)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "status": "active.tendering",
            "data": {
                "enquiryPeriod": {
                    "startDate": enq_p["startDate"],
                    "endDate": end_data.isoformat(),
                },
                "tenderPeriod": {
                    "startDate": end_data.isoformat(),
                    "endDate": tender_end.isoformat(),
                },
            },
        },
        status=200,
    )


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELATED_LOT_REQUIRED_FROM",
    get_now() + timedelta(days=1),
)
def tender_created_before_related_lot_is_required(self):
    data = deepcopy(test_tender_below_data)
    data["status"] = "draft"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    # successfully patch tender without lot
    self.add_sign_doc(self.tender_id, self.tender_token)
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}", {"data": {"status": "active.enquiries"}}, status=200
    )
    self.assertEqual(response.json["data"]["status"], "active.enquiries")


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELATED_LOT_REQUIRED_FROM",
    get_now() - timedelta(days=1),
)
def tender_created_after_related_lot_is_required(self):
    data = deepcopy(test_tender_below_data)
    data["status"] = "draft"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]
    self.add_sign_doc(self.tender_id, self.tender_token)

    # forbid to patch tender without lot
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}", {"data": {"status": "active.enquiries"}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "item.relatedLot", "description": "This field is required"}],
    )

    lots = deepcopy(self.test_lots_data)
    lots.append(
        {
            "title": "invalid lot title",
            "description": "invalid lot description",
            "value": {"amount": 500},
            "minimalStep": {"amount": 15},
        }
    )
    set_tender_lots(data, lots)
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]
    self.add_sign_doc(self.tender_id, self.tender_token)

    # successfully patch tender with lot
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}", {"data": {"status": "active.enquiries"}}, status=200
    )
    self.assertEqual(response.json["data"]["status"], "active.enquiries")


def tender_financing_milestones(self):
    data = deepcopy(self.initial_data)
    percentage = data["milestones"][-1].pop("percentage", None)
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "milestones", "description": [{"percentage": ["This field is required."]}]}],
    )

    data["milestones"][-1]["percentage"] = percentage
    data["milestones"][-1]["duration"]["days"] = 1500
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [{"duration": ["days shouldn't be more than 1000 for financing milestone"]}],
            }
        ],
    )

    data["milestones"][-1]["duration"]["days"] = 1000
    data["milestones"][-1]["code"] = "standard"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [{"code": [f"Value must be one of {MILESTONE_CODES['financing']}"]}],
            }
        ],
    )

    data["milestones"][-1]["code"] = "postpayment"
    data["milestones"][-1]["title"] = "afterPostPayment"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [{"title": [f"Value must be one of {MILESTONE_TITLES['financing']}"]}],
            }
        ],
    )
    data["milestones"][-1]["title"] = "signingTheContract"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")


def tender_delivery_milestones(self):
    lot_id = self.initial_lots[0]["id"]
    data = deepcopy(self.initial_data)
    data["milestones"].append(
        {
            "id": "c" * 32,
            "title": "signingTheContract",
            "type": "delivery",
            "duration": {"days": 1500, "type": "calendar"},
            "sequenceNumber": 0,
            "code": "postpayment",
            "percentage": 10,
        }
    )
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [
                    {
                        "code": [f"Value must be one of {MILESTONE_CODES['delivery']}"],
                    }
                ],
            }
        ],
    )

    data["milestones"][-1]["code"] = "standard"
    data["milestones"][-1]["title"] = "executionOfWorks"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [{"title": [f"Value must be one of {MILESTONE_TITLES['delivery']}"]}],
            }
        ],
    )
    data["milestones"][-1]["title"] = "signingTheContract"
    data["milestones"][-1]["sequenceNumber"] = 3
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [
                    {
                        "relatedLot": "Related lot must be set in all milestones or all milestones should be related to tender"
                    }
                ],
            }
        ],
    )
    data["milestones"][-1]["relatedLot"] = lot_id
    del data["milestones"][-1]["percentage"]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "milestones", "description": [{"percentage": ["This field is required."]}]}],
    )
    data["milestones"][-1]["percentage"] = 10
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": f"Sum of the delivery milestone percentages 10.0 is not equal 100 for lot {lot_id}.",
            }
        ],
    )
    data["milestones"][-1]["percentage"] = 100
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender_id = response.json["data"]["id"]
    tender_token = response.json["access"]["token"]

    # try to patch incorrect milestone code
    data["milestones"][-1]["code"] = "postpayment"
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={tender_token}",
        {"data": {"milestones": data["milestones"]}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [
                    {
                        "code": [f"Value must be one of {MILESTONE_CODES['delivery']}"],
                    }
                ],
            }
        ],
    )


def tender_milestones_sequence_number(self):
    data = deepcopy(self.initial_data)
    lot = deepcopy(self.initial_lots[0])
    lot["id"] = uuid4().hex
    data["lots"].append(lot)
    data["items"][0]["relatedLot"] = lot["id"]
    data["milestones"] = [
        {
            "title": "signingTheContract",
            "code": "prepayment",
            "type": "financing",
            "duration": {"days": 2, "type": "banking"},
            "sequenceNumber": 1,
            "percentage": 100,
            "relatedLot": self.initial_lots[0]["id"],
        },
        {
            "title": "signingTheContract",
            "code": "prepayment",
            "type": "financing",
            "duration": {"days": 2, "type": "banking"},
            "sequenceNumber": 2,
            "percentage": 100,
            "relatedLot": lot["id"],
        },
    ]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [
                    {
                        "sequenceNumber": "Field should contain incrementing sequence numbers starting from 1 for tender/lot separately"
                    }
                ],
            }
        ],
    )
    data["milestones"][-1]["sequenceNumber"] = 1
    del data["milestones"][0]["relatedLot"]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": [
                    {
                        "relatedLot": "Related lot must be set in all milestones or all milestones should be related to tender"
                    }
                ],
            }
        ],
    )
    data["milestones"] = [
        {
            "title": "signingTheContract",
            "code": "prepayment",
            "type": "financing",
            "duration": {"days": 2, "type": "banking"},
            "sequenceNumber": 1,
            "percentage": 45.55,
            "relatedLot": self.initial_lots[0]["id"],
        },
        {
            "title": "signingTheContract",
            "type": "delivery",
            "duration": {"days": 1500, "type": "calendar"},
            "sequenceNumber": 2,
            "code": "standard",
            "percentage": 10,
            "relatedLot": self.initial_lots[0]["id"],
        },
        {
            "title": "signingTheContract",
            "type": "delivery",
            "duration": {"days": 1500, "type": "calendar"},
            "sequenceNumber": 3,
            "code": "standard",
            "percentage": 90,
            "relatedLot": self.initial_lots[0]["id"],
        },
        {
            "title": "signingTheContract",
            "type": "delivery",
            "duration": {"days": 1500, "type": "calendar"},
            "sequenceNumber": 1,
            "code": "standard",
            "percentage": 100,
            "relatedLot": lot["id"],
        },
        {
            "title": "deliveryOfGoods",
            "code": "postpayment",
            "type": "financing",
            "duration": {"days": 999, "type": "calendar"},
            "sequenceNumber": 2,
            "percentage": 100,
            "relatedLot": lot["id"],
        },
        {
            "title": "deliveryOfGoods",
            "code": "postpayment",
            "type": "financing",
            "duration": {"days": 999, "type": "calendar"},
            "sequenceNumber": 4,
            "percentage": 54.45,
            "relatedLot": self.initial_lots[0]["id"],
        },
    ]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")


def check_notice_doc_during_activation(self):
    data = deepcopy(test_tender_below_data)
    data["status"] = "draft"
    lots = deepcopy(self.test_lots_data)
    set_tender_lots(data, lots)
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]
    self.assertNotIn("noticePublicationDate", response.json["data"])

    request_path = f"/tenders/{self.tender_id}?acc_token={self.tender_token}"
    response = self.app.patch_json(
        request_path,
        {"data": {"status": "active.enquiries"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"], "Document with type 'notice' and format pkcs7-signature is required"
    )

    # let's add sign doc
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/documents?acc_token={self.tender_token}",
        {
            "data": {
                "title": "sign.p7s",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pdf",
                "documentType": "notice",
            }
        },
    )
    doc_id = response.json["data"]["id"]

    # put document title
    self.app.put_json(
        f"/tenders/{self.tender_id}/documents/{doc_id}?acc_token={self.tender_token}",
        {
            "data": {
                "title": "new.txt",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pdf",
                "documentType": "notice",
            }
        },
    )

    # try to activate tender
    response = self.app.patch_json(
        request_path,
        {"data": {"status": "active.enquiries"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"], "Document with type 'notice' and format pkcs7-signature is required"
    )
    # patch title
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/documents/{doc_id}?acc_token={self.tender_token}",
        {"data": {"title": "sign-2.p7s"}},
    )

    response = self.app.patch_json(
        request_path,
        {"data": {"status": "active.enquiries"}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("noticePublicationDate", response.json["data"])
    self.assertEqual(response.json["data"]["status"], "active.enquiries")


@mock.patch(
    "openprocurement.tender.core.procedure.utils.CONTRACT_TEMPLATES",
    {
        "0322": {
            "templates": [
                {
                    "title": "Зернові культури, картопля, овочі, фрукти та горіхи",
                    "name": "03220000.0001.01",
                    "active": True,
                },
            ],
        },
        "03222": {
            "templates": [
                {
                    "title": "Фрукти і горіхи",
                    "name": "03222000.0001.01",
                    "active": True,
                },
            ],
        },
        "0931": {
            "templates": [],
        },
        DEFAULT_CONTRACT_TEMPLATE_KEY: {
            "templates": [
                {
                    "title": "Загальний шаблон",
                    "name": "00000000.0001.01",
                    "active": False,
                },
                {
                    "title": "Загальний шаблон",
                    "name": "00000000.0002.01",
                    "active": True,
                },
                {
                    "title": "Загальний шаблон",
                    "name": "00000000.0003.01",
                    "active": True,
                },
            ],
        },
    },
)
def contract_template_name_set(self):

    def prepare_tender_state(classification_ids, template_name=None):
        """Prepare tender state for testing"""
        tender = self.mongodb.tenders.get(self.tender_id)

        # Update tender items classifications
        item = deepcopy(tender["items"][0])
        tender["items"] = []
        for classification_id in classification_ids:
            item = deepcopy(item)
            item["id"] = uuid4().hex
            item["classification"]["id"] = classification_id
            tender["items"].append(item)

        # Update agreement classification
        if getattr(self, "agreement_id"):
            agreement = self.mongodb.agreements.get(self.agreement_id)
            if agreement:
                if agreement.get("items"):
                    item = deepcopy(agreement["items"][0])
                    agreement["items"] = []
                    for classification_id in classification_ids:
                        item = deepcopy(item)
                        item["id"] = uuid4().hex
                        item["classification"]["id"] = classification_id
                        agreement["items"].append(item)
                elif agreement.get("classification"):
                    agreement["classification"]["id"] = classification_ids[0]
                self.mongodb.agreements.save(agreement)

        # Handle contract template
        if template_name is not None:
            tender["contractTemplateName"] = template_name
        else:
            tender.pop("contractTemplateName", None)

        # Handle documents, remove contractProforma
        for doc in tender.get("documents", []):
            if doc.get("documentType") == "contractProforma":
                tender["documents"].remove(doc)

        # Clean criteria
        tender.pop("criteria", None)

        self.mongodb.tenders.save(tender)

        criteria_status_map = {
            "closeFrameworkAgreementSelectionUA": ("draft", "active.enquiries"),
            "requestForProposal": ("draft", "active.enquiries"),
            "belowThreshold": ("draft", "active.enquiries"),
            "negotiation": [],
            "negotiation.quick": [],
            "aboveThresholdUA.defense": [],
        }
        default_criteria_statuses = ("draft", "active.tendering")
        criteria_statuses = criteria_status_map.get(pmt, default_criteria_statuses)

        if criteria_statuses and tender["status"] in criteria_statuses:
            criteria = []
            criteria.extend(test_default_criteria)
            set_tender_criteria(criteria, tender.get("lots", []), tender.get("items", []))
            self.app.post_json(
                f"/tenders/{self.tender_id}/criteria?acc_token={self.tender_token}",
                {"data": criteria},
                status=201,
            )

    def test_no_template(classification_ids):
        # Disallowed set contractTemplateName for classification that has 0 templates
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"contractTemplateName": "invalid_contract_template_name"}},
            status=422,
        )
        self.assertIn(
            f"contractTemplateName is not allowed for current classifications {', '.join(classification_ids)}",
            response.json["errors"][0]["description"],
        )

    def test_after_contract_proforma():
        # Disallowed set contractTemplateName if exist document with documentType contractProforma

        if pmt == "closeFrameworkAgreementSelectionUA" and status == "active.tendering":
            return

        response = self.app.post_json(
            f"/tenders/{self.tender_id}/documents?acc_token={self.tender_token}",
            {
                "data": {  # pass documents with the tender post request
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "contractProforma",
                }
            },
        )
        doc_id = response.json["data"]["id"]

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"contractTemplateName": "invalid_contract_template_name"}},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "contractTemplateName",
                    "description": "Cannot use both contractTemplateName and contractProforma document simultaneously",
                }
            ],
        )

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/documents/{doc_id}?acc_token={self.tender_token}",
            {"data": {"documentType": "tenderNotice"}},
        )
        self.assertEqual(response.status, "200 OK")

    def test_set_invalid_value(template_name, allowed_template_names, classification_ids):
        # Set invalid contractTemplateName value from standards and not default classification
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"contractTemplateName": template_name}},
            status=422,
        )
        self.assertEqual(response.json["errors"][0]["name"], "contractTemplateName")
        self.assertIn(
            f"Incorrect contractTemplateName {template_name} "
            f"for current classifications {', '.join(classification_ids)}, "
            f"use one of {', '.join(allowed_template_names)}",
            response.json["errors"][0]["description"],
        )

    def test_match_multiple_template_groups(template_name, classification_ids):
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"contractTemplateName": template_name}},
            status=422,
        )
        self.assertEqual(response.json["errors"][0]["name"], "contractTemplateName")
        self.assertIn(
            f"Multiple contract template groups match current classifications {', '.join(classification_ids)}. "
            "Consider using items with classifications that belong to the same contract template group",
            response.json["errors"][0]["description"],
        )

    def test_contract_proforma():

        if pmt == "closeFrameworkAgreementSelectionUA" and status == "active.tendering":
            return

        response = self.app.post_json(
            f"/tenders/{self.tender_id}/documents?acc_token={self.tender_token}",
            {
                "data": {  # pass documents with the tender post request
                    "title": "name.doc",
                    "url": self.generate_docservice_url(),
                    "hash": "md5:" + "0" * 32,
                    "format": "application/msword",
                    "documentType": "contractProforma",
                }
            },
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Cannot use both contractTemplateName and contractProforma document simultaneously",
                }
            ],
        )

    def test_set_valid_value(template_name, extra=None):
        # Set valid value success

        data = {"contractTemplateName": template_name}

        if not (pmt == "closeFrameworkAgreementSelectionUA" and status == "active.tendering"):
            data.update(extra or {})

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": data},
        )
        self.assertEqual(response.status, "200 OK")

        for key, value in data.items():
            self.assertEqual(response.json["data"][key], value)

    def test_not_required():
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"contractTemplateName": None}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertNotIn("contractTemplateName", response.json["data"])

    def test_required(extra=None):
        data = {"contractTemplateName": None}
        data.update(extra or {})
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": data},
            status=422,
        )
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "contractTemplateName",
                    "description": "Either contractTemplateName or contractProforma document is required",
                }
            ],
        )

    data = deepcopy(self.initial_data)
    data["procuringEntity"]["signerInfo"] = test_signer_info
    data["status"] = "draft"
    pmt = data["procurementMethodType"]

    status_map = {
        "closeFrameworkAgreementSelectionUA": ("draft", "active.enquiries", "active.tendering"),
        "requestForProposal": ("draft", "active.enquiries", "active.tendering"),
        "belowThreshold": ("draft", "active.enquiries"),
        "negotiation": ("draft", "active"),
        "negotiation.quick": ("draft", "active"),
        "priceQuotation": ("draft",),
    }
    default_statuses = ("draft", "active.tendering")
    statuses = status_map.get(pmt, default_statuses)

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    required_for_pmts = (
        "priceQuotation",
        "belowThreshold",
        "aboveThreshold",
        "aboveThresholdUA",
        "aboveThresholdEU",
        "simple.defense",
        "competitiveOrdering",
    )

    # Test activation
    if pmt in required_for_pmts:
        # Test general template
        prepare_tender_state(
            template_name=None,
            classification_ids=["44617100-9"],
        )
        test_required(
            extra={"status": self.primary_tender_status},
        )

        # Test no template
        prepare_tender_state(
            template_name=None,
            classification_ids=["09310000-5"],
        )
        test_required(
            extra={"status": self.primary_tender_status},
        )

    # Test procedure for every allowed statuses
    for status in statuses:
        self.set_status(status)

        if status == "draft":
            prepare_tender_state(
                template_name="00000000.0002.01",
                classification_ids=["44617100-9"],
            )
            test_not_required()

            prepare_tender_state(
                template_name=None,
                classification_ids=["44617100-9"],
            )
            test_after_contract_proforma()
        else:
            if pmt in required_for_pmts:
                prepare_tender_state(
                    template_name="00000000.0002.01",
                    classification_ids=["44617100-9"],
                )
                test_required()
            else:
                prepare_tender_state(
                    template_name="00000000.0002.01",
                    classification_ids=["44617100-9"],
                )
                test_not_required()

                prepare_tender_state(
                    template_name=None,
                    classification_ids=["44617100-9"],
                )
                test_after_contract_proforma()

        # Test general template
        prepare_tender_state(
            template_name=None,
            classification_ids=["44617100-9"],
        )
        test_set_invalid_value(
            template_name="invalid_contract_template_name",
            allowed_template_names=["00000000.0002.01", "00000000.0003.01"],
            classification_ids=["44617100-9"],
        )

        # Test inactive template
        prepare_tender_state(
            template_name=None,
            classification_ids=["44617100-9"],
        )
        test_set_invalid_value(
            template_name="00000000.0001.01",  # inactive
            allowed_template_names=["00000000.0002.01", "00000000.0003.01"],
            classification_ids=["44617100-9"],
        )
        # If it's already set, it's allowed to keep it
        prepare_tender_state(
            template_name="00000000.0001.01",  # inactive
            classification_ids=["44617100-9"],
        )
        test_set_valid_value(
            template_name="00000000.0001.01",  # inactive
            extra={"title": uuid4().hex},  # we need to change something to trigger update
        )

        # Test specific template
        prepare_tender_state(
            template_name=None,
            classification_ids=["03221000-6"],
        )
        test_set_invalid_value(
            template_name="invalid_contract_template_name",
            allowed_template_names=["03220000.0001.01"],
            classification_ids=["03221000-6"],
        )
        test_set_invalid_value(
            template_name="00000000.0003.01",
            allowed_template_names=["03220000.0001.01"],
            classification_ids=["03221000-6"],
        )
        test_set_valid_value(
            template_name="03220000.0001.01",
        )

        # Test post contract proforma document forbidden
        prepare_tender_state(
            template_name="03220000.0001.01",
            classification_ids=["03221000-6"],
        )
        test_contract_proforma()

        # Test no template
        prepare_tender_state(
            template_name=None,
            classification_ids=["09310000-5"],
        )
        test_no_template(
            classification_ids=["09310000-5"],
        )

        # Test detailed
        # Example:
        # 03221113-1 (0322)
        # 03222111-4 (03222)
        # 03222111-4 (03222)
        # Allowed template names:
        # 03220000.0001.01
        prepare_tender_state(
            template_name=None,
            classification_ids=["03221113-1", "03222111-4", "03222111-4"],
        )
        test_set_valid_value(
            template_name="03220000.0001.01",
        )
        test_set_invalid_value(
            template_name="03222000.0001.01",
            allowed_template_names=["03220000.0001.01"],
            classification_ids=["03221113-1", "03222111-4"],
        )
        # Example:
        # 03221113-1 (0322)
        # Allowed template names:
        # 03220000.0001.01
        prepare_tender_state(
            template_name=None,
            classification_ids=["03221113-1"],
        )
        test_set_valid_value(
            template_name="03220000.0001.01",
        )
        test_set_invalid_value(
            template_name="03222000.0001.01",
            allowed_template_names=["03220000.0001.01"],
            classification_ids=["03221113-1"],
        )
        # Example:
        # 03222111-4 (03222)
        # Allowed template names:
        # 03220000.0001.01
        # 03222000.0001.01
        prepare_tender_state(
            template_name=None,
            classification_ids=["03222111-4"],
        )
        test_set_valid_value(
            template_name="03220000.0001.01",
        )
        test_set_valid_value(
            template_name="03222000.0001.01",
        )


def set_procuring_entity_signer_info(self):
    tender_data = deepcopy(self.initial_data)
    tender_data["contractTemplateName"] = "00000000.0002.01"
    tender_data["procuringEntity"].pop("signerInfo", None)

    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "procuringEntity",
                "description": {"signerInfo": "This field is required."},
            }
        ],
    )

    tender_data.pop("contractTemplateName", None)

    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertNotIn("signerInfo", response.json["data"]["procuringEntity"])
    tender_id = response.json["data"]["id"]
    tender_token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={tender_token}",
        {
            "data": {
                "contractTemplateName": "00000000.0002.01",
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "procuringEntity",
                "description": {"signerInfo": "This field is required."},
            }
        ],
    )

    tender_data["procuringEntity"]["signerInfo"] = test_signer_info

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={tender_token}",
        {
            "data": {
                "contractTemplateName": "00000000.0002.01",
                "procuringEntity": tender_data["procuringEntity"],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["procuringEntity"]["signerInfo"], test_signer_info)


def set_buyers_signer_info(self):
    tender_data = deepcopy(self.initial_data)
    tender_data["contractTemplateName"] = "00000000.0002.01"
    tender_data["procuringEntity"].pop("signerInfo", None)

    buyer = deepcopy(test_tender_below_buyer)
    buyer["id"] = uuid4().hex
    buyer.pop("signerInfo", None)

    tender_data["buyers"] = [buyer]
    tender_data["items"][0]["relatedBuyer"] = buyer["id"]

    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "buyers.0",
                "description": {"signerInfo": "This field is required."},
            }
        ],
    )

    tender_data.pop("contractTemplateName", None)

    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertNotIn("signerInfo", response.json["data"]["procuringEntity"])
    tender_id = response.json["data"]["id"]
    tender_token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={tender_token}",
        {
            "data": {
                "contractTemplateName": "00000000.0002.01",
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "buyers.0",
                "description": {"signerInfo": "This field is required."},
            }
        ],
    )

    tender_data["buyers"][0]["signerInfo"] = test_signer_info

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={tender_token}",
        {
            "data": {
                "contractTemplateName": "00000000.0002.01",
                "buyers": tender_data["buyers"],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["buyers"][0]["signerInfo"], test_signer_info)


def set_procuring_entity_contract_owner(self):
    tender_data = deepcopy(self.initial_data)
    tender_data.pop("contractTemplateName", None)
    tender_data["procuringEntity"]["contract_owner"] = "test"

    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "procuringEntity",
                "description": {"contract_owner": "could be set only along with signerInfo and contractTemplateName"},
            }
        ],
    )

    tender_data["contractTemplateName"] = "00000000.0002.01"
    tender_data["procuringEntity"]["signerInfo"] = test_signer_info

    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "procuringEntity",
                "description": {"contract_owner": "should be one of brokers with level 6"},
            }
        ],
    )

    tender_data["procuringEntity"].pop("contract_owner")
    with mock.patch(
        "openprocurement.tender.core.procedure.validation.CONTRACT_OWNER_REQUIRED_FROM", get_now() - timedelta(days=1)
    ):
        response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
        self.assertEqual(
            response.json["errors"],
            [
                {
                    "location": "body",
                    "name": "procuringEntity",
                    "description": {"contract_owner": "This field is required."},
                }
            ],
        )

    tender_data["procuringEntity"]["contract_owner"] = "broker"
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["procuringEntity"]["contract_owner"], "broker")

    buyer = deepcopy(test_tender_below_buyer)
    buyer["id"] = uuid4().hex
    buyer["contract_owner"] = "broker"

    tender_data["buyers"] = [buyer]
    tender_data["items"][0]["relatedBuyer"] = buyer["id"]
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["buyers"][0]["contract_owner"], "broker")
