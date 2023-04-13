# -*- coding: utf-8 -*-
from copy import deepcopy
import mock
from datetime import timedelta
from uuid import uuid4
from openprocurement.api.utils import get_now
from openprocurement.api.constants import (
    ROUTE_PREFIX,
    CPV_ITEMS_CLASS_FROM,
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM,
    RELEASE_2020_04_19,
    NEW_NEGOTIATION_CAUSES_FROM,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_organization,
    test_tender_below_cancellation,
)
from openprocurement.tender.core.tests.cancellation import activate_cancellation_after_2020_04_19
from openprocurement.tender.limited.models import NegotiationTender, NegotiationQuickTender


def create_tender_accreditation(self):
    for broker in ["broker1", "broker3"]:
        self.app.authorization = ("Basic", (broker, ""))
        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")

    for broker in ["broker2", "broker4"]:
        self.app.authorization = ("Basic", (broker, ""))
        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config}, status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json["errors"][0]["description"], "Broker Accreditation level does not permit tender creation"
        )

    self.app.authorization = ("Basic", ("broker1t", ""))
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Broker Accreditation level does not permit tender creation"
    )


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

    response = self.app.get("/tenders")
    self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in tenders]))
    self.assertEqual(set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in tenders]))
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders]))

    response = self.app.get(f"/tenders?offset={offset}")
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
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders", params=[("opt_fields", "status")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "status"]))
    self.assertIn("opt_fields=status", response.json["next_page"]["uri"])

    response = self.app.get("/tenders?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
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
    self.set_initial_status(response.json)

    while True:
        response = self.app.get("/tenders?mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def tender_award_create(self):
    data = self.initial_data.copy()
    award_id = "1234" * 8
    data["awards"] = [
        {
            "suppliers": [test_tender_below_organization],
            "subcontractingDetails": "Details",
            "status": "pending",
            "qualified": True,
            "id": award_id,
        }
    ]

    data["contracts"] = [{"title": "contract title", "description": "contract description", "awardID": award_id}]
    response = self.app.post_json("/tenders",
                                  {"data": data},
                                  status=422)
    self.assertCountEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "awards",
                "description": "Rogue field"
            },
            {
                "location": "body",
                "name": "contracts",
                "description": "Rogue field"
            }
        ]
    )


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

    while True:
        response = self.app.get("/tenders?feed=changes")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

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
    self.set_initial_status(response.json)

    while True:
        response = self.app.get("/tenders?feed=changes&mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/tenders?feed=changes&mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def create_tender_invalid(self):
    request_path = "/tenders"

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": "reporting", "invalid_field": "invalid_value"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": "reporting", "value": "invalid_value"}}, status=422
    )
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

    response = self.app.post_json(
        request_path, {"data": {"procurementMethodType": "reporting", "procurementMethod": "invalid_value"}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {
            "description": ["Value must be one of ['limited']."],
            "location": "body",
            "name": "procurementMethod",
        },
        response.json["errors"],
    )
    self.assertIn(
        {"description": ["This field is required."], "location": "body", "name": "items"}, response.json["errors"]
    )

    data = self.initial_data["items"][0].pop("additionalClassifications")
    if get_now() > CPV_ITEMS_CLASS_FROM:
        cpv_code = self.initial_data["items"][0]["classification"]["id"]
        self.initial_data["items"][0]["classification"]["id"] = "99999999-9"
    status = 422 if get_now() < NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM else 201
    response = self.app.post_json(request_path, {
        "data": self.initial_data,
        "config": self.initial_config,
    }, status=status)
    self.initial_data["items"][0]["additionalClassifications"] = data
    if get_now() > CPV_ITEMS_CLASS_FROM:
        self.initial_data["items"][0]["classification"]["id"] = cpv_code
    if status == 201:
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
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
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
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
                                "One of additional classifications should be one of [ДК003, ДК015, ДК018, specialNorms]."
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
                                "One of additional classifications should be one of [ДКПП, NONE, ДК003, ДК015, ДК018]."
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
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
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
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
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
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["items"] = self.initial_data["items"][:1]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["CPV class of items should be identical"], "location": "body", "name": "items"}],
    )

    data = deepcopy(self.initial_data)
    del data["items"][0]["deliveryDate"]
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": [{"deliveryDate": ["This field is required."]}], "location": "body", "name": "items"}],
    )


