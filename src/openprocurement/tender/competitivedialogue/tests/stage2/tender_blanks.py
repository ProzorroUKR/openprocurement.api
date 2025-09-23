from copy import deepcopy
from datetime import timedelta
from unittest import mock

from freezegun import freeze_time

from openprocurement.api.constants import ROUTE_PREFIX, TZ
from openprocurement.api.constants_env import RELEASE_2020_04_19
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_base_organization,
    test_tender_below_cancellation,
)
from openprocurement.tender.belowthreshold.tests.tender_blanks import (
    create_tender_central as create_tender_central_base,
)
from openprocurement.tender.competitivedialogue.constants import STAGE2_STATUS
from openprocurement.tender.core.procedure.utils import dt_from_iso
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_with_complaints_after_2020_04_19,
)
from openprocurement.tender.core.tests.criteria_utils import add_criteria
from openprocurement.tender.core.tests.utils import (
    activate_contract,
    change_auth,
    set_bid_items,
)
from openprocurement.tender.core.utils import calculate_tender_full_date


# CompetitiveDialogStage2EUResourceTest
@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_criteria_rules",
    mock.Mock(return_value={}),
)
def patch_tender_eu(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.tender_id = tender["id"]
    self.set_enquiry_period_end()

    self.app.authorization = ("Basic", ("broker", ""))
    items = deepcopy(tender["items"])
    items[0]["deliveryDate"]["startDate"] = get_now().isoformat()
    items[0]["deliveryDate"]["endDate"] = (get_now() + timedelta(days=2)).isoformat()
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": items}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "tenderPeriod should be extended by 7 days")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    tender = response.json["data"]
    tender_period_end_date = (
        calculate_tender_full_date(
            get_now(),
            timedelta(days=7),
            tender=tender,
        )
        + timedelta(seconds=1)
    ).astimezone(TZ)
    enquiry_period_end_date = calculate_tender_full_date(
        tender_period_end_date,
        -timedelta(days=10),
        tender=tender,
    )
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "items": items,
                "tenderPeriod": {
                    "startDate": tender["tenderPeriod"]["startDate"],
                    "endDate": tender_period_end_date.isoformat(),
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["tenderPeriod"]["endDate"], tender_period_end_date.isoformat())
    self.assertEqual(response.json["data"]["enquiryPeriod"]["endDate"], enquiry_period_end_date.isoformat())


# TenderStage2UAResourceTest
def empty_listing_ua(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertNotIn('{\n    "', response.body.decode())
    self.assertNotIn("callback({", response.body.decode())
    self.assertEqual(response.json["next_page"]["offset"], "")
    self.assertNotIn("prev_page", response.json)

    response = self.app.get("/tenders?opt_jsonp=callback")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertNotIn('{\n    "', response.body.decode())
    self.assertIn("callback({", response.body.decode())

    response = self.app.get("/tenders?opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body.decode())
    self.assertNotIn("callback({", response.body.decode())

    response = self.app.get("/tenders?opt_jsonp=callback&opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('{\n    "', response.body.decode())
    self.assertIn("callback({", response.body.decode())

    response = self.app.get("/tenders?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertIn("descending=1", response.json["next_page"]["uri"])
    self.assertIn("limit=10", response.json["next_page"]["uri"])
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertIn("limit=10", response.json["prev_page"]["uri"])

    response = self.app.get("/tenders?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertEqual(response.json["next_page"]["offset"], "")
    self.assertNotIn("prev_page", response.json)

    response = self.app.get("/tenders?feed=changes&offset=0", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Offset expired/invalid", "location": "url", "name": "offset"}],
    )

    response = self.app.get("/tenders?feed=changes&descending=1&limit=10")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertIn("descending=1", response.json["next_page"]["uri"])
    self.assertIn("limit=10", response.json["next_page"]["uri"])
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertIn("limit=10", response.json["prev_page"]["uri"])


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_criteria_rules",
    mock.Mock(return_value={}),
)
def patch_tender_ua(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.tender_id = tender["id"]
    self.set_status("active.tendering")
    self.set_enquiry_period_end()
    self.app.get("/tenders/{}?acc_token={}".format(tender["id"], owner_token))
    self.app.authorization = ("Basic", ("broker", ""))
    items = deepcopy(tender["items"])
    items[0]["deliveryDate"]["startDate"] = get_now().isoformat()
    items[0]["deliveryDate"]["endDate"] = (get_now() + timedelta(days=2)).isoformat()
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": items}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")

    self.assertEqual(response.json["errors"][0]["description"], "tenderPeriod should be extended by 7 days")
    tender_period_end_date = (
        calculate_tender_full_date(
            get_now(),
            timedelta(days=7),
            tender=tender,
        )
        + timedelta(seconds=1)
    ).astimezone(TZ)
    enquiry_period_end_date = calculate_tender_full_date(
        tender_period_end_date,
        -timedelta(days=10),
        tender=tender,
    )

    response = self.app.get("/tenders/{}?acc_token={}".format(tender["id"], owner_token))
    tender = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "items": items,
                "tenderPeriod": {
                    "endDate": tender_period_end_date.isoformat(),
                    "startDate": tender["tenderPeriod"]["startDate"],
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["tenderPeriod"]["endDate"], tender_period_end_date.isoformat())
    self.assertEqual(response.json["data"]["enquiryPeriod"]["endDate"], enquiry_period_end_date.isoformat())


def create_tender_invalid_config(self):
    self.app.authorization = ("Basic", ("token", ""))
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
        [{"description": "0 is less than the minimum of 2", "location": "body", "name": "config.minBidsNumber"}],
    )
    config.update({"minBidsNumber": 3})
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
        [{"description": "3 is greater than the maximum of 2", "location": "body", "name": "config.minBidsNumber"}],
    )


# CompetitiveDialogStage2ResourceTest
def listing(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []
    tokens = []

    for i in range(3):
        response = self.app.post_json(
            "/tenders",
            {
                "data": self.initial_data,
                "config": self.initial_config,
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        tenders.append(response.json["data"])
        tokens.append(response.json["access"]["token"])

    # set status to draft.stage2
    for tender in tenders:
        self.set_tender_status(tender, tokens[tenders.index(tender)], "draft.stage2")

    # set status to active.tendering
    for tender in tenders:
        offset = get_now().timestamp()
        response = self.set_tender_status(tender, tokens[tenders.index(tender)], "active.tendering")
        tenders[tenders.index(tender)] = response.json["data"]

    ids = ",".join([i["id"] for i in tenders])

    response = self.app.get("/tenders")
    self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))

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

    test_tender_data_2 = self.initial_data.copy()
    test_tender_data_2["mode"] = "test"
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders",
        {
            "data": test_tender_data_2,
            "config": self.initial_config,
        },
    )
    self.set_tender_status(response.json["data"], response.json["access"]["token"], "draft.stage2")
    self.set_tender_status(response.json["data"], response.json["access"]["token"], "active.tendering")
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/tenders?mode=test")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def listing_draft(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []
    data = self.initial_data.copy()
    data.update({"status": "draft"})

    for i in range(3):
        response = self.app.post_json(
            "/tenders",
            {
                "data": data,
                "config": self.initial_config,
            },
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.set_tender_status(response.json["data"], response.json["access"]["token"], "draft.stage2")
        response = self.set_tender_status(response.json["data"], response.json["access"]["token"], "active.tendering")
        tenders.append(response.json["data"])
        response = self.app.post_json(
            "/tenders",
            {
                "data": data,
                "config": self.initial_config,
            },
        )
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


def tender_not_found(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.get("/tenders/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    self.app.authorization = ("Basic", ("broker", ""))

    response = self.app.patch_json("/tenders/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


def invalid_procurementMethod(self):
    """Edit field procurementMethod second stage"""
    self.app.authorization = ("Basic", ("token", ""))
    data = deepcopy(self.initial_data)
    del data["procurementMethod"]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(response.json["data"]["procurementMethod"], "selective")

    add_criteria(self, tender["id"], token)
    self.set_tender_status(tender, token, "draft.stage2")
    # Try edit
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"procurementMethod": "open", "status": "active.tendering"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "procurementMethod", "description": "Field change's not allowed"}],
    )


def listing_changes(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []
    tokens = []

    for i in range(3):
        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        token = response.json["access"]["token"]
        data = response.json["data"]
        self.set_tender_status(data, token, "draft.stage2")
        data = self.set_tender_status(data, token, "active.tendering").json["data"]
        tenders.append(data)
        tokens.append(token)

    ids = ",".join([i["id"] for i in tenders])

    while True:
        response = self.app.get("/tenders?feed=changes")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

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

    test_tender_stage2_data_eu2 = self.initial_data.copy()
    test_tender_stage2_data_eu2["mode"] = "test"
    response = self.app.post_json("/tenders", {"data": test_tender_stage2_data_eu2, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.set_tender_status(response.json["data"], response.json["access"]["token"], "draft.stage2")
    self.set_tender_status(response.json["data"], response.json["access"]["token"], "active.tendering")

    while True:
        response = self.app.get("/tenders?feed=changes&mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?feed=changes&mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def create_tender(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)
    initial_data = deepcopy(self.initial_data)
    response = self.app.post_json("/tenders", {"data": initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    tender_set = set(tender)
    if "procurementMethodDetails" in tender_set:
        tender_set.remove("procurementMethodDetails")
    self.assertEqual(
        tender_set - set(self.initial_data),
        {
            "id",
            "dateModified",
            "dateCreated",
            "enquiryPeriod",
            "complaintPeriod",
            "awardCriteria",
            "submissionMethod",
            "date",
        },
    )
    self.assertIn(tender["id"], response.headers["Location"])
    self.assertEqual(tender["tenderID"], self.initial_data["tenderID"])

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


def tender_features_invalid(self):
    self.app.authorization = ("Basic", ("token", ""))
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
            "enum": [
                {"value": 0.1, "title": "До 1000 Вт"},
                {"value": 0.15, "title": "Більше 1000 Вт"},
                {"value": 0.3, "title": "До 500 Вт"},
            ],
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
    data["features"][0]["enum"][0]["value"] = 1.0
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"enum": [{"value": ["Float value should be less than 0.99."]}]}],
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
    copy_data = deepcopy(data)
    copy_data["features"][1]["code"] = "OCDS-123454-YEARS"
    copy_data["features"][1]["enum"][0]["value"] = 0.5
    feature = deepcopy(copy_data["features"][1])
    feature["code"] = "OCDS-123455-YEARS"
    copy_data["features"].append(feature)
    feature = deepcopy(copy_data["features"][1])
    feature["code"] = "OCDS-123456-YEARS"
    copy_data["features"].append(feature)
    response = self.app.post_json("/tenders", {"data": copy_data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Sum of max value of all features for lot should be less then or equal to 99%"],
                "location": "body",
                "name": "features",
            }
        ],
    )
    del copy_data
    del feature


def get_tender(self):
    self.app.authorization = ("Basic", ("token", ""))
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


def create_tender_with_non_required_unit(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)
    tender_data = deepcopy(self.initial_data)

    _unit = tender_data["items"][0].pop("unit")
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("unit", response.json["data"]['items'][0])

    _quantity = tender_data["items"][0].pop("quantity")
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("quantity", response.json["data"]['items'][0])
    self.assertNotIn("unit", response.json["data"]['items'][0])

    tender_data["items"][0]["unit"] = _unit
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


def tender_features(self):
    self.app.authorization = ("Basic", ("token", ""))
    data = self.initial_data.copy()
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
    self.assertEqual(tender["features"], data["features"])
    token = response.json["access"]["token"]
    self.tender_id = response.json["data"]["id"]
    # switch to draft.stage2
    self.set_status(STAGE2_STATUS)
    response = self.app.get("/tenders/{}?acc_token={}".format(tender["id"], token))
    self.assertEqual(response.status, "200 OK")
    self.assertIn("features", response.json["data"])


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.get_criteria_rules",
    mock.Mock(return_value={}),
)
def patch_tender_1(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "draft")
    self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    self.set_status(STAGE2_STATUS)

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/credentials?acc_token={}".format(tender["id"], owner_token), {"data": ""}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        "/tenders/{}/credentials?acc_token={}".format(tender["id"], self.test_access_token_data), {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")

    owner_token = response.json["access"]["token"]

    # switch to active.tendering
    self.set_status("active.tendering")
    tender["status"] = "active.tendering"

    response = self.app.get(f"/tenders/{tender['id']}")
    items = deepcopy(response.json["data"]["items"])

    pq_entity = deepcopy(response.json["data"]["procuringEntity"])
    pq_entity["kind"] = "defense"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": pq_entity}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "procuringEntity", "description": "Field change's not allowed"}],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [items[0]]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)
    tender_items = response.json["data"]["items"]

    items = deepcopy(tender_items)
    items[0]["classification"] = {
        "scheme": "CPV",
        "id": "55523100-3",
        "description": "Послуги з харчування у школах",
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": items}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "items.classification", "description": "Field change's not allowed"}],
    )

    deliveryDateStart = (get_now() + timedelta(days=10)).isoformat()
    deliveryDateEnd = (get_now() + timedelta(days=15)).isoformat()

    updates = {
        "description": "Шолом Дарта Вейдера",
        "unit": {"name": "item", "code": "KWT"},
        "quantity": 3,
        "deliveryAddress": {
            "countryName": "Україна",
            "postalCode": "49000",
            "region": "Дніпропетровська область",
            "locality": "м. Дніпро",
            "streetAddress": "вул. Нютона 4",
        },
    }

    for k, v in updates.items():
        item = deepcopy(tender_items[0])
        item[k] = v
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"items": [item]}}, status=422
        )
        self.assertEqual(
            response.json["errors"],
            [{"location": "body", "name": f"items.{k}", "description": "Field change's not allowed"}],
        )

    item = deepcopy(tender_items[0])
    item["deliveryDate"] = {"startDate": deliveryDateStart, "endDate": deliveryDateEnd}
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"items": [item]}}
    )
    self.assertEqual(response.json["data"]["items"][0]["deliveryDate"]["startDate"], deliveryDateStart)
    self.assertEqual(response.json["data"]["items"][0]["deliveryDate"]["endDate"], deliveryDateEnd)

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.auction"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


