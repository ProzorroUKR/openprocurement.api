from copy import deepcopy
from datetime import datetime, timedelta
from unittest import mock

import requests
from jsonschema import validate

from openprocurement.api.constants import TZ
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
    test_tender_below_lots,
)
from openprocurement.tender.belowthreshold.tests.utils import activate_contract
from openprocurement.tender.core.tests.base import (
    test_exclusion_criteria,
    test_language_criteria,
    test_lcc_lot_criteria,
)
from openprocurement.tender.core.tests.criteria_utils import add_criteria
from openprocurement.tender.core.utils import calculate_tender_full_date
from openprocurement.tender.open.constants import ABOVE_THRESHOLD
from openprocurement.tender.open.tests.base import test_tender_open_data


def empty_listing(self):
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

    offset = datetime.fromisoformat("2015-01-01T00:00:00+02:00").timestamp()
    response = self.app.get(f"/tenders?offset={offset}&descending=1&limit=10")
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

    response = self.app.get("/tenders?feed=changes&offset=latest", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Invalid offset provided: latest", "location": "querystring", "name": "offset"}],
    )


def create_tender_invalid(self):
    request_path = "/tenders"
    self.app.post_json(request_path, {"data": {}}, status=404)

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

    self.app.post_json(request_path, {"data": {"procurementMethodType": "invalid_value"}}, status=404)

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": ABOVE_THRESHOLD, "invalid_field": "invalid_value"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": ABOVE_THRESHOLD, "value": "invalid_value"}}, status=422
    )
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

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": ABOVE_THRESHOLD, "procurementMethod": "invalid_value"}},
        status=422,
    )
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
        {"description": ["This field is required."], "location": "body", "name": "value"}, response.json["errors"]
    )
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "items"}, response.json["errors"]
    )

    response = self.app.post_json(
        request_path,
        {"data": {"procurementMethodType": ABOVE_THRESHOLD, "enquiryPeriod": {"endDate": "invalid_value"}}},
        status=422,
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
                "name": "enquiryPeriod",
            }
        ],
    )

    response = self.app.post_json(
        request_path,
        {
            "data": {
                "procurementMethodType": ABOVE_THRESHOLD,
                "enquiryPeriod": {"endDate": "9999-12-31T23:59:59.999999"},
            }
        },
        status=422,
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

    self.initial_data["tenderPeriod"]["startDate"] = (get_now() - timedelta(minutes=30)).isoformat()
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    del self.initial_data["tenderPeriod"]["startDate"]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["tenderPeriod.startDate should be in greater than current date"],
                "location": "body",
                "name": "tenderPeriod",
            }
        ],
    )

    now = get_now()
    self.initial_data["awardPeriod"] = {"startDate": now.isoformat(), "endDate": now.isoformat()}
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    del self.initial_data["awardPeriod"]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["period should begin after tenderPeriod"], "location": "body", "name": "awardPeriod"}],
    )

    self.initial_data["auctionPeriod"] = {
        "startDate": (now + timedelta(days=16)).isoformat(),
        "endDate": (now + timedelta(days=16)).isoformat(),
    }
    self.initial_data["awardPeriod"] = {
        "startDate": (now + timedelta(days=15)).isoformat(),
        "endDate": (now + timedelta(days=15)).isoformat(),
    }
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    del self.initial_data["auctionPeriod"]
    del self.initial_data["awardPeriod"]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["period should begin after auctionPeriod"], "location": "body", "name": "awardPeriod"}],
    )

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
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

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
    self.initial_data["items"] = [self.initial_data["items"][0], data]
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["items"] = self.initial_data["items"][:1]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["CPV class of items should be identical"], "location": "body", "name": "items"}],
    )

    data = deepcopy(self.initial_data)
    del data["items"][0]["deliveryDate"]["endDate"]
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"deliveryDate": {"endDate": ["This field is required."]}}],
                "location": "body",
                "name": "items",
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
        [{"description": "0 is less than the minimum of 1", "location": "body", "name": "minBidsNumber"}],
    )
    config.update({"minBidsNumber": 2})
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
        [{"description": "2 is greater than the maximum of 1", "location": "body", "name": "minBidsNumber"}],
    )


