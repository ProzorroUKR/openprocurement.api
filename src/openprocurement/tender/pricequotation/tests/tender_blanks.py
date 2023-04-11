import mock
from uuid import uuid4
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.utils import get_now
from openprocurement.api.constants import (
    ROUTE_PREFIX,
    CPV_BLOCK_FROM,
    NOT_REQUIRED_ADDITIONAL_CLASSIFICATION_FROM,
    SANDBOX_MODE,
    CPV_ITEMS_CLASS_FROM,
    PQ_MULTI_PROFILE_FROM,
)
from openprocurement.tender.pricequotation.tests.base import (
    test_tender_pq_organization,
    test_tender_pq_cancellation,
    test_tender_pq_shortlisted_firms,
    test_tender_pq_short_profile,
    test_tender_pq_requirement_response,
    test_tender_pq_data_before_multiprofile,
    test_tender_pq_data_after_multiprofile,
    test_tender_pq_item_before_multiprofile,
    test_tender_pq_item_after_multiprofile,
)
from openprocurement.tender.pricequotation.tests.data import test_tender_pq_milestones
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.core.tests.criteria_utils import add_criteria
from openprocurement.tender.pricequotation.constants import PQ, PQ_KINDS


def listing(self):
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []

    for i in range(3):
        offset = get_now().isoformat()
        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.tender_id = response.json['data']['id']
        self.set_status('active.tendering')
        tender = self.app.get("/tenders/{}".format(self.tender_id)).json['data']
        tenders.append(tender)

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