def field_relatedLot(self):
    request_path = "/tenders"
    data = deepcopy(self.initial_data)
    data["items"][0]["relatedLot"] = uuid4().hex
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedLot": ["This option is not available"]}],
                "location": "body",
                "name": "items",
            }
        ],
    )


def create_tender_generated(self):
    data = self.initial_data.copy()
    data.update({"id": "hash"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    fields = [
        "id",
        "dateCreated",
        "dateModified",
        "tenderID",
        "status",
        "items",
        "value",
        "procuringEntity",
        "owner",
        "procurementMethod",
        "procurementMethodType",
        "title",
        "date",
        "mainProcurementCategory",
        "milestones",
    ]
    if "procurementMethodDetails" in self.initial_data:
        fields.append("procurementMethodDetails")
    if "negotiation" == self.initial_data["procurementMethodType"]:
        fields.append("cause")
    if "negotiation.quick" == self.initial_data["procurementMethodType"]:
        fields.append("cause")
    if "negotiation" in self.initial_data["procurementMethodType"]:
        fields.append("causeDescription")
    self.assertEqual(set(tender), set(fields))
    self.assertNotEqual(data["id"], tender["id"])


def create_tender_draft(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"value": {"amount": 100}}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Can't update tender in current (draft) status", "location": "body", "name": "data"}],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "active")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "active")


def create_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    tender_set = set(tender)
    if "procurementMethodDetails" in tender_set:
        tender_set.remove("procurementMethodDetails")
    if "negotiation" == self.initial_data["procurementMethodType"]:
        tender_set.remove("cause")
    if "negotiation" in self.initial_data["procurementMethodType"]:
        tender_set.remove("causeDescription")
    self.assertEqual(
        tender_set - set(self.initial_data),
        {"id", "date", "dateModified", "dateCreated", "owner", "tenderID", "status", "procurementMethod"},
    )
    self.assertIn(tender["id"], response.headers["Location"])

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

    response = self.app.post_json("/tenders?opt_pretty=1", {"data": self.initial_data, "config": self.initial_config})
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

    data = deepcopy(self.initial_data)
    del data["items"][0]["deliveryAddress"]["postalCode"]
    del data["items"][0]["deliveryAddress"]["locality"]
    del data["items"][0]["deliveryAddress"]["streetAddress"]
    del data["items"][0]["deliveryAddress"]["region"]
    response = self.app.post_json("/tenders", {
        "data": data,
        "config": self.initial_config,
    })
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("postalCode", response.json["data"]["items"][0]["deliveryAddress"])
    self.assertNotIn("locality", response.json["data"]["items"][0]["deliveryAddress"])
    self.assertNotIn("streetAddress", response.json["data"]["items"][0]["deliveryAddress"])
    self.assertNotIn("region", response.json["data"]["items"][0]["deliveryAddress"])

    initial_data = deepcopy(self.initial_data)
    initial_data["items"][0]["classification"]["id"] = "99999999-9"
    additional_classification = initial_data["items"][0].pop("additionalClassifications")
    additional_classification[0]["scheme"] = "specialNorms"
    if get_now() > NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM:
        response = self.app.post_json("/tenders", {
            "data": initial_data,
            "config": self.initial_config,
        })
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        tender = response.json["data"]
        self.assertEqual(tender["items"][0]["classification"]["id"], "99999999-9")
        self.assertNotIn("additionalClassifications", tender["items"][0])

    initial_data["items"][0]["additionalClassifications"] = additional_classification
    response = self.app.post_json("/tenders", {
        "data": initial_data,
        "config": self.initial_config,
    })
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["items"][0]["classification"]["id"], "99999999-9")
    self.assertEqual(tender["items"][0]["additionalClassifications"], additional_classification)


def patch_tender(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    owner_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)
    tender = response.json["data"]
    dateModified = tender.pop("dateModified")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procurementMethodRationale": "Limited"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    new_tender = response.json["data"]
    new_dateModified = new_tender.pop("dateModified")
    tender["procurementMethodRationale"] = "Limited"
    self.assertEqual(tender, new_tender)
    self.assertNotEqual(dateModified, new_dateModified)

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"dateModified": new_dateModified}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "dateModified",
            "description": "Rogue field"
        }]
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
        [{
            "location": "body",
            "name": "procuringEntity",
            "description": "Can't change procuringEntity.kind in a public tender"
        }]
    )

    revisions = self.mongodb.tenders.get(tender["id"]).get("revisions")
    self.assertEqual(revisions[-1]["changes"][0]["op"], "remove")
    self.assertEqual(revisions[-1]["changes"][0]["path"], "/procurementMethodRationale")

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
        {"data": {"items": [self.initial_data["items"][0]]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)

    item = deepcopy(self.initial_data["items"][0])
    item["classification"] = {
        "scheme": "ДК021",
        "id": "55523100-3",
        "description": "Послуги з харчування у школах",
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "items": [item]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    item = deepcopy(self.initial_data["items"][0])
    item["additionalClassifications"] = [
        tender["items"][0]["additionalClassifications"][0] for i in range(3)
    ]
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {"items": [item]}
        },
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

    # The following operations are performed for a proper transition to the "Complete" tender status

    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender["id"], owner_token),
        {"data": {"suppliers": [test_tender_below_organization],
                  "status": "pending",
                  "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False}}},
    )
    award_id = response.json["data"]["id"]
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender["id"], award_id, owner_token),
        {"data": {"qualified": True, "status": "active"}},
    )

    response = self.app.get("/tenders/{}/contracts".format(tender["id"]))
    contract_id = response.json["data"][0]["id"]

    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(tender["id"], contract_id, owner_token),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )
    self.assertEqual(response.status, "201 Created")

    save_tender = self.mongodb.tenders.get(tender["id"])
    for i in save_tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # works for negotiation tender
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(save_tender)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender["id"], contract_id, owner_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "complete")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender in current (complete) status")