def create_tender_generated(self):
    data = self.initial_data.copy()
    data.update({"id": "hash"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    if "procurementMethodDetails" in tender:
        tender.pop("procurementMethodDetails")
    fields = [
        "procurementMethodType",
        "id",
        "dateModified",
        "dateCreated",
        "tenderID",
        "status",
        "enquiryPeriod",
        "tenderPeriod",
        "complaintPeriod",
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
        "date",
        "mainProcurementCategory",
        "milestones",
        "documents",
        "noticePublicationDate",
    ]
    if tender["procurementMethodType"] not in ("aboveThresholdUA.defense", "simple.defense"):
        fields.append("criteria")
    if self.initial_lots:
        fields.append("lots")
    else:
        fields.append("auctionPeriod")
    self.assertEqual(set(tender), set(fields))
    self.assertNotEqual(data["id"], tender["id"])


def tender_fields(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    self.tender_id = tender["id"]
    tender_set = set(tender)
    if "procurementMethodDetails" in tender_set:
        tender_set.remove("procurementMethodDetails")

    difference = tender_set - set(self.initial_data)
    difference -= {"auctionPeriod"}  # openeu
    self.assertEqual(
        difference,
        {
            "id",
            "dateModified",
            "dateCreated",
            "enquiryPeriod",
            "complaintPeriod",
            "criteria",
            "tenderID",
            "status",
            "procurementMethod",
            "awardCriteria",
            "submissionMethod",
            "next_check",
            "owner",
            "date",
            "documents",
            "noticePublicationDate",
        },
    )

    self.set_status("complete")
    self.check_chronograph()

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "complete")
    expected_keys = {
        "id",
        "dateCreated",
        "dateModified",
        "enquiryPeriod",
        "auctionPeriod",
        "complaintPeriod",
        "criteria",
        "tenderID",
        "status",
        "procurementMethod",
        "awardCriteria",
        "submissionMethod",
        "owner",
        "date",
        "awardPeriod",
        "documents",
        "noticePublicationDate",
    }
    self.assertEqual(set(tender.keys()) - set(self.initial_data.keys()), expected_keys)


def patch_draft_invalid_json(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    response = self.app.patch(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), "{}d", content_type="application/json", status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Extra data: line 1 column 3 (char 2)",
            }
        ],
    )