def listing_changes(self):
    response = self.app.get("/tenders?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    tenders = []

    for i in range(3):
        response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.tender_id = response.json['data']['id']
        self.set_status('active.tendering')
        tender = self.app.get("/tenders/{}".format(self.tender_id)).json['data']
        tenders.append(tender)
    ids = ",".join([i["id"] for i in tenders])

    while True:
        response = self.app.get("/tenders?feed=changes")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

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

    response = self.app.get("/tenders?feed=changes", params=[("opt_fields", "status")])
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
        self.tender_id = response.json['data']['id']
        self.set_status('active.tendering')
        tender = self.app.get("/tenders/{}".format(self.tender_id)).json['data']
        tenders.append(tender)

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


def create_tender_invalid(self):
    request_path = "/tenders"
    self.app.post_json(request_path, {"data": {"procurementMethodType": "invalid_value"}}, status=404)

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value", "procurementMethodType": PQ}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"value": "invalid_value", "procurementMethodType": PQ}}, status=422)
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

    response = self.app.post_json(request_path, {"data": {"procurementMethod": "invalid_value", "procurementMethodType": PQ }}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")

    self.assertIn(
        {
            "description": ["Value must be one of ['selective']."],
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

    data = self.initial_data["tenderPeriod"]
    self.initial_data["tenderPeriod"] = {"startDate": "2014-10-31T00:00:00", "endDate": "2014-10-01T00:00:00"}
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
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

    now = get_now()
    self.initial_data["awardPeriod"] = {"startDate": now.isoformat(), "endDate": now.isoformat()}
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    del self.initial_data["awardPeriod"]
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["period should begin after tenderPeriod"], "location": "body", "name": "awardPeriod"}],
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

    invalid_data = deepcopy(self.initial_data)
    del invalid_data["procuringEntity"]["contactPoint"]["telephone"]
    response = self.app.post_json(request_path, {"data": invalid_data}, status=422)
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

    cpv = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "160173000-1"
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["items"][0]["classification"]["id"] = cpv
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("classification", response.json["errors"][0]["description"][0])
    self.assertIn("id", response.json["errors"][0]["description"][0]["classification"])
    self.assertEqual(response.json["errors"][0]["description"][0]["classification"]["id"][0],
                     "Value must be one of ДК021 codes")

    cpv = self.initial_data["items"][0]["classification"]["id"]
    if get_now() < CPV_BLOCK_FROM:
        self.initial_data["items"][0]["classification"]["scheme"] = "CPV"
    self.initial_data["items"][0]["classification"]["id"] = "00000000-0"
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    if get_now() < CPV_BLOCK_FROM:
        self.initial_data["items"][0]["classification"]["scheme"] = "CPV"
    self.initial_data["items"][0]["classification"]["id"] = cpv
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("classification", response.json["errors"][0]["description"][0])
    self.assertIn("id", response.json["errors"][0]["description"][0]["classification"])
    self.assertEqual(response.json["errors"][0]["description"][0]["classification"]["id"][0],
                     "Value must be one of {} codes".format(self.initial_data["items"][0]["classification"]["scheme"]))

    procuringEntity = self.initial_data["procuringEntity"]
    data = self.initial_data["procuringEntity"].copy()
    del data["kind"]
    self.initial_data["procuringEntity"] = data
    response = self.app.post_json(request_path, {"data": self.initial_data}, status=422)
    self.initial_data["procuringEntity"] = procuringEntity
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "procuringEntity",
            "description": {
                "kind": ["This field is required."]
            }
        }],
    )

    data = deepcopy(self.initial_data)
    data['milestones'] = test_tender_pq_milestones
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{
            "location": "body",
            "name": "milestones",
            "description": "Rogue field"
        }],
    )

    data = deepcopy(self.initial_data)
    data["procuringEntity"]['kind'] = 'central'
    response = self.app.post_json(request_path, {"data": data}, status=422)
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "procuringEntity", "description": {"kind": [
            "Value must be one of [\'general\', \'special\', \'defense\', \'other\', \'social\', \'authority\']."]}}]
    )

    before = get_now() - timedelta(days=1)
    with mock.patch("openprocurement.tender.pricequotation.procedure.models.item.PQ_MULTI_PROFILE_FROM", before):
        with mock.patch("openprocurement.tender.pricequotation.procedure.models.tender.PQ_MULTI_PROFILE_FROM", before):
            data = deepcopy(test_tender_pq_data_after_multiprofile)
            data["agreement"]["id"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"
            response = self.app.post_json(request_path, {"data": data}, status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["status"], "error")
            self.assertEqual(
                response.json["errors"], [{
                    "description": {"id": ["Hash value is wrong length."]},
                    "location": "body",
                    "name": "agreement"
                }],
            )

            data["agreement"]["id"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            response = self.app.post_json(request_path, {"data": data}, status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["status"], "error")
            self.assertEqual(
                response.json["errors"], [{
                    "description": {"id": ["id must be one of exists agreement"]},
                    "location": "body",
                    "name": "agreement"
                }],
            )

            del data["agreement"]["id"]
            response = self.app.post_json(request_path, {"data": data}, status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["status"], "error")
            self.assertEqual(
                response.json["errors"], [{
                    "description": {"id": ["This field is required."]},
                    "location": "body",
                    "name": "agreement"
                }],
            )

            del data["agreement"]
            response = self.app.post_json(request_path, {"data": data}, status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["status"], "error")
            self.assertEqual(
                response.json["errors"], [{
                    "description": ["This field is required."],
                    "location": "body",
                    "name": "agreement"
                }],
            )

            data = deepcopy(test_tender_pq_data_after_multiprofile)
            data["items"] = [test_tender_pq_item_before_multiprofile]
            response = self.app.post_json(request_path, {"data": data}, status=422)
            self.assertEqual(response.status, '422 Unprocessable Entity')
            self.assertEqual(response.content_type, "application/json")
            self.assertEqual(response.json["status"], "error")
            self.assertEqual(
                response.json["errors"], [{
                    "description": [{"profile": ["This field is required."]}],
                    "location": "body",
                    "name": "items"
                }],
            )


def create_tender_with_inn(self):
    request_path = "/tenders"

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


def create_tender_generated(self):
    data = self.initial_data.copy()
    data.update({"id": "hash"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    if "procurementMethodDetails" in tender:
        tender.pop("procurementMethodDetails")
    tender_keys = [
        "procurementMethodType",
        "id",
        "date",
        "dateCreated",
        "dateModified",
        "tenderID",
        "status",
        "tenderPeriod",
        "items",
        "procuringEntity",
        "procurementMethod",
        "awardCriteria",
        "title",
        "owner",
        "mainProcurementCategory",
        "value",
    ]
    if get_now() < PQ_MULTI_PROFILE_FROM:
        tender_keys.append("profile")
    else:
        tender_keys.append("agreement")
    self.assertEqual(
        set(tender),
        set(tender_keys),
    )

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
    self.assertNotIn("noticePublicationDate", tender)
    self.assertNotIn("unsuccessfulReason", tender)

    if SANDBOX_MODE:
        period = {
            'endDate': (get_now() + timedelta(minutes=1)).isoformat(),
            'startDate': tender["tenderPeriod"]["startDate"],
        }
    else:
        period = {
            'endDate': (get_now() + timedelta(days=1)).isoformat(),
            'startDate': tender["tenderPeriod"]["startDate"],
        }

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"status": self.primary_tender_status, "tenderPeriod": period}},
        status=422
    )

    self.assertEqual(
        response.json["errors"],
        [{'description': ['tenderPeriod must be at least 2 full business days long'],
          'location': 'body',
          'name': 'tenderPeriod'}]
    )

    forbidden_statuses = ("draft.unsuccessful", "active.tendering", "active.qualification", "active.awarded",
                          "complete", "cancelled", "unsuccessful")
    current_status = tender["status"]
    for forbidden_status in forbidden_statuses:
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], token),
            {"data": {"status": forbidden_status}},
            status=422
        )
        self.assertEqual(response.json['status'], "error")
        self.assertEqual(response.json['errors'][0]["name"], "status")

    pq_entity = deepcopy(tender["procuringEntity"])
    pq_entity["kind"] = "central"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"procuringEntity": pq_entity}},
        status=422
    )
    self.assertEqual(
        response.json['errors'],
        [{
            "location": "body",
            "name": "procuringEntity",
            "description": {
                "kind": ["Value must be one of ['general', 'special', 'defense', 'other', 'social', 'authority']."]
            }
        }]
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"status": self.primary_tender_status, "unsuccessfulReason": ["some value from buyer"]}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "unsuccessfulReason",
            "description": "Rogue field"
        }]
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"status": self.primary_tender_status}},
        status=403,
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "data",
            "description": "Can't update tender to next (draft.publishing) status without criteria"
        }],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": {
                "status": self.primary_tender_status,
                "criteria": self.test_criteria_1,
            }
        }
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], self.primary_tender_status)
    self.assertEqual(tender["noticePublicationDate"], tender["tenderPeriod"]["startDate"])
    self.assertNotIn("unsuccessfulReason", tender)
    self.assertIn("criteria", tender)

    response = self.app.get("/tenders/{}".format(tender["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(tender["status"], self.primary_tender_status)


def create_tender_draft_with_criteria(self):
    data = self.initial_data.copy()
    data["criteria"] = self.test_criteria_1
    data["status"] = "draft"

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    tender = response.json["data"]
    tender_id = tender["id"]
    token = response.json["access"]["token"]

    self.assertEqual(
        set(e["description"] for e in tender["criteria"]),
        set(e["description"] for e in data["criteria"])
    )

    # try updating criteria ids
    patch_criteria = deepcopy(tender["criteria"])
    for c in patch_criteria:
        c["id"] = uuid4().hex

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"criteria": patch_criteria}}
    )
    patch_result = response.json["data"]
    self.assertEqual(
        set(e["id"] for e in patch_result["criteria"]),
        set(e["id"] for e in patch_criteria)
    )

    # try adding a new criteria
    patch_criteria = patch_criteria + deepcopy(patch_criteria)

    from openprocurement.tender.pricequotation.procedure.models.requirement import PQ_CRITERIA_ID_FROM
    if get_now() > PQ_CRITERIA_ID_FROM:
        response = self.app.patch_json(
            f"/tenders/{tender_id}?acc_token={token}",
            {"data": {"criteria": patch_criteria}},
            status=422
        )
        self.assertEqual(
            response.json["errors"],
            [{"location": "body", "name": "criteria",
              "description": ["Criteria id should be uniq"]}]
        )
        # fix criteria ids
        for c in patch_criteria:
            c["id"] = uuid4().hex
        response = self.app.patch_json(
            f"/tenders/{tender_id}?acc_token={token}",
            {"data": {"criteria": patch_criteria}},
            status=422
        )
        self.assertEqual(
            response.json["errors"],
            [{"location": "body", "name": "criteria",
              "description": ["Requirement group id should be uniq in tender"]}]
        )

        # fix group ids
        for c in patch_criteria:
            for g in c["requirementGroups"]:
                g["id"] = uuid4().hex
        response = self.app.patch_json(
            f"/tenders/{tender_id}?acc_token={token}",
            {"data": {"criteria": patch_criteria}},
            status=422
        )
        self.assertEqual(
            response.json["errors"],
            [{"location": "body", "name": "criteria",
              "description": ["Requirement id should be uniq for all requirements in tender"]}]
        )

    # fix requirement ids
    for c in patch_criteria:
        for g in c["requirementGroups"]:
            for r in g["requirements"]:
                r["id"] = uuid4().hex
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"criteria": patch_criteria}},
    )
    patch_result = response.json["data"]

    # old object ids hasn't been changed
    self.assertEqual(len(patch_result["criteria"]), 6)
    self.assertEqual(
        [e["id"] for e in patch_result["criteria"]],
        [e["id"] for e in patch_criteria]
    )