def dateModified_tender(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")

    self.tender_id = response.json["data"]["id"]
    # switch to active.tendering
    self.set_status("active.tendering")

    tender = response.json["data"]
    dateModified = tender["dateModified"]
    owner_token = response.json["access"]["token"]

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["dateModified"], dateModified)


def guarantee(self):
    self.app.authorization = ("Basic", ("token", ""))
    data = deepcopy(self.initial_data)
    data["guarantee"] = {"amount": 55}
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertIn("guarantee", response.json["data"])
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.tender_id = response.json["data"]["id"]
    # switch to active.tendering
    self.set_status("active.tendering")
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"amount": 70, "currency": "UAH"}}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "guarantee", "description": "Field change's not allowed"}],
    )


def tender_Administrator_change(self):
    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]

    self.set_tender_status(tender, response.json["access"]["token"], "draft.stage2")
    response = self.set_tender_status(tender, response.json["access"]["token"], "active.tendering")

    tender = response.json["data"]

    self.app.authorization = ("Basic", ("broker", ""))
    tender_db = self.mongodb.tenders.get(tender["id"])
    identifier = tender_db["shortlistedFirms"][0]["identifier"]
    self.test_bids_data[0]["tenderers"][0]["identifier"]["id"] = identifier["id"]
    self.test_bids_data[0]["tenderers"][0]["identifier"]["scheme"] = identifier["scheme"]
    enquiry_period_start = dt_from_iso(tender["enquiryPeriod"]["startDate"])
    with freeze_time(enquiry_period_start.isoformat()):
        response = self.app.post_json(
            "/tenders/{}/questions".format(tender["id"]),
            {"data": {"title": "question title", "description": "question description", "author": self.author_data}},
        )
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
    question = response.json["data"]

    pq_entity = deepcopy(tender["procuringEntity"])
    pq_entity["identifier"]["id"] = "00000000"
    with change_auth(self.app, ("Basic", ("administrator", ""))):
        response = self.app.patch_json(
            "/tenders/{}".format(tender["id"]),
            {"data": {"procuringEntity": pq_entity}},
        )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["procuringEntity"]["identifier"]["id"], "00000000")

    with change_auth(self.app, ("Basic", ("administrator", ""))):
        response = self.app.patch_json(
            "/tenders/{}/questions/{}".format(tender["id"], question["id"]), {"data": {"answer": "answer"}}, status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"], [{"location": "url", "name": "permission", "description": "Forbidden"}]
        )

    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.tender_id = tender["id"]
    owner_token = self.tender_token = response.json["access"]["token"]

    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if RELEASE_2020_04_19 < get_now() and set_complaint_period_end:
        set_complaint_period_end()

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender["id"], owner_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    cancellation_id = response.json["data"]["id"]
    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id)