def patch_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    dateModified = tender.pop("dateModified")

    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "cancelled"}}, status=422
    )

    procuring_entity = deepcopy(tender["procuringEntity"])
    procuring_entity["kind"] = "defense"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": procuring_entity}},
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

    tender_period = deepcopy(tender["tenderPeriod"])
    tender_period["startDate"] = tender["enquiryPeriod"]["endDate"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"tenderPeriod": tender_period}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "tenderPeriod",
                "description": ["tenderPeriod must be at least 7 full calendar days long"],
            }
        ],
    )
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"procurementMethodRationale": "Open"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("invalidationDate", response.json["data"]["enquiryPeriod"])
    new_tender = response.json["data"]
    new_enquiryPeriod = new_tender.pop("enquiryPeriod")
    new_dateModified = new_tender.pop("dateModified")
    tender.pop("enquiryPeriod")
    tender["procurementMethodRationale"] = "Open"
    self.assertEqual(tender, new_tender)
    self.assertNotEqual(dateModified, new_dateModified)

    revisions = self.mongodb.tenders.get(tender["id"]).get("revisions")
    self.assertTrue(
        any(i for i in revisions[-1]["changes"] if i["op"] == "remove" and i["path"] == "/procurementMethodRationale")
    )

    # update again
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procurementMethodRationale": "OpenOpen"}},
    )
    new_tender2 = response.json["data"]
    new_enquiryPeriod2 = new_tender2.pop("enquiryPeriod")
    new_dateModified2 = new_tender2.pop("dateModified")
    new_tender.pop("procurementMethodRationale")
    new_tender2.pop("procurementMethodRationale")
    self.assertEqual(new_tender, new_tender2)
    self.assertNotEqual(new_enquiryPeriod, new_enquiryPeriod2)
    self.assertNotEqual(new_dateModified, new_dateModified2)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"dateModified": new_dateModified}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "dateModified", "description": "Rogue field"}]
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [self.initial_data["items"][0]]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [self.initial_data["items"][0], self.initial_data["items"][0]]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    item0 = response.json["data"]["items"][0]
    item1 = response.json["data"]["items"][1]
    self.assertNotEqual(item0.pop("id"), item1.pop("id"))
    self.assertEqual(item0, item1)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [self.initial_data["items"][0]]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)

    item = deepcopy(self.initial_data["items"][0])
    item["classification"] = {"scheme": "ДК021", "id": "44620000-2", "description": "Cartons 2"}
    self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
        status=200,
    )

    item["classification"] = {
        "scheme": "ДК021",
        "id": "55523100-3",
        "description": "Послуги з харчування у школах",
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0],
        {"description": ["Can't change classification group of items"], "location": "body", "name": "items"},
    )

    item = deepcopy(self.initial_data["items"][0])
    item["additionalClassifications"] = [tender["items"][0]["additionalClassifications"][0] for i in range(3)]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    item = deepcopy(self.initial_data["items"][0])
    item["additionalClassifications"] = tender["items"][0]["additionalClassifications"]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [item]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    period = {
        "startDate": calculate_tender_full_date(
            parse_date(new_dateModified2),
            -timedelta(3),
            tender=None,
            working_days=True,
        ).isoformat(),
        "endDate": new_dateModified2,
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"enquiryPeriod": period}},
    )
    result = response.json["data"]
    self.assertNotEqual(period["startDate"], result["enquiryPeriod"]["startDate"])
    self.assertNotEqual(period["endDate"], result["enquiryPeriod"]["endDate"])
    self.assertEqual(tender["enquiryPeriod"]["startDate"], result["enquiryPeriod"]["startDate"])
    self.assertEqual(tender["enquiryPeriod"]["endDate"], result["enquiryPeriod"]["endDate"])

    # set lots
    base_value = result["value"]
    base_currency, base_tax = base_value["currency"], base_value["valueAddedTaxIncluded"]
    for lot in test_tender_below_lots:
        response = self.app.post_json(f"/tenders/{tender['id']}/lots?acc_token={owner_token}", {"data": lot})
        self.assertEqual(response.status, "201 Created")
        lot_data = response.json["data"]
        self.assertEqual(lot_data["value"]["currency"], base_currency)
        self.assertEqual(lot_data["value"]["valueAddedTaxIncluded"], base_tax)

    changed_value = deepcopy(base_value)
    changed_value["valueAddedTaxIncluded"] = not base_tax
    changed_value["currency"] = "GBP"
    minimal_step = {"amount": result["minimalStep"]["amount"], "currency": "GBP", "valueAddedTaxIncluded": not base_tax}
    response = self.app.patch_json(
        f"/tenders/{tender['id']}?acc_token={owner_token}",
        {
            "data": {
                "value": changed_value,
                "minimalStep": minimal_step,
            }
        },
    )
    result = response.json["data"]
    new_value = result["value"]

    self.assertEqual(changed_value["currency"], new_value["currency"])
    self.assertEqual(changed_value["valueAddedTaxIncluded"], new_value["valueAddedTaxIncluded"])

    for lot in result["lots"]:
        self.assertEqual(lot["value"]["currency"], new_value["currency"])
        self.assertEqual(lot["value"]["valueAddedTaxIncluded"], new_value["valueAddedTaxIncluded"])

    self.set_status("complete")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active.auction"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


def patch_tender_period(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.tender_id, self.tender_token = tender["id"], response.json["access"]["token"]

    add_criteria(self)
    self.set_enquiry_period_end()  # sets tenderPeriod.startDate in the past, be careful
    response = self.app.get(f"/tenders/{tender['id']}")
    tender = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], self.tender_token),
        {"data": {"description": "new description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "tenderPeriod should be extended by 4 days")

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
        -timedelta(days=3),
        tender=tender,
    )
    tender_period = deepcopy(tender["tenderPeriod"])
    tender_period["endDate"] = tender_period_end_date.isoformat()
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], self.tender_token),
        {"data": {"description": "new description", "tenderPeriod": tender_period}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["tenderPeriod"]["endDate"], tender_period_end_date.isoformat())
    self.assertEqual(response.json["data"]["enquiryPeriod"]["endDate"], enquiry_period_end_date.isoformat())