def create_tender_draft_with_criteria_expected_values(self):
    data = self.initial_data.copy()
    data["criteria"] = self.test_criteria_1
    data["status"] = "draft"

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    tender = response.json["data"]
    tender_id = tender["id"]
    token = response.json["access"]["token"]

    self.assertEqual(
        set(e["description"] for e in tender["criteria"]),
        set(e["description"] for e in data["criteria"])
    )

    tender_criteria = tender["criteria"]

    patch_failed_criteria = deepcopy(tender_criteria)
    patch_failed_criteria[2]["requirementGroups"][0]["requirements"][0]["expectedValue"] = "value"
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"criteria": patch_failed_criteria}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": [
                    "expectedValue conflicts with ['minValue', 'maxValue', 'expectedValues']"
                ]
            }]
        }]
    )

    patch_failed_criteria = deepcopy(tender_criteria)
    patch_failed_criteria[2]["requirementGroups"][0]["requirements"][0]["minValue"] = "2"
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"criteria": patch_failed_criteria}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": ["expectedValues conflicts with "
                                      "['minValue', 'maxValue', 'expectedValue']"]
            }]
        }]
    )

    patch_failed_criteria = deepcopy(tender_criteria)
    patch_failed_criteria[2]["requirementGroups"][0]["requirements"][0]["expectedValues"] = None
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"criteria": patch_failed_criteria}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": ["Value required for at least one field "
                                      "[\"expectedValues\", \"expectedValue\", \"minValue\", \"maxValue\"]"]
            }]
        }]
    )

    patch_failed_criteria = deepcopy(tender_criteria)
    patch_failed_criteria[2]["requirementGroups"][0]["requirements"][0]["expectedValues"] = None
    patch_failed_criteria[2]["requirementGroups"][0]["requirements"][0]["expectedValue"] = "value"
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"criteria": patch_failed_criteria}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": ["expectedMinItems and expectedMaxItems "
                                      "couldn't exist without expectedValues"]
            }]
        }]
    )

    patch_failed_criteria = deepcopy(tender_criteria)
    patch_failed_criteria[2]["requirementGroups"][0]["requirements"][0]["expectedMinItems"] = 4
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"criteria": patch_failed_criteria}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": ["expectedMinItems couldn't be higher then expectedMaxItems"]
            }]
        }]
    )

    patch_failed_criteria = deepcopy(tender_criteria)
    patch_failed_criteria[2]["requirementGroups"][0]["requirements"][0]["expectedMinItems"] = 5
    patch_failed_criteria[2]["requirementGroups"][0]["requirements"][0]["expectedMaxItems"] = None
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"criteria": patch_failed_criteria}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": ["expectedMinItems couldn't be higher then count of items in expectedValues"]
            }]
        }]
    )

    patch_failed_criteria = deepcopy(tender_criteria)
    patch_failed_criteria[2]["requirementGroups"][0]["requirements"][0]["expectedMaxItems"] = 5
    patch_failed_criteria[2]["requirementGroups"][0]["requirements"][0]["expectedMinItems"] = None
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"criteria": patch_failed_criteria}},
        status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": ["expectedMaxItems couldn't be higher then count of items in expectedValues"]
            }]
        }]
    )