def field_relatedLot_negotiation(self):
    request_path = "/tenders"
    data = deepcopy(self.initial_data)
    data["items"][0]["relatedLot"] = uuid4().hex
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [{"relatedLot": ["relatedLot should be one of lots"]}],
                "location": "body",
                "name": "items",
            }
        ],
    )


def changing_tender_after_award(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)

    # create lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    first_lot = response.json["data"]

    # create second lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # change tender
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"description": "New description"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["description"], "New description")

    # first award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_tender_below_organization],
                  "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
                  "status": "pending",
                  "lotID": first_lot["id"],
                  "qualified": True}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # change tender
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"description": "New description new"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update tender when there is at least one award.")


def initial_lot_date(self):
    # create tender were initial data has lots
    lots = deepcopy(self.test_lots_data) * 2
    data = deepcopy(self.initial_data)
    data["lots"] = lots
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    # check if initial lots have date
    response = self.app.get("/tenders/{}".format(tender_id))
    lots = response.json["data"]["lots"]
    self.assertIn("date", lots[0])
    self.assertIn("date", lots[1])

    # create lot
    response = self.app.post_json(
        "/tenders/{}/lots?acc_token={}".format(tender_id, owner_token), {"data": self.test_lots_data[0]}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # check all lots has a initial date
    response = self.app.get("/tenders/{}".format(tender_id))
    lots = response.json["data"]["lots"]
    self.assertIn("date", lots[0])
    self.assertIn("date", lots[1])
    self.assertIn("date", lots[2])


def tender_status_change(self):
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)

    self.app.authorization = ("Basic", ("chronograph", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"status": "complete"}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"status": "complete"}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    # check status
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "active")

    # try to mark tender complete
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "complete"}},
        status=422
    )
    self.assertEqual(response.json["errors"][0]["name"], "status")

    # try to mark tender draft
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "draft"}},
        status=422
    )
    self.assertEqual(response.json["errors"][0]["name"], "status")