def invalid_bid_tender_features(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    data = deepcopy(self.initial_data)
    data["features"] = [
        {
            "code": "OCDS-123454-POSTPONEMENT",
            "featureOf": "tenderer",
            "title": "Відстрочка платежу",
            "description": "Термін відстрочки платежу",
            "enum": [{"value": 0.05, "title": "До 90 днів"}, {"value": 0.1, "title": "Більше 90 днів"}],
        }
    ]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)

    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["parameters"] = [{"code": "OCDS-123454-POSTPONEMENT", "value": 0.1}]
    bid_data["lotValues"][0]["value"] = {"amount": 500}
    bid, bid_token = self.create_bid(tender_id, bid_data)
    bid_id = bid["id"]

    features = deepcopy(tender["features"])
    features[0]["code"] = "OCDS-123-POSTPONEMENT"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"features": features}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("OCDS-123-POSTPONEMENT", response.json["data"]["features"][0]["code"])

    parameters = deepcopy(bid["parameters"])
    parameters[0]["code"] = "OCDS-123-POSTPONEMENT"
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token),
        {"data": {"parameters": parameters, "status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("OCDS-123-POSTPONEMENT", response.json["data"]["parameters"][0]["code"])

    features[0]["enum"][0]["value"] = 0.2
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"features": features}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(0.2, response.json["data"]["features"][0]["enum"][0]["value"])

    parameters[0]["value"] = 0.2
    response = self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token),
        {"data": {"parameters": parameters, "status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual("OCDS-123-POSTPONEMENT", response.json["data"]["parameters"][0]["code"])

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"features": []}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("features", response.json["data"])

    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotEqual(response.json["data"]["date"], tender["date"])


def invalid_bid_tender_lot(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)

    lots = []
    for lot in test_tender_below_lots * 2:
        response = self.app.post_json("/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": lot})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        lots.append(response.json["data"]["id"])

    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data.update(
        {"value": None, "status": "draft", "lotValues": [{"value": {"amount": 500}, "relatedLot": i} for i in lots]}
    )
    bid, bid_token = self.create_bid(tender_id, bid_data)
    bid_id = bid["id"]

    response = self.app.delete("/tenders/{}/lots/{}?acc_token={}".format(tender_id, lots[0], owner_token))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotEqual(response.json["data"]["date"], tender["date"])


def one_valid_bid_tender_ua(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender = response.json["data"]
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # switch to active.tendering XXX temporary action.
    response = self.set_status(
        "active.tendering", {"auctionPeriod": {"startDate": (get_now() + timedelta(days=16)).isoformat()}}
    )
    self.assertIn("auctionPeriod", response.json["data"])

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"][0]["value"] = {"amount": 500}

    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {"data": bid_data},
    )

    bid_id = self.bid_id = response.json["data"]["id"]

    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "unsuccessful")
    self.assertNotEqual(response.json["data"]["date"], tender["date"])


def invalid1_and_1draft_bids_tender(self):
    self.app.authorization = ("Basic", ("broker", ""))
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))

    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"][0]["value"] = {"amount": 500}
    bid, bid_token = self.create_bid(tender_id, bid_data, "draft")

    self.app.authorization = ("Basic", ("broker", ""))
    bid, bid_token = self.create_bid(tender_id, bid_data)

    response = self.app.get(f"/tenders/{self.tender_id}")
    tender = response.json["data"]

    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    response = self.check_chronograph()
    # get awards
    self.assertEqual(response.json["data"]["status"], "active.qualification")


def activate_bid_after_adding_lot(self):
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"][0]["value"] = {"amount": 500}
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid, bid_token = self.create_bid(tender_id, bid_data)
    bid_id = bid["id"]

    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(self.tender_id, owner_token), {"data": test_tender_below_lots[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    lot_id = response.json["data"]["id"]

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))

    self.app.patch_json(
        "/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token),
        {
            "data": {
                "status": "pending",
                "value": None,
                "lotValues": [
                    {
                        "value": {"amount": 500},
                        "relatedLot": lot_id,
                        "status": "pending",
                    }
                ],
            }
        },
    )

    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid_token))

    self.assertNotIn("value", response.json)
    # switch to active.qualification
    self.set_status("active.auction", {"auctionPeriod": {"startDate": None}, "status": "active.tendering"})
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.qualification")


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
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"][0]["value"] = {"amount": 450}
    bid, bid1_token = self.create_bid(self.tender_id, bid_data)
    bid_id = bid["id"]
    # create second bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid_data["lotValues"][0]["value"] = {"amount": 475}
    _, bid2_token = self.create_bid(self.tender_id, bid_data)
    # switch to active.auction
    self.set_status("active.auction")

    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction urls
    response = self.app.patch_json(
        "/tenders/{}/auction/{}".format(tender_id, bid_data["lotValues"][0]["relatedLot"]),
        {
            "data": {
                "lots": [
                    {
                        "auctionUrl": "https://tender.auction.url",
                    }
                ],
                "bids": [
                    {
                        "id": i["id"],
                        "lotValues": [
                            {"participationUrl": "https://tender.auction.url/for_bid/{}".format(i["id"])}
                            for v in i["lotValues"]
                        ],
                    }
                    for i in auction_bids_data
                ],
            }
        },
    )
    # view bid participationUrl
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/bids/{}?acc_token={}".format(tender_id, bid_id, bid1_token))
    self.assertEqual(
        response.json["data"]["lotValues"][0]["participationUrl"],
        "https://tender.auction.url/for_bid/{}".format(bid_id),
    )

    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction".format(tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as unsuccessful
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful"}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award2_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    self.assertNotEqual(award_id, award2_id)
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award2_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    self.assertNotEqual(award_id, award2_id)
    # create first award complaint
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
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