def tender_criteria_values_type(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    tender = response.json["data"]
    tender_id = tender["id"]
    token = response.json["access"]["token"]

    req_path = f"/tenders/{tender_id}?acc_token={token}"

    # Test dataType == "string"

    criteria = [deepcopy(self.test_criteria_1[0])]
    requirement = criteria[0]["requirementGroups"][0]["requirements"][0]
    requirement["dataType"] = "string"
    requirement["expectedValue"] = 1
    data = {"data": {"criteria": criteria}}
    response = self.app.patch_json(req_path, data, status=422)

    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": [{
                    "requirements": [{
                        "expectedValue": ["Couldn't interpret '1' as string."]
                    }]
                }]
            }]
        }]
    )

    requirement["expectedValue"] = True
    response = self.app.patch_json(req_path, data, status=422)

    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": [{
                    "requirements": [{
                        "expectedValue": ["Couldn't interpret 'True' as string."]
                    }]
                }]
            }]
        }]
    )

    # Test dataType == "integer"
    requirement["dataType"] = "integer"
    requirement["expectedValue"] = "5"
    response = self.app.patch_json(req_path, data, status=422)

    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": [{
                    "requirements": [{
                        "expectedValue": ["Value '5' is not int."]
                    }]
                }]
            }]
        }]
    )

    requirement["expectedValue"] = 5.5
    response = self.app.patch_json(req_path, data, status=422)

    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": [{
                    "requirements": [{
                        "expectedValue": ["Value '5.5' is not int."]
                    }]
                }]
            }]
        }]
    )

    # Test dataType == "number"

    requirement["dataType"] = "number"

    requirement["expectedValue"] = "5.5"
    response = self.app.patch_json(req_path, data, status=422)

    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": [{
                    "requirements": [{
                        "expectedValue": ["Number '5.5' failed to convert to a decimal."]
                    }]
                }]
            }]
        }]
    )

    # Test dataType == "boolean"

    requirement["dataType"] = "boolean"

    requirement["expectedValue"] = "False"
    response = self.app.patch_json(req_path, data, status=422)

    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": [{
                    "requirements": [{
                        "expectedValue": ["Value 'False' is not boolean."]
                    }]
                }]
            }]
        }]
    )

    requirement["expectedValue"] = 1
    response = self.app.patch_json(req_path, data, status=422)

    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": [{
                    "requirements": [{
                        "expectedValue": ["Value '1' is not boolean."]
                    }]
                }]
            }]
        }]
    )

    # dataType == "string" for expectedValues
    del requirement["expectedValue"]
    requirement["dataType"] = "string"

    requirement["expectedValues"] = ["hello", 11, "world"]
    response = self.app.patch_json(req_path, data, status=422)

    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": [{
                    "requirements": [{
                        "expectedValues": ["Couldn't interpret '11' as string."]
                    }]
                }]
            }]
        }]
    )

    # dataType == "integer" for expectedValues
    requirement["dataType"] = "integer"

    requirement["expectedValues"] = [5, "6", 7]
    response = self.app.patch_json(req_path, data, status=422)

    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": [{
                    "requirements": [{
                        "expectedValues": ["Value '6' is not int."]
                    }]
                }]
            }]
        }]
    )

    # Test dataType == "boolean" for expectedValues

    requirement["dataType"] = "boolean"

    requirement["expectedValues"] = [True, False, "False"]
    response = self.app.patch_json(req_path, data, status=422)

    self.assertEqual(
        response.json["errors"],
        [{
            "location": "body",
            "name": "criteria",
            "description": [{
                "requirementGroups": [{
                    "requirements": [{
                        "expectedValues": ["Value 'False' is not boolean."]
                    }]
                }]
            }]
        }]
    )


def create_tender_in_not_draft_status(self):
    data = self.initial_data.copy()
    forbidden_statuses = ("draft.unsuccessful", "active.tendering", "active.qualification", "active.awarded",
                          "complete", "cancelled", "unsuccessful")
    for forbidden_status in forbidden_statuses:
        data.update({"status": forbidden_status})
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
        self.assertEqual(response.json["errors"][0]["name"], "status")


def tender_period_update(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    update = {
        "tenderPeriod": {
            "startDate": tender["tenderPeriod"]["startDate"],
            "endDate": (get_now() + timedelta(seconds=1)).isoformat(),
        }
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": update},
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
        }]
    )