def tender_negotiation_status_change(self):
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json("/tenders/{}".format(tender_id), {"data": {"status": "complete"}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    # check status
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "active")

    # try to mark tender complete
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "complete"}},
        status=422
    )
    self.assertEqual(response.json["errors"][0]["name"], "status")

    # try to mark tender draft
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token),
        {"data": {"status": "draft"}},
        status=422
    )
    self.assertEqual(response.json["errors"][0]["name"], "status")


def single_award_tender(self):
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)

    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(response.json["data"], [])

    # create award
    response = self.app.post_json(
        "/tenders/{}/awards".format(tender_id),
        {"data": {"suppliers": [test_tender_below_organization], "value": {"amount": 500}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_tender_below_organization], "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")

    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))

    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]

    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"qualified": True, "status": "active"}},
    )

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])

    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # reporting procedure does not have complaintPeriod
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    # sign contract
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    # check status
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")

    # create new tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)

    # create award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_tender_below_organization], "qualified": True, "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")

    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(len(response.json["data"]), 1)

    # get last award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][-1]

    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    self.assertEqual(contract["awardID"], award_id)

    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # reporting procedure does not have complaintPeriod
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    # set award to cancelled
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "cancelled"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # try to sign contract
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract["id"], owner_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update contract in current (cancelled) status")

    # tender status remains the same
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "active")