def lost_contract_for_active_award(self):
    bid_data = deepcopy(self.test_bids_data[0])
    bid_data["lotValues"][0]["value"] = {"amount": 500}
    self.app.authorization = ("Basic", ("broker", ""))
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    _, bid1_token = self.create_bid(tender_id, bid_data)
    # create bid #2
    self.app.authorization = ("Basic", ("broker", ""))
    _, bid2_token = self.create_bid(tender_id, bid_data)
    # switch to active.auction
    self.set_status("active.auction")

    # get auction info
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.get("/tenders/{}/auction".format(tender_id))
    auction_bids_data = response.json["data"]["bids"]
    # posting auction results
    self.app.authorization = ("Basic", ("auction", ""))
    response = self.app.post_json(
        "/tenders/{}/auction".format(tender_id), {"data": {"bids": [{"id": b["id"]} for b in auction_bids_data]}}
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True, "eligible": True}},
    )
    # lost contract
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender["contracts"]:
        self.mongodb.contracts.delete(i["id"])
    del tender["contracts"]
    self.mongodb.tenders.save(tender)
    # we no longer calculate next_check in get methods
    # check tender
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
    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)
    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    activate_contract(self, tender_id, contract_id, owner_token, bid1_token)
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def tender_with_main_procurement_category(self):
    data = deepcopy(self.initial_data)

    # test fail creation
    data["mainProcurementCategory"] = "whiskey,tango,foxtrot"
    response = self.app.post_json("/tenders", {"data": data}, status=422)
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
    token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["status"], "active.tendering")
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "goods")

    self.tender_id = tender["id"]

    # test success update tender in active.tendering status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"mainProcurementCategory": "services"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "services")


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
            "sequenceNumber": 1,
            "percentage": 45.55,
            "relatedLot": self.initial_lots[0]["id"] if self.initial_lots else None,
        },
        {
            "title": "deliveryOfGoods",
            "code": "postpayment",
            "type": "financing",
            "duration": {"days": 999, "type": "calendar"},
            "sequenceNumber": 2,
            "percentage": 54.45,
            "relatedLot": self.initial_lots[0]["id"] if self.initial_lots else None,
        },
    ]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.assertIn("milestones", tender)
    self.assertEqual(len(tender["milestones"]), 2)
    for milestone in tender["milestones"]:
        fields = {"id", "code", "duration", "percentage", "type", "sequenceNumber", "title"}
        if self.initial_lots:
            fields = fields | {"relatedLot"}
        self.assertEqual(
            set(milestone.keys()),
            fields,
        )
    self.assertEqual(data["milestones"][0]["id"], tender["milestones"][0]["id"])
    token = response.json["access"]["token"]
    self.tender_id = tender["id"]

    # test success update
    new_title = "endDateOfTheReportingPeriod"
    milestones = tender["milestones"]
    milestones[1]["title"] = new_title
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"milestones": milestones}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("milestones", response.json["data"])
    milestones = response.json["data"]["milestones"]
    self.assertEqual(len(milestones), 2)
    self.assertEqual(milestones[0]["title"], tender["milestones"][0]["title"])
    self.assertEqual(milestones[1]["title"], new_title)