def tender_owner_can_change_in_draft(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    pq_entity = deepcopy(tender["procuringEntity"])
    pq_entity["name"] = "Національне управління справами"
    general = {
        "tenderPeriod": {
            "startDate": tender["tenderPeriod"]["startDate"],
            "endDate": (get_now() + timedelta(days=14)).isoformat(),
        },
        "procuringEntity": pq_entity,
        "mainProcurementCategory": "services",
    }
    descriptions = {
        "description": "Some text 1",
        "description_en": "Some text 2",
        "description_ru": "Some text 3",
        "procurementMethodRationale": "Some text 4",
        "procurementMethodRationale_en": "Some text 5",
        "procurementMethodRationale_ru": "Some text 6",
    }
    titles = {
        "title": "Test title 1",
        "title_en": "Test title 2",
        "title_ru": "Test title 3"
    }
    criterias = {
        "eligibilityCriteria": "Test criteria 1",
        "eligibilityCriteria_en": "Test criteria 2",
        "eligibilityCriteria_ru": "Test criteria 3",
        "awardCriteriaDetails": "Test criteria 4",
        "awardCriteriaDetails_en": "Test criteria 5",
        "awardCriteriaDetails_ru": "Test criteria 6"
    }
    buyer_id = uuid4().hex

    items = deepcopy(tender["items"])
    items[0]["description"] = "New description"
    lists = {
        "buyers": [
            {
                "id": buyer_id,
                "name": "John Doe",
                "identifier": {
                    "scheme": "AE-DCCI",
                    "id": "AE1"
                }
            }
        ],
        "funders": [
            {
                "name": "First funder",
                "identifier": {
                    "scheme": "XM-DAC",
                    "id": "44000"
                },
                "address": {
                    "countryName": "Японія"
                },
                "contactPoint": {
                    "name": "Funder name",
                    "email": "fake_japan_email@gmail.net"
                }
            }
        ],
        "items": items
    }
    status = {
        "status": "draft.publishing"
    }

    # general
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": general}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender["mainProcurementCategory"], general["mainProcurementCategory"])
    self.assertNotEqual(tender["mainProcurementCategory"], data.get("mainProcurementCategory"))
    self.assertEqual(tender["tenderPeriod"]["endDate"], general["tenderPeriod"]["endDate"])
    self.assertNotEqual(tender["tenderPeriod"]["endDate"], data.get("tenderPeriod", {}).get("endDate"))
    self.assertEqual(tender["procuringEntity"]["name"], general["procuringEntity"]["name"])
    self.assertNotEqual(tender["procuringEntity"]["name"], data.get("procuringEntity", {}).get("name"))

    # descriptions
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": descriptions}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender["description"], descriptions["description"])
    self.assertNotEqual(tender["description"], data.get("description"))
    self.assertEqual(tender["description_en"], descriptions["description_en"])
    self.assertNotEqual(tender["description_en"], data.get("description_en"))
    self.assertEqual(tender["description_ru"], descriptions["description_ru"])
    self.assertNotEqual(tender["description_ru"], data.get("description_ru"))
    self.assertEqual(tender["procurementMethodRationale"], descriptions["procurementMethodRationale"])
    self.assertNotEqual(tender["procurementMethodRationale"], data.get("procurementMethodRationale"))
    self.assertEqual(tender["procurementMethodRationale_en"], descriptions["procurementMethodRationale_en"])
    self.assertNotEqual(tender["procurementMethodRationale_en"], data.get("procurementMethodRationale_en"))
    self.assertEqual(tender["procurementMethodRationale_ru"], descriptions["procurementMethodRationale_ru"])
    self.assertNotEqual(tender["procurementMethodRationale_ru"], data.get("procurementMethodRationale_ru"))

    # titles
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": titles}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender["title"], titles["title"])
    self.assertNotEqual(tender["title"], data.get("title"))
    self.assertEqual(tender["title_en"], titles["title_en"])
    self.assertNotEqual(tender["title_en"], data.get("title_en"))
    self.assertEqual(tender["title_ru"], titles["title_ru"])
    self.assertNotEqual(tender["title_ru"], data.get("title_ru"))

    # criterias
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": criterias}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender["eligibilityCriteria"], criterias["eligibilityCriteria"])
    self.assertNotEqual(tender["eligibilityCriteria"], data.get("eligibilityCriteria"))
    self.assertEqual(tender["eligibilityCriteria_en"], criterias["eligibilityCriteria_en"])
    self.assertNotEqual(tender["eligibilityCriteria_en"], data.get("eligibilityCriteria_en"))
    self.assertEqual(tender["eligibilityCriteria_ru"], criterias["eligibilityCriteria_ru"])
    self.assertNotEqual(tender["eligibilityCriteria_ru"], data.get("eligibilityCriteria_ru"))
    self.assertEqual(tender["awardCriteriaDetails"], criterias["awardCriteriaDetails"])
    self.assertNotEqual(tender["awardCriteriaDetails"], data.get("awardCriteriaDetails"))
    self.assertEqual(tender["awardCriteriaDetails_en"], criterias["awardCriteriaDetails_en"])
    self.assertNotEqual(tender["awardCriteriaDetails_en"], data.get("awardCriteriaDetails_en"))
    self.assertEqual(tender["awardCriteriaDetails_ru"], criterias["awardCriteriaDetails_ru"])
    self.assertNotEqual(tender["awardCriteriaDetails_ru"], data.get("awardCriteriaDetails_ru"))

    # lists
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": lists}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender["funders"], lists["funders"])
    buyer_id = tender["buyers"][0]["id"]
    lists["buyers"][0]["id"] = buyer_id

    self.assertEqual(tender["buyers"], lists["buyers"])

    self.assertEqual(tender["items"][0]["description"], lists["items"][0]["description"])

    # status
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": status},
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
    items[0]["relatedBuyer"] = buyer_id
    patch_data = {
        "items": items,
        "criteria": self.test_criteria_1,
    }
    patch_data.update(status)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": patch_data
        },
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender["status"], status["status"])
    self.assertNotEqual(tender["status"], data["status"])