def multiple_awards_tender(self):
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    self.set_initial_status(response.json)

    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(response.json["data"], [])

    # create award
    response = self.app.post_json(
        "/tenders/{}/awards".format(tender_id),
        {"data": {"suppliers": [test_tender_below_organization], "qualified": True, "value": {"amount": 500}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_tender_below_organization], "qualified": True, "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")
    award = response.json["data"]

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award["id"], owner_token),
        {"data": {"qualified": True, "status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_tender_below_organization], "qualified": True, "value": {"amount": 501}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't create new award while any (active) award exists"
    )

    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award["id"], owner_token),
        {"data": {"status": "cancelled"}},
    )

    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_tender_below_organization], "qualified": True, "value": {"amount": 505}}},
    )
    self.assertEqual(response.status, "201 Created")

    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(len(response.json["data"]), 2)

    # get last award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][-1]

    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token), {"data": {"status": "active"}}
    )

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    self.assertEqual(contract["awardID"], award_id)

    # time travel
    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # reporting procedure does not have complaintPeriod
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    # sign contract
    contract["value"]["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract["id"], owner_token),
        {"data": {"status": "active", "value": contract["value"]}},
    )
    # check status
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def tender_cancellation(self):
    # empty tenders listing
    response = self.app.get("/tenders")
    self.assertEqual(response.json["data"], [])
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = self.tender_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)

    # create cancellation
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "reason": "invalid conditions",
        "status": "active"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    cacnellation_id = response.json["data"]["id"]
    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_after_2020_04_19(self, cacnellation_id, tender_id, owner_token)

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "cancelled")

    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)

    # create award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_tender_below_organization], "qualified": True, "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")

    # create cancellation
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "reason": "invalid conditions",
        "status": "active"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    cancellation_id = response.json["data"]["id"]
    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_after_2020_04_19(
            self,
            cancellation_id,
            tender_id,
            owner_token
        )
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "cancelled")

    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = self.tender_token = response.json["access"]["token"]
    self.set_initial_status(response.json)

    # create award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_tender_below_organization], "qualified": True, "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")
    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(len(response.json["data"]), 1)
    award = response.json["data"][0]
    self.assertEqual(award["status"], "pending")

    # set award as active
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award["id"], owner_token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])

    self.set_all_awards_complaint_period_end()

    # create cancellation in stand still
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "reason": "invalid conditions",
        "status": "active"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    cancellation_id = response.json["data"]["id"]
    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_after_2020_04_19(
            self,
            cancellation_id,
            tender_id,
            owner_token
        )

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "cancelled")

    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = self.tender_token = response.json["access"]["token"]
    response = self.set_initial_status(response.json)

    # create award
    response = self.app.post_json(
        "/tenders/{}/awards?acc_token={}".format(tender_id, owner_token),
        {"data": {"suppliers": [test_tender_below_organization], "qualified": True, "value": {"amount": 500}}},
    )
    self.assertEqual(response.status, "201 Created")
    # get awards
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    self.assertEqual(len(response.json["data"]), 1)
    award = response.json["data"][0]
    self.assertEqual(award["status"], "pending")

    # set award as active
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award["id"], owner_token), {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])

    tender = self.mongodb.tenders.get(tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # works for negotiation tender
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    # sign contract
    self.app.authorization = ("Basic", ("broker", ""))
    contract_value["valueAddedTaxIncluded"] = False
    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(tender_id, contract_id, owner_token),
        {"data": {"status": "active", "value": contract_value}},
    )
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "complete")

    self.set_all_awards_complaint_period_end()

    # create cancellation
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update({
        "reason": "invalid conditions",
        "status": "active"
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "complete")


def tender_cause(self):
    data = deepcopy(self.initial_data)

    del data["cause"]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "cause"}],
    )

    data["cause"] = "additionalPurchase"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")

    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender_id, owner_token), {"data": {"cause": "stateLegalServices"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["cause"], "stateLegalServices")


def tender_cause_quick(self):
    data = deepcopy(self.initial_data)
    del data["cause"]

    constant_target = "openprocurement.tender.limited.procedure.models.tender.QUICK_CAUSE_REQUIRED_FROM"

    with mock.patch(constant_target, get_now() + timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})

    self.assertEqual(response.status, "201 Created")

    with mock.patch(constant_target, get_now() - timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "cause"}],
    )

    data["cause"] = "additionalConstruction"

    with mock.patch(constant_target, get_now() - timedelta(days=1)):
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})

    self.assertEqual(response.status, "201 Created")


def tender_cause_choices(self):
    data = deepcopy(self.initial_data)

    data["cause"] = "unexisting value"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    if get_now() > NEW_NEGOTIATION_CAUSES_FROM:
        cause_choices_map = {
            "negotiation": NegotiationTender._cause_choices_new,
            "negotiation.quick": NegotiationQuickTender._cause_choices_new,
        }
    else:
        cause_choices_map = {
            "negotiation": NegotiationTender._cause_choices,
            "negotiation.quick": NegotiationQuickTender._cause_choices,
        }

    cause_choices = cause_choices_map.get(data["procurementMethodType"])

    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Value must be one of ['{}'].".format("', '".join(cause_choices))],
                "location": "body",
                "name": "cause",
            }
        ],
    )


def tender_cause_desc(self):
    data = deepcopy(self.initial_data)
    del data["causeDescription"]
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "causeDescription"}],
    )

    data["causeDescription"] = ""
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["String value is too short."], "location": "body", "name": "causeDescription"}],
    )

    data["causeDescription"] = "blue pine"
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["causeDescription"], "blue pine")


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

    # test success update tender in active status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"mainProcurementCategory": "services"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("mainProcurementCategory", response.json["data"])
    self.assertEqual(response.json["data"]["mainProcurementCategory"], "services")


def tender_set_fund_organizations(self):
    data = dict(**self.initial_data)
    data["funders"] = [{"name": "Запишіть в тєтрадку"}]

    resp = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=201)
    result = resp.json["data"]
    self.assertEquals([{"name": "Запишіть в тєтрадку"}], result["funders"])