def patch_not_author(self):
    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]

    self.set_tender_status(tender, response.json["access"]["token"], "draft.stage2")
    response = self.set_tender_status(tender, response.json["access"]["token"], "active.tendering")

    tender = response.json["data"]

    self.app.authorization = ("Basic", ("bot", "bot"))

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
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/documents/{}?acc_token={}".format(tender["id"], doc_id, owner_token),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only author")


# TenderStage2UAProcessTest
def invalid_tender_conditions(self):
    # self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])

    with change_auth(self.app, ("Basic", ("token", ""))):
        response = self.app.post_json("/tenders", {"data": self.test_tender_data_ua, "config": self.initial_config})
        tender_id = self.tender_id = response.json["data"]["id"]
        owner_token = self.tender_token = response.json["access"]["token"]
    # switch to active.tendering
    self.set_status("active.tendering")
    # cancellation
    set_complaint_period_end = getattr(self, "set_complaint_period_end", None)
    if RELEASE_2020_04_19 < get_now() and set_complaint_period_end:
        set_complaint_period_end()

    cancellation = deepcopy(test_tender_below_cancellation)
    cancellation.update({"reason": "invalid conditions", "status": "active"})
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]
    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_with_complaints_after_2020_04_19(self, cancellation_id, tender_id, owner_token)
    # check status
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def one_valid_bid_tender_ua(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json("/tenders", {"data": self.test_tender_data_ua, "config": self.initial_config})
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    self.app.authorization = ("Basic", ("broker", ""))
    # switch to active.tendering XXX temporary action.
    response = self.set_status(
        "active.tendering", {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
    )
    self.assertIn("auctionPeriod", response.json["data"])

    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    tender_db = self.mongodb.tenders.get(tender["id"])
    identifier = tender_db["shortlistedFirms"][0]["identifier"]
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["tenderers"][0]["identifier"]["id"] = identifier["id"]
    bid_data["tenderers"][0]["identifier"]["scheme"] = identifier["scheme"]
    bid_data["value"] = {"amount": 500}
    set_bid_items(self, bid_data)

    self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )

    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotEqual(response.json["data"]["date"], tender["date"])


def one_invalid_and_1draft_bids_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json("/tenders", {"data": self.test_tender_data_ua, "config": self.initial_config})
    tender = response.json["data"]
    tender_id = self.tender_id = tender["id"]
    self.set_status("active.tendering")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    tender_db = self.mongodb.tenders.get(tender["id"])
    identifier = tender_db["shortlistedFirms"][0]["identifier"]
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["tenderers"][0]["identifier"]["id"] = identifier["id"]
    bid_data["tenderers"][0]["identifier"]["scheme"] = identifier["scheme"]
    bid_data["value"] = {"amount": 500}
    set_bid_items(self, bid_data)

    self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )

    bid_data["status"] = "draft"
    self.app.authorization = ("Basic", ("broker", ""))
    self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )
    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    response = self.check_chronograph()
    # get awards
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def first_bid_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json("/tenders", {"data": self.test_tender_data_ua, "config": self.initial_config})
    tender = response.json["data"]
    tender_id = self.tender_id = tender["id"]
    owner_token = response.json["access"]["token"]
    # switch to active.tendering
    self.set_status("active.tendering")
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    tender_db = self.mongodb.tenders.get(tender["id"])
    identifier = tender_db["shortlistedFirms"][0]["identifier"]
    bid_data = deepcopy(self.test_bids_data[0])
    del bid_data["value"]
    bid_data["tenderers"][0]["identifier"]["id"] = identifier["id"]
    bid_data["tenderers"][0]["identifier"]["scheme"] = identifier["scheme"]
    bid_data["value"] = {"amount": 450}

    bid, bid1_token = self.create_bid(tender_id, bid_data)
    bid_id = bid["id"]
    # create second bid
    bid_data["value"] = {"amount": 475}

    self.app.authorization = ("Basic", ("broker", ""))
    _, bid2_token = self.create_bid(tender_id, bid_data)
    # switch to active.auction
    self.set_status("active.auction", {"status": "active.tendering"})
    response = self.check_chronograph()

    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = [{"id": b["id"], "value": b["value"]} for b in response.json["data"]["bids"]]
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
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid1_token))
    self.assertEqual(response.json["data"]["participationUrl"], "https://tender.auction.url/for_bid/{}".format(bid_id))

    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    self.app.post_json("/tenders/{}/auction".format(tender_id), {"data": {"bids": auction_bids_data}})
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as unsuccessful
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful", "qualified": False, "eligible": False}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award2_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    self.assertNotEqual(award_id, award2_id)
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.add_sign_doc(tender_id, owner_token, docs_url=f"/awards/{award_id}/documents")
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
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
    activate_contract(self, tender_id, contract_id, owner_token, bid2_token)
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def tender_milestones_not_required(self):
    data = deepcopy(self.initial_data)
    self.app.authorization = ("Basic", ("token", ""))
    data["milestones"] = []

    self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=201)


def create_tender_central(self):
    with change_auth(self.app, ("Basic", ("token", ""))):
        create_tender_central_base(self)