def tender_owner_cannot_change_in_draft(self):
    data = self.initial_data.copy()
    data.update({"status": "draft"})
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    token = response.json["access"]["token"]
    self.assertEqual(tender["status"], "draft")

    # general
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {
            "tenderID": "Some id",
            "procurementMethodType": "belowThreshold",
            "procurementMethod": "selective",
            "submissionMethod": "written",
            "mode": "test"
        }},
        status=422
    )
    self.assertCountEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "mode",
                "description": "Rogue field"
            },
            {
                "location": "body",
                "name": "tenderID",
                "description": "Rogue field"
            },
            {
                "location": "body",
                "name": "procurementMethodType",
                "description": "Rogue field"
            }
        ]
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {
            "submissionMethod": "written",
        }},
        status=422
    )

    # owner
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {
            "owner": "Test owner",
            "transfer_token": "17bc682ec79245bca7d9cdbabbfce8f8",
            "owner_token": "17bc682ec79245bca7d9cdbabbfce8f7"
        }},
        status=422
    )
    self.assertCountEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "owner_token",
                "description": "Rogue field"
            },
            {
                "location": "body",
                "name": "transfer_token",
                "description": "Rogue field"
            },
            {
                "location": "body",
                "name": "owner",
                "description": "Rogue field"
            }
        ]
    )

    # time
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {
            "date": (get_now() + timedelta(days=1)).isoformat(),
            "dateModified": (get_now() + timedelta(days=1)).isoformat(),
        }},
        status=422
    )
    self.assertCountEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "date",
                "description": "Rogue field"
            },
            {
                "location": "body",
                "name": "dateModified",
                "description": "Rogue field"
            }
        ]
    )

    # lists
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {
            "revisions": [{"author": "Some author"}],
            "plans": [{"id": uuid4().hex}],
            "cancellations": [
                {
                    "reason": "Some reason",
                    "reasonType": "noDemand"
                }
            ],
        }},
        status=422
    )
    self.assertCountEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "revisions",
                "description": "Rogue field"
            },
            {
                "location": "body",
                "name": "cancellations",
                "description": "Rogue field"
            }
        ]
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
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json,
        {"status": "error", "errors": [{"location": "body", "name": "guarantee", "description": "Rogue field"}]}
    )

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

    for kind in PQ_KINDS:
        data = deepcopy(self.initial_data)
        data['procuringEntity']['kind'] = kind
        response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(
            response.json['data']['procuringEntity']['kind'],
            kind
        )


def tender_fields(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    self.assertEqual(
        set(tender) - set(self.initial_data),
        {
            "id",
            "dateModified",
            "dateCreated",
            "tenderID",
            "date",
            "status",
            "awardCriteria",
            "owner",
        },
    )
    self.assertIn(tender["id"], response.headers["Location"])


def patch_tender(self):
    data = self.initial_data.copy()
    data["procuringEntity"]["contactPoint"]["faxNumber"] = "+0440000000"
    response = self.app.get("/tenders")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    owner_token = response.json["access"]["token"]
    dateModified = tender.pop("dateModified")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"milestones": test_tender_pq_milestones}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{
            "location": "body",
            "name": "milestones",
            "description": "Rogue field"
        }],
    )

    pq_entity = deepcopy(tender["procuringEntity"])
    pq_entity["kind"] = "defense"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"procuringEntity": pq_entity}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["procuringEntity"]["kind"], "defense")
    tender["procuringEntity"]['kind'] = "defense"

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

    data = deepcopy(item0)
    data["classification"] = {
        "scheme": "ДК021",
        "id": "55523100-3",
        "description": "Послуги з харчування у школах",
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {
            "data": {
                "items": [data]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"guarantee": {"amount": 12, "valueAddedTaxIncluded": True}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0],
        {
            "location": "body",
            "name": "guarantee",
            "description": "Rogue field"
        }
    )


@mock.patch("openprocurement.tender.core.models.CANT_DELETE_PERIOD_START_DATE_FROM", get_now() - timedelta(days=1))
def required_field_deletion(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"tenderPeriod": {
            "startDate": None,
            "endDate": tender["tenderPeriod"]["endDate"],
        }}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": {"startDate": ["This field is required."]},
                "location": "body",
                "name": "tenderPeriod",
            }
        ],
    )


def patch_tender_status(self):
    cur_status = "draft.publishing"
    patch_status = "cancelled"
    self.create_tender()
    self.set_status(cur_status)
    data = {"data": {
        "status": patch_status,
        }
    }
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), data, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": f"Can't update tender in current (draft.publishing) status"
            }

        ],
    )


@mock.patch("openprocurement.tender.pricequotation.procedure.models.tender.PQ_MULTI_PROFILE_FROM",
            get_now() + timedelta(days=1))
@mock.patch("openprocurement.tender.pricequotation.procedure.models.item.PQ_MULTI_PROFILE_FROM",
            get_now() + timedelta(days=1))