def create_tender_with_criteria_lcc(self):
    # create not lcc tender
    data = deepcopy(self.initial_data)
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.assertNotEqual(tender["awardCriteria"], "lifeCycleCost")

    token = response.json["access"]["token"]
    self.tender_id = tender["id"]

    # can not patch awardCriteria
    tender_request_path = "/tenders/{}?acc_token={}".format(
        self.tender_id,
        token,
    )
    response = self.app.patch_json(tender_request_path, {"data": {"awardCriteria": "lifeCycleCost"}}, status=403)
    self.assertEqual(
        [{"location": "body", "name": "awardCriteria", "description": "Can\'t change awardCriteria"}],
        response.json["errors"],
    )

    # can not add lcc criteria in not lcc tender
    criteria_request_path = "/tenders/{}/criteria?acc_token={}".format(
        self.tender_id,
        token,
    )
    lcc_criteria = deepcopy(test_lcc_lot_criteria)
    response = self.app.post_json(criteria_request_path, {"data": [lcc_criteria[0]]}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "classification",
                "description": {
                    "id": [
                        "{} is available only with lifeCycleCost awardCriteria".format(
                            lcc_criteria[0]["classification"]["id"]
                        )
                    ]
                },
            }
        ],
    )

    # can not create lcc tender with features
    data["awardCriteria"] = "lifeCycleCost"
    test_feature = {
        "code": "OCDS-123454-AIR-INTAKE",
        "featureOf": "tenderer",
        "title": "test title",
        "description": "test description",
        "enum": [{"value": 0.1, "title": "test enum title"}, {"value": 0.15, "title": "test enum title 2"}],
    }
    data["features"] = [test_feature]

    response = self.app.post_json("/tenders", {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "awardCriteria",
                "description": ["Can`t add features with lifeCycleCost awardCriteria"],
            }
        ],
    )

    # create lcc tender
    data = deepcopy(self.initial_data)
    data["awardCriteria"] = "lifeCycleCost"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    self.assertEqual(tender["awardCriteria"], "lifeCycleCost")

    token = response.json["access"]["token"]
    self.tender_id = tender["id"]

    # can not add features to lcc tender
    tender_request_path = "/tenders/{}?acc_token={}".format(
        self.tender_id,
        token,
    )
    response = self.app.patch_json(tender_request_path, {"data": {"features": [test_feature]}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "awardCriteria",
                "description": ["Can`t add features with lifeCycleCost awardCriteria"],
            }
        ],
    )


def get_ocds_schema(self):
    self.create_tender()

    # get response in OCDS schema format
    resp = self.app.get(f"/tenders/{self.tender_id}?opt_schema=ocds-1.1")

    # validate the response is validated
    response = requests.get("https://standard.open-contracting.org/schema/1__1__5/release-package-schema.json")
    schema = response.json()
    validate(instance=resp.json, schema=schema)


@mock.patch(
    "openprocurement.tender.core.procedure.state.tender_details.RELATED_LOT_REQUIRED_FROM",
    get_now() + timedelta(days=1),
)
def tender_created_before_related_lot_constant(self):
    data = deepcopy(test_tender_open_data)
    data["status"] = "draft"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.tender_id = response.json["data"]["id"]
    self.tender_token = response.json["access"]["token"]

    test_criteria_data = deepcopy(test_exclusion_criteria)
    for i in range(len(test_criteria_data)):
        classification_id = test_criteria_data[i]['classification']['id']
        if classification_id == 'CRITERION.EXCLUSION.CONTRIBUTIONS.PAYMENT_OF_TAXES':
            del test_criteria_data[i]
            break
    test_criteria_data.extend(test_language_criteria)

    response = self.app.post_json(
        '/tenders/{}/criteria?acc_token={}'.format(self.tender_id, self.tender_token), {'data': test_criteria_data}
    )
    self.assertEqual(response.status, '201 Created')
    self.add_notice_doc(self.tender_id, self.tender_token)

    # forbid patch tender without lot even before RELATED_LOT_REQUIRED_FROM constant for aboveThreshold
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}?acc_token={self.tender_token}", {"data": {"status": "active.tendering"}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "item.relatedLot", "description": "This field is required"}],
    )


# TenderDPSResourceTest


def create_tender_dps(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("complaintPeriod", response.json["data"])
    tender_id = response.json["data"]["id"]

    # try to add complaint
    complaint_data = deepcopy(test_tender_below_draft_complaint)
    response = self.app.post_json(f"/tenders/{tender_id}/complaints", {"data": complaint_data}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add complaint as it is forbidden by configuration"
    )


def create_tender_dps_invalid_config(self):
    for config_name in ("hasTenderComplaints", "hasAwardComplaints", "hasCancellationComplaints"):
        config = deepcopy(self.initial_config)
        config.update({config_name: True})
        response = self.app.post_json(
            "/tenders",
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
            [{"description": "True is not one of [False]", "location": "body", "name": config_name}],
        )