def patch_tender_by_pq_bot_before_multiprofile(self):
    response = self.app.post_json("/tenders", {
        "data": deepcopy(test_tender_pq_data_before_multiprofile),
        "config": self.initial_config,
    })
    self.assertEqual(response.status, "201 Created")
    tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender = response.json["data"]

    self.assertEqual(tender["status"], "draft")
    self.assertEqual(len(tender["items"]), 1)
    self.assertNotIn("shortlistedFirms", tender)

    data = {"data": {
        "status": "draft.publishing",
        "profile": test_tender_pq_short_profile["id"],
        "criteria": self.test_criteria_1}
    }
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender_id, owner_token), data)
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "draft.publishing")
    self.assertEqual(tender["profile"], test_tender_pq_short_profile["id"])

    items = deepcopy(tender["items"])
    items[0]["classification"] = test_tender_pq_short_profile["classification"]
    items[0]["unit"] = test_tender_pq_short_profile["unit"]
    amount = sum([item["quantity"] for item in items]) * test_tender_pq_short_profile["value"]["amount"]
    value = deepcopy(test_tender_pq_short_profile["value"])
    value["amount"] = amount
    criteria = deepcopy(test_tender_pq_short_profile["criteria"])
    data = {
        "data": {
            "status": "active.tendering",
            "items": items,
            "shortlistedFirms": test_tender_pq_shortlisted_firms,
            "criteria": criteria,
            "value": value
        }
    }

    # try to patch by user
    for patch in ({'data': {'status': 'active.tendering'}}, data):
        with change_auth(self.app, ("Basic", ("broker", ""))) as app:
            resp = app.patch_json("/tenders/{}?acc_token={}".format(tender_id, owner_token), patch, status=403)
            self.assertEqual(resp.status, "403 Forbidden")
            self.assertEqual(resp.json['status'], "error")
            self.assertEqual(resp.json['errors'], [
                {'description': "Can't update tender in current (draft.publishing) status",
                 'location': 'body',
                 'name': 'data'}
            ])

    # patch by bot
    with change_auth(self.app, ("Basic", ("pricequotation", ""))) as app:
        resp = app.patch_json("/tenders/{}".format(tender_id), data)
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], data["data"]["status"])
    self.assertIn("classification", tender["items"][0])
    self.assertIn("unit", tender["items"][0])
    self.assertEqual(len(tender["shortlistedFirms"]), len(test_tender_pq_shortlisted_firms))
    self.assertEqual(len(tender["criteria"]), len(test_tender_pq_short_profile["criteria"]))
    self.assertEqual(tender["value"], value)

    # switch tender to `draft.unsuccessful`
    response = self.app.post_json("/tenders", {
        "data": deepcopy(test_tender_pq_data_before_multiprofile),
        "config": self.initial_config,
    })
    self.assertEqual(response.status, "201 Created")
    tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender = response.json["data"]

    self.assertEqual(tender["status"], "draft")
    self.assertEqual(len(tender["items"]), 1)
    self.assertNotIn("shortlistedFirms", tender)

    data = {"data": {"status": "draft.publishing", "profile": "a1b2c3-a1b2c3e4-f1g2i3-h1g2k3l4"}}
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender_id, owner_token), data, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "profile", "description": ["The profile value doesn't match id pattern"]}]
    )

    # set not existed profile id
    data["data"]["profile"] = "123456-12345678-123456-12345678"
    data["data"]["criteria"] = self.test_criteria_1
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender_id, owner_token), data)
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "draft.publishing")
    self.assertEqual(tender["profile"], "123456-12345678-123456-12345678")

    with change_auth(self.app, ("Basic", ("pricequotation", ""))) as app:
        self.app.patch_json(
            "/tenders/{}".format(tender_id),
            {"data": {"status": "draft.unsuccessful", "unsuccessfulReason": ["Profile not found in catalogue"]}}
        )

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "draft.unsuccessful")
    self.assertEqual(tender["unsuccessfulReason"], ["Profile not found in catalogue"])
    self.assertNotIn("shortlistedFirms", tender)


@mock.patch("openprocurement.tender.pricequotation.models.tender.PQ_MULTI_PROFILE_FROM", get_now() - timedelta(days=1))
def patch_tender_by_pq_bot_after_multiprofile(self):
    response = self.app.post_json("/tenders", {
        "data": deepcopy(test_tender_pq_data_after_multiprofile),
        "config": self.initial_config,
    })
    self.assertEqual(response.status, "201 Created")
    tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender = response.json["data"]

    self.assertEqual(tender["status"], "draft")
    self.assertEqual(len(tender["items"]), 1)
    self.assertNotIn("shortlistedFirms", tender)
    self.assertIn("classification", tender["items"][0])
    self.assertIn("additionalClassifications", tender["items"][0])

    test_agreement = {
        "id": self.agreement_id,
    }

    data = {
        "data": {
            "status": "draft.publishing",
            "agreement": test_agreement,
            "criteria": test_tender_pq_short_profile["criteria"]
        }
    }
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender_id, owner_token), data)
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "draft.publishing")
    self.assertEqual(tender["agreement"], test_agreement)
    expected_criteria = deepcopy(test_tender_pq_short_profile["criteria"])
    for c in expected_criteria:
        c.update(id=mock.ANY)

        for g in c.get("requirementGroups"):
            g.update(id=mock.ANY)

            for r in g.get("requirements"):
                r.update(id=mock.ANY)

    self.assertEqual(tender["criteria"], expected_criteria)

    amount = sum([item["quantity"] for item in tender["items"]]) * test_tender_pq_short_profile["value"]["amount"]
    value = deepcopy(test_tender_pq_short_profile["value"])
    value["amount"] = amount

    data = {
        "data": {
            "value": value,
            "status": "active.tendering",
            "shortlistedFirms": test_tender_pq_shortlisted_firms,
        }
    }

    # try to patch by user
    for patch in ({'data': {'status': 'active.tendering'}}, data):
        with change_auth(self.app, ("Basic", ("broker", ""))) as app:
            resp = app.patch_json("/tenders/{}?acc_token={}".format(tender_id, owner_token), patch, status=403)
            self.assertEqual(resp.status, "403 Forbidden")
            self.assertEqual(resp.json['status'], "error")
            self.assertEqual(resp.json['errors'], [
                {
                    "location": "body",
                    "name": "data",
                    "description": "Can't update tender in current (draft.publishing) status"
                }
            ])

    # patch by bot
    with change_auth(self.app, ("Basic", ("pricequotation", ""))) as app:
        resp = app.patch_json("/tenders/{}".format(tender_id), data)
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], data["data"]["status"])
    self.assertEqual(len(tender["shortlistedFirms"]), len(test_tender_pq_shortlisted_firms))
    self.assertEqual(tender["value"], value)

    # switch tender to `draft.unsuccessful`
    response = self.app.post_json("/tenders", {
        "data": deepcopy(test_tender_pq_data_after_multiprofile),
        "config": self.initial_config,
    })
    self.assertEqual(response.status, "201 Created")
    tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    tender = response.json["data"]

    self.assertEqual(tender["status"], "draft")
    self.assertEqual(len(tender["items"]), 1)
    self.assertNotIn("shortlistedFirms", tender)

    items = deepcopy(tender["items"])
    items[0]["profile"] = "a1b2c3-a1b2c3e4-f1g2i3-h1g2k3l4"
    data = {"data": {"status": "draft.publishing", "items": items}}
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender_id, owner_token), data, status=422)
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "items", "description": [{"profile": ["The profile value doesn't match id pattern"]}]}]
    )

    # set not existed profile id
    data["data"]["items"][0]["profile"] = "123456-12345678-123456-12345678"
    data["data"]["criteria"] = self.test_criteria_1
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender_id, owner_token), data)
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "draft.publishing")
    self.assertEqual(tender["items"][0]["profile"], "123456-12345678-123456-12345678")

    with change_auth(self.app, ("Basic", ("pricequotation", ""))):
        self.app.patch_json(
            "/tenders/{}".format(tender_id),
            {"data": {"status": "draft.unsuccessful", "unsuccessfulReason": ["Profile not found in catalogue"]}}
        )

    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.status, "200 OK")
    tender = response.json["data"]
    self.assertEqual(tender["status"], "draft.unsuccessful")
    self.assertEqual(tender["unsuccessfulReason"], ["Profile not found in catalogue"])
    self.assertNotIn("shortlistedFirms", tender)


def invalid_tender_conditions(self):
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # switch to active.tendering
    self.set_status("active.tendering")
    # cancellation
    cancellation = dict(**test_tender_pq_cancellation)
    cancellation.update({
        "reason": "invalid conditions",
        "reasonType": "noDemand",
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {"data": {
            "title": "name.doc",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/msword",
        }},
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(tender_id, cancellation_id, owner_token),
        {"data": {"status": "active"}},
    )

    # check status
    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def one_valid_bid_tender(self):
    tender_id = self.tender_id
    owner_token = self.tender_token
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    resp = self.app.post_json(
        "/tenders/{}/bids".format(tender_id), {"data": {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": test_tender_pq_requirement_response,
        }}
    )
    token = resp.json['access']['token']
    # switch to active.qualification
    self.set_status("active.qualification")
    response = self.check_chronograph()
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    award_date = [i["date"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, token),
        {"data": {"status": "active"}}
    )
    self.assertNotEqual(response.json["data"]["date"], award_date)

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
    # after stand slill period
    self.set_status("active.awarded", 'end')
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
    tender_id = self.tender_id
    owner_token = self.tender_token
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid, token = self.create_bid(
        self.tender_id,
        {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": test_tender_pq_requirement_response,
        },
    )
    # switch to active.qualification
    self.set_status('active.tendering', 'end')
    resp = self.check_chronograph()
    self.assertEqual(resp.json['data']['status'], 'active.qualification')
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, token),
        {"data": {"status": "unsuccessful"}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def first_bid_tender(self):
    tender_id =  self.tender_id
    owner_token = self.tender_token
    # create bid
    bid, bid_token1 = self.create_bid(
        self.tender_id,
        {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 450},
            "requirementResponses": test_tender_pq_requirement_response,
        },
    )
    bid_1 = bid["id"]

    # create second bid
    bid, bid_token2 = self.create_bid(
        self.tender_id,
        {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 300},
            "requirementResponses": test_tender_pq_requirement_response,
        },
    )
    bid_2 = bid["id"]
    self.set_status('active.tendering', 'end')
    resp = self.check_chronograph()
    self.assertEqual(resp.json['data']['status'], 'active.qualification')
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award = [i for i in response.json["data"] if i["status"] == "pending"][0]
    award_id = award['id']
    self.assertEqual(award['bid_id'], bid_2)
    self.assertEqual(award['value']['amount'], 300)
    # set award as unsuccessful
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, bid_token2),
        {"data": {"status": "unsuccessful"}},
    )
    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award = [i for i in response.json["data"] if i["status"] == "pending"][0]
    award2_id = award['id']
    self.assertEqual(award['bid_id'], bid_1)
    self.assertEqual(award['value']['amount'], 450)
    self.assertNotEqual(award_id, award2_id)

    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, bid_token1),
        {"data": {"status": "active"}}
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
    tender_id = self.tender_id
    owner_token = self.tender_token
    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid, token = self.create_bid(
        self.tender_id,
        {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": test_tender_pq_requirement_response,
        },
    )
    # switch to active.qualification
    self.set_status("active.tendering", 'end')
    resp = self.check_chronograph().json
    self.assertEqual(resp['data']['status'], 'active.qualification')

    # get awards
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/awards?acc_token={}".format(tender_id, owner_token))
    # get pending award
    award_id = [i["id"] for i in response.json["data"] if i["status"] == "pending"][0]
    # set award as active
    self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, token), {"data": {"status": "active"}}
    )
    # lost contract
    tender = self.mongodb.tenders.get(tender_id)
    del tender["contracts"]
    self.mongodb.tenders.save(tender)
    # create lost contract
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    self.assertIn("contracts", response.json["data"])
    self.assertNotIn("next_check", response.json["data"])
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    contract_value = deepcopy(contract["value"])
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


def patch_items_related_buyer_id(self):
    # create tender with two buyers
    data = deepcopy(self.initial_data)
    test_organization1 = deepcopy(test_tender_pq_organization)
    test_organization2 = deepcopy(test_tender_pq_organization)
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
        {"data": {"status": self.primary_tender_status, "criteria": self.test_criteria_1}}
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
