from copy import deepcopy
from datetime import timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

from openprocurement.api.constants import (
    MILESTONE_CODES,
    MILESTONE_TITLES,
    ROUTE_PREFIX,
    SANDBOX_MODE,
)
from openprocurement.api.procedure.models.organization import ProcuringEntityKind
from openprocurement.api.utils import get_now
from openprocurement.framework.dps.constants import DPS_TYPE
from openprocurement.tender.core.tests.base import test_tech_feature_criteria
from openprocurement.tender.core.tests.criteria_utils import add_criteria
from openprocurement.tender.core.tests.mock import patch_market
from openprocurement.tender.core.tests.utils import (
    get_contract_template_name,
    set_bid_responses,
    set_tender_criteria,
)
from openprocurement.tender.pricequotation.constants import PQ, PQ_KINDS
from openprocurement.tender.pricequotation.tests.data import (
    test_agreement_pq_data,
    test_tender_pq_cancellation,
    test_tender_pq_category,
    test_tender_pq_criteria,
    test_tender_pq_data,
    test_tender_pq_item,
    test_tender_pq_milestones,
    test_tender_pq_organization,
    test_tender_pq_short_profile,
)
from openprocurement.tender.pricequotation.tests.utils import activate_econtract


def listing(self):
    response = self.app.get("/tenders")
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
    offset = response.json["next_page"]["offset"]

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

    response = self.app.get("/tenders", params=[("opt_fields", "status")])
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

    response = self.app.get("/tenders?feed=changes", params=[("opt_fields", "status")])
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
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in tenders})
    self.assertEqual({i["dateModified"] for i in response.json["data"]}, {i["dateModified"] for i in tenders})
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in tenders]))


def create_tender_invalid(self):
    request_path = "/tenders"
    self.app.post_json(
        request_path, {"data": {"procurementMethodType": "invalid_value"}, "config": self.initial_config}, status=404
    )

    response = self.app.post_json(
        request_path,
        {"data": {"invalid_field": "invalid_value", "procurementMethodType": PQ}, "config": self.initial_config},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(
        request_path,
        {"data": {"value": "invalid_value", "procurementMethodType": PQ}, "config": self.initial_config},
        status=422,
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
        request_path,
        {"data": {"procurementMethod": "invalid_value", "procurementMethodType": PQ}, "config": self.initial_config},
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

    data = deepcopy(self.initial_data)
    data["procurementMethod"] = "open"
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn(
        {
            "description": "procurementMethod should be selective",
            "location": "body",
            "name": "procurementMethod",
        },
        response.json["errors"],
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

    data = self.initial_data["items"][0].pop("additionalClassifications")
    cpv_code = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "99999999-9"

    response = self.app.post_json(
        request_path,
        {
            "data": self.initial_data,
            "config": self.initial_config,
        },
        status=201,
    )
    self.initial_data["items"][0]["additionalClassifications"] = data
    self.initial_data["items"][0]["classification"]["id"] = cpv_code
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "201 Created")

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

    cpv = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "160173000-1"
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["items"][0]["classification"]["id"] = cpv
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("classification", response.json["errors"][0]["description"][0])
    self.assertIn("id", response.json["errors"][0]["description"][0]["classification"])
    self.assertEqual(
        response.json["errors"][0]["description"][0]["classification"]["id"][0], "Value must be one of ДК021 codes"
    )

    cpv = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "00000000-0"
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["items"][0]["classification"]["id"] = cpv
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertIn("classification", response.json["errors"][0]["description"][0])
    self.assertIn("id", response.json["errors"][0]["description"][0]["classification"])
    self.assertEqual(
        response.json["errors"][0]["description"][0]["classification"]["id"][0],
        "Value must be one of {} codes".format(self.initial_data["items"][0]["classification"]["scheme"]),
    )

    procuringEntity = self.initial_data["procuringEntity"]
    data = self.initial_data["procuringEntity"].copy()
    del data["kind"]
    self.initial_data["procuringEntity"] = data
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config}, status=422)
    self.initial_data["procuringEntity"] = procuringEntity
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "procuringEntity", "description": {"kind": ["This field is required."]}}],
    )

    data = deepcopy(self.initial_data)
    data["procuringEntity"]['kind'] = 'central'
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "procuringEntity",
                "description": {
                    "kind": [
                        "Value must be one of [\'general\', \'special\', \'defense\', \'other\', \'social\', \'authority\']."
                    ]
                },
            }
        ],
    )

    data = deepcopy(test_tender_pq_data)
    data["agreement"]["id"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": {"id": ["Hash value is wrong length."]}, "location": "body", "name": "agreement"}],
    )

    data["agreement"]["id"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Agreement not found",
                "location": "body",
                "name": "agreement",
            }
        ],
    )

    del data["agreement"]["id"]
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": {"id": ["This field is required."]}, "location": "body", "name": "agreement"}],
    )

    del data["agreement"]
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["This field is required."], "location": "body", "name": "agreement"}],
    )

    # try to post tender with items without profile
    data = deepcopy(self.initial_data)
    data["items"] = [deepcopy(test_tender_pq_item)]
    del data["items"][0]["profile"]
    data["value"] = {'amount': 500001, 'currency': 'UAH'}
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(response.status, '422 Unprocessable Entity')
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": [{"profile": ["This field is required."]}], "location": "body", "name": "items"}],
    )

    data["procuringEntity"]["kind"] = ProcuringEntityKind.SPECIAL
    response = self.app.post_json(request_path, {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, '201 Created')


def create_tender_with_inn(self):
    request_path = "/tenders"

    addit_classif = [
        {"scheme": "INN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"}
    ]
    data = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "33611000-6"
    self.initial_data["contractTemplateName"] = get_contract_template_name(self.initial_data)
    orig_addit_classif = self.initial_data["items"][0]["additionalClassifications"]
    self.initial_data["items"][0]["additionalClassifications"] = addit_classif
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config})
    self.initial_data["items"][0]["additionalClassifications"] = orig_addit_classif
    self.initial_data["items"][0]["classification"]["id"] = data
    self.initial_data["contractTemplateName"] = get_contract_template_name(self.initial_data)
    self.assertEqual(response.status, "201 Created")

    addit_classif = [
        {"scheme": "NotINN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
        {"scheme": "NotINN", "id": "17.21.1", "description": "папір і картон гофровані, паперова й картонна тара"},
    ]
    data = self.initial_data["items"][0]["classification"]["id"]
    self.initial_data["items"][0]["classification"]["id"] = "33652000-5"
    self.initial_data["contractTemplateName"] = get_contract_template_name(self.initial_data)
    orig_addit_classif = self.initial_data["items"][0]["additionalClassifications"]
    self.initial_data["items"][0]["additionalClassifications"] = addit_classif
    response = self.app.post_json(request_path, {"data": self.initial_data, "config": self.initial_config})
    self.initial_data["items"][0]["additionalClassifications"] = orig_addit_classif
    self.initial_data["items"][0]["classification"]["id"] = data
    self.initial_data["contractTemplateName"] = get_contract_template_name(self.initial_data)
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
        "agreement",
        "contractTemplateName",
    ]

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
        status=422,
    )

    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': ['tenderPeriod must be at least 2 full business days long'],
                'location': 'body',
                'name': 'tenderPeriod',
            }
        ],
    )

    forbidden_statuses = (
        "active.qualification",
        "active.awarded",
        "complete",
        "cancelled",
        "unsuccessful",
    )
    current_status = tender["status"]
    for forbidden_status in forbidden_statuses:
        response = self.app.patch_json(
            "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"status": forbidden_status}}, status=422
        )
        self.assertEqual(response.json['status'], "error")
        self.assertEqual(response.json['errors'][0]["name"], "status")

    pq_entity = deepcopy(tender["procuringEntity"])
    pq_entity["kind"] = "central"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token), {"data": {"procuringEntity": pq_entity}}, status=422
    )
    self.assertEqual(
        response.json['errors'],
        [
            {
                "location": "body",
                "name": "procuringEntity",
                "description": {
                    "kind": ["Value must be one of ['general', 'special', 'defense', 'other', 'social', 'authority']."]
                },
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"status": self.primary_tender_status, "unsuccessfulReason": ["some value from buyer"]}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "unsuccessfulReason", "description": "Rogue field"}]
    )

    test_criteria = deepcopy(test_tender_pq_criteria)
    set_tender_criteria(test_criteria, tender.get("lots", []), tender.get("items", []))

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": {
                "status": self.primary_tender_status,
                "criteria": test_criteria,
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "documents",
                "description": "Document with type 'notice' and format pkcs7-signature is required",
            }
        ],
    )
    self.add_sign_doc(tender["id"], token)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": {
                "status": self.primary_tender_status,
                "criteria": test_criteria,
            }
        },
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

    test_criteria = deepcopy(test_tender_pq_criteria)
    set_tender_criteria(test_criteria, data.get("lots", []), data.get("items", []))

    data["criteria"] = test_criteria
    data["status"] = "draft"

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    tender = response.json["data"]
    tender_id = tender["id"]
    token = response.json["access"]["token"]

    self.assertEqual({e["description"] for e in tender["criteria"]}, {e["description"] for e in data["criteria"]})

    # try updating criteria ids
    patch_criteria = deepcopy(tender["criteria"])
    for c in patch_criteria:
        c["id"] = uuid4().hex

    response = self.app.patch_json(f"/tenders/{tender_id}?acc_token={token}", {"data": {"criteria": patch_criteria}})
    patch_result = response.json["data"]
    self.assertEqual({e["id"] for e in patch_result["criteria"]}, {e["id"] for e in patch_criteria})

    # try adding a new criteria
    patch_criteria = patch_criteria + deepcopy(patch_criteria)

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}", {"data": {"criteria": patch_criteria}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "criteria", "description": ["Criteria id should be uniq"]}],
    )

    for c in patch_criteria:
        c["id"] = uuid4().hex
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}", {"data": {"criteria": patch_criteria}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "criteria",
                "description": ["Requirement group id should be uniq in tender"],
            }
        ],
    )

    # fix group ids
    for c in patch_criteria:
        for g in c["requirementGroups"]:
            g["id"] = uuid4().hex
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}", {"data": {"criteria": patch_criteria}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "criteria",
                "description": ["Requirement id should be uniq for all requirements in tender"],
            }
        ],
    )

    # fix requirement ids
    for i, c in enumerate(patch_criteria):
        c["classification"]["id"] += str(i)
        for g in c["requirementGroups"]:
            for r in g["requirements"]:
                r["id"] = uuid4().hex

    new_req = deepcopy(test_criteria[0]["requirementGroups"][0]["requirements"][0])

    patch_criteria[0]["requirementGroups"][0]["requirements"].append(new_req)

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}", {"data": {"criteria": patch_criteria}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "criteria",
                "description": ["Requirement title should be uniq for one requirementGroup"],
            }
        ],
    )

    # change status
    patch_criteria[0]["requirementGroups"][0]["requirements"][-1]["status"] = "cancelled"

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}",
        {"data": {"criteria": patch_criteria}},
    )
    patch_result = response.json["data"]

    # old object ids hasn't been changed
    self.assertEqual(len(patch_result["criteria"]), 2)
    self.assertEqual([e["id"] for e in patch_result["criteria"]], [e["id"] for e in patch_criteria])

    # check unique criteria classification ids
    criterion_1 = deepcopy(test_criteria[0])
    criterion_2 = deepcopy(test_criteria[0])

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}", {"data": {"criteria": [criterion_1, criterion_2]}}, status=403
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Criteria are not unique",
            }
        ],
    )


def create_tender_draft_with_criteria_expected_values(self):
    data = self.initial_data.copy()

    test_criteria = deepcopy(test_tender_pq_criteria)
    set_tender_criteria(test_criteria, data.get("lots", []), data.get("items", []))

    test_additional_criteria = deepcopy(test_tech_feature_criteria)
    set_tender_criteria(test_additional_criteria, data.get("lots", []), data.get("items", []))
    test_additional_criteria[0]["classification"]["id"] = "CRITERION.TEST"
    test_additional_criteria[0]["requirementGroups"][0]["requirements"] = [
        {
            "dataType": "string",
            "expectedValues": ["Розчин для інфузій"],
            "title": "Форма випуску",
            "expectedMinItems": 1,
        },
        {
            "dataType": "integer",
            "minValue": 5,
            "title": "Доза діючої речовини",
            "unit": {"code": "KGM", "name": "кілограми"},
        },
    ]

    test_criteria = test_criteria + test_additional_criteria

    data["criteria"] = test_criteria
    data["status"] = "draft"

    test_requirement = {
        "dataType": "string",
        "expectedValues": ["Відповідь1", "Відповідь2", "Відповідь3", "Відповідь4"],
        "expectedMinItems": 1,
        "expectedMaxItems": 3,
        "id": "400496-0003-001-01",
        "title": "Форма випуску",
    }

    test_criteria[-1]["requirementGroups"][0]["requirements"][0] = test_requirement

    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    tender = response.json["data"]
    tender_id = tender["id"]
    token = response.json["access"]["token"]

    self.assertEqual({e["description"] for e in tender["criteria"]}, {e["description"] for e in data["criteria"]})

    tender_criteria = tender["criteria"]

    patch_failed_criteria = deepcopy(tender_criteria)
    patch_failed_criteria[-1]["requirementGroups"][0]["requirements"][0]["expectedValue"] = "value"
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}", {"data": {"criteria": patch_failed_criteria}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "criteria",
                "description": [
                    {
                        "requirementGroups": [
                            {
                                "requirements": [
                                    {
                                        "expectedValue": [
                                            "expectedValue conflicts with ['minValue', 'maxValue', 'expectedValues']",
                                        ],
                                        "expectedValues": [
                                            "expectedValues conflicts with ['minValue', 'maxValue', 'expectedValue']",
                                        ],
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        ],
    )

    patch_failed_criteria = deepcopy(tender_criteria)
    patch_failed_criteria[-1]["requirementGroups"][0]["requirements"][0]["minValue"] = 2
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}", {"data": {"criteria": patch_failed_criteria}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "criteria",
                "description": [
                    {
                        "requirementGroups": [
                            {
                                "requirements": [
                                    {
                                        "minValue": [
                                            "minValue must be integer or number",
                                        ],
                                        "expectedValues": [
                                            "expectedValues conflicts with ['minValue', 'maxValue', 'expectedValue']",
                                        ],
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        ],
    )

    patch_failed_criteria = deepcopy(tender_criteria)
    patch_failed_criteria[-1]["requirementGroups"][0]["requirements"][0]["expectedValues"] = None
    patch_failed_criteria[-1]["requirementGroups"][0]["requirements"][0]["expectedValue"] = "value"
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}", {"data": {"criteria": patch_failed_criteria}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "criteria",
                "description": [
                    {
                        "requirementGroups": [
                            {
                                "requirements": [
                                    {
                                        "expectedValues": [
                                            "expectedMinItems and expectedMaxItems couldn't exist without expectedValues",
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        ],
    )

    patch_failed_criteria = deepcopy(tender_criteria)
    patch_failed_criteria[-1]["requirementGroups"][0]["requirements"][0]["expectedMinItems"] = 4
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}", {"data": {"criteria": patch_failed_criteria}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "criteria",
                "description": [
                    {
                        "requirementGroups": [
                            {
                                "requirements": [
                                    {
                                        "expectedValues": [
                                            "expectedMinItems couldn't be higher then expectedMaxItems",
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        ],
    )

    patch_failed_criteria = deepcopy(tender_criteria)
    patch_failed_criteria[-1]["requirementGroups"][0]["requirements"][0]["expectedMinItems"] = 5
    patch_failed_criteria[-1]["requirementGroups"][0]["requirements"][0]["expectedMaxItems"] = None
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}", {"data": {"criteria": patch_failed_criteria}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "criteria",
                "description": [
                    {
                        "requirementGroups": [
                            {
                                "requirements": [
                                    {
                                        "expectedValues": [
                                            "expectedMinItems couldn't be higher then count of items in expectedValues"
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        ],
    )

    patch_failed_criteria = deepcopy(tender_criteria)
    patch_failed_criteria[-1]["requirementGroups"][0]["requirements"][0]["expectedMaxItems"] = 5
    patch_failed_criteria[-1]["requirementGroups"][0]["requirements"][0]["expectedMinItems"] = None
    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={token}", {"data": {"criteria": patch_failed_criteria}}, status=422
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "criteria",
                "description": [
                    {
                        "requirementGroups": [
                            {
                                "requirements": [
                                    {
                                        "expectedValues": [
                                            "expectedMaxItems couldn't be higher then count of items in expectedValues"
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ],
            }
        ],
    )


def tender_criteria_values_type(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    tender = response.json["data"]
    tender_id = tender["id"]
    token = response.json["access"]["token"]

    req_path = f"/tenders/{tender_id}?acc_token={token}"

    test_criteria = deepcopy(test_tender_pq_criteria)
    set_tender_criteria(test_criteria, tender.get("lots", []), tender.get("items", []))

    test_additional_criteria = deepcopy(test_tech_feature_criteria)
    set_tender_criteria(test_additional_criteria, tender.get("lots", []), tender.get("items", []))
    test_additional_criteria[0]["classification"]["id"] = "CRITERION.TEST"
    test_additional_criteria[0]["requirementGroups"][0]["requirements"] = [
        {
            "title": "Test",
        }
    ]

    # Test dataType == "string"

    criteria = test_criteria + test_additional_criteria
    requirement = criteria[-1]["requirementGroups"][0]["requirements"][0]
    data = {"data": {"criteria": criteria}}

    requirement["dataType"] = "string"
    requirement["expectedValues"] = [1]
    requirement["expectedValue"] = None
    requirement["minValue"] = None
    requirement["maxValue"] = None
    requirement["expectedMinItems"] = 1
    requirement["expectedMaxItems"] = None
    requirement["unit"] = None

    response = self.app.patch_json(req_path, data)
    actual_req = response.json["data"]["criteria"][-1]["requirementGroups"][0]["requirements"][0]
    self.assertEqual(actual_req['expectedValues'], ["1"])

    requirement["expectedValues"] = [True]
    response = self.app.patch_json(req_path, data)
    actual_req = response.json["data"]["criteria"][-1]["requirementGroups"][0]["requirements"][0]
    self.assertEqual(actual_req['expectedValues'], ["True"])

    # Test dataType == "integer"
    requirement["dataType"] = "integer"
    requirement["expectedValues"] = None
    requirement["expectedValue"] = "5"
    requirement["minValue"] = None
    requirement["maxValue"] = None
    requirement["expectedMinItems"] = None
    requirement["expectedMaxItems"] = None
    requirement["unit"] = {"code": "H87", "name": "штук"}
    response = self.app.patch_json(req_path, data)
    actual_req = response.json["data"]["criteria"][-1]["requirementGroups"][0]["requirements"][0]
    self.assertEqual(actual_req['expectedValue'], 5)

    requirement["expectedValue"] = 5.5
    response = self.app.patch_json(req_path, data)
    actual_req = response.json["data"]["criteria"][-1]["requirementGroups"][0]["requirements"][0]
    self.assertEqual(actual_req['expectedValue'], 5)

    # Test dataType == "number"

    requirement["dataType"] = "number"

    requirement["expectedValue"] = "5.5"
    response = self.app.patch_json(req_path, data)
    actual_req = response.json["data"]["criteria"][-1]["requirementGroups"][0]["requirements"][0]
    self.assertEqual(actual_req['expectedValue'], 5.5)

    # Test dataType == "boolean"

    requirement["dataType"] = "boolean"
    del requirement["unit"]

    requirement["expectedValue"] = "False"
    response = self.app.patch_json(req_path, data)
    actual_req = response.json["data"]["criteria"][-1]["requirementGroups"][0]["requirements"][0]
    self.assertEqual(actual_req['expectedValue'], False)

    requirement["expectedValue"] = 1
    response = self.app.patch_json(req_path, data)
    actual_req = response.json["data"]["criteria"][-1]["requirementGroups"][0]["requirements"][0]
    self.assertEqual(actual_req['expectedValue'], True)

    # dataType == "string" for expectedValues
    del requirement["expectedValue"]
    requirement["dataType"] = "string"
    requirement["expectedMinItems"] = 1

    requirement["expectedValues"] = ["hello", 11, "world"]
    response = self.app.patch_json(req_path, data)
    actual_req = response.json["data"]["criteria"][-1]["requirementGroups"][0]["requirements"][0]
    self.assertEqual(actual_req['expectedValues'], ["hello", "11", "world"])


def create_tender_in_not_draft_status(self):
    data = self.initial_data.copy()
    forbidden_statuses = (
        "active.qualification",
        "active.awarded",
        "complete",
        "cancelled",
        "unsuccessful",
    )
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
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token), {"data": update}, status=422)
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
    titles = {"title": "Test title 1", "title_en": "Test title 2", "title_ru": "Test title 3"}
    criterias = {
        "eligibilityCriteria": "Test criteria 1",
        "eligibilityCriteria_en": "Test criteria 2",
        "eligibilityCriteria_ru": "Test criteria 3",
        "awardCriteriaDetails": "Test criteria 4",
        "awardCriteriaDetails_en": "Test criteria 5",
        "awardCriteriaDetails_ru": "Test criteria 6",
    }
    buyer_id = uuid4().hex

    items = deepcopy(tender["items"])
    items[0]["description"] = "New description"
    lists = {
        "buyers": [{"id": buyer_id, "name": "John Doe", "identifier": {"scheme": "AE-DCCI", "id": "AE1"}}],
        "funders": [
            {
                "name": "First funder",
                "identifier": {"scheme": "XM-DAC", "id": "44000"},
                "address": {"countryName": "Японія"},
                "contactPoint": {"name": "Funder name", "email": "fake_japan_email@gmail.net"},
            }
        ],
        "items": items,
    }
    status = {"status": "active.tendering"}

    # general
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token), {"data": general})
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
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token), {"data": descriptions})
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
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token), {"data": titles})
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
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token), {"data": criterias})
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
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token), {"data": lists})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]

    self.assertEqual(tender["funders"], lists["funders"])
    buyer_id = tender["buyers"][0]["id"]
    lists["buyers"][0]["id"] = buyer_id

    self.assertEqual(tender["buyers"], lists["buyers"])

    self.assertEqual(tender["items"][0]["description"], lists["items"][0]["description"])
    self.add_sign_doc(tender["id"], token)

    # status
    response = self.app.patch_json("/tenders/{}?acc_token={}".format(tender["id"], token), {"data": status}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{'description': [{'relatedBuyer': ['This field is required.']}], 'location': 'body', 'name': 'items'}],
    )
    items = deepcopy(tender["items"])
    items[0]["relatedBuyer"] = buyer_id

    test_criteria = deepcopy(test_tender_pq_criteria)
    set_tender_criteria(test_criteria, tender.get("lots", []), items)

    patch_data = {
        "items": items,
        "criteria": test_criteria,
    }
    patch_data.update(status)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": patch_data},
    )
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
        {
            "data": {
                "tenderID": "Some id",
                "procurementMethodType": "belowThreshold",
                "procurementMethod": "selective",
                "submissionMethod": "written",
                "mode": "test",
            }
        },
        status=422,
    )
    self.assertCountEqual(
        response.json["errors"],
        [
            {"location": "body", "name": "mode", "description": "Rogue field"},
            {"location": "body", "name": "tenderID", "description": "Rogue field"},
            {"location": "body", "name": "procurementMethodType", "description": "Rogue field"},
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": {
                "submissionMethod": "written",
            }
        },
        status=422,
    )

    # owner
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": {
                "owner": "Test owner",
                "transfer_token": "17bc682ec79245bca7d9cdbabbfce8f8",
                "owner_token": "17bc682ec79245bca7d9cdbabbfce8f7",
            }
        },
        status=422,
    )
    self.assertCountEqual(
        response.json["errors"],
        [
            {"location": "body", "name": "owner_token", "description": "Rogue field"},
            {"location": "body", "name": "transfer_token", "description": "Rogue field"},
            {"location": "body", "name": "owner", "description": "Rogue field"},
        ],
    )

    # time
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": {
                "date": (get_now() + timedelta(days=1)).isoformat(),
                "dateModified": (get_now() + timedelta(days=1)).isoformat(),
            }
        },
        status=422,
    )
    self.assertCountEqual(
        response.json["errors"],
        [
            {"location": "body", "name": "date", "description": "Rogue field"},
            {"location": "body", "name": "dateModified", "description": "Rogue field"},
        ],
    )

    # lists
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": {
                "revisions": [{"author": "Some author"}],
                "plans": [{"id": uuid4().hex}],
                "cancellations": [{"reason": "Some reason", "reasonType": "noDemand"}],
            }
        },
        status=422,
    )
    self.assertCountEqual(
        response.json["errors"],
        [
            {"location": "body", "name": "plans", "description": "Rogue field"},
            {"location": "body", "name": "revisions", "description": "Rogue field"},
            {"location": "body", "name": "cancellations", "description": "Rogue field"},
        ],
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
    response = self.app.post_json("/tenders", {"data": tender_data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json,
        {"status": "error", "errors": [{"location": "body", "name": "guarantee", "description": "Rogue field"}]},
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
        self.assertEqual(response.json['data']['procuringEntity']['kind'], kind)


def tender_fields(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender = response.json["data"]
    tender_fields = {
        "id",
        "dateModified",
        "dateCreated",
        "tenderID",
        "date",
        "status",
        "awardCriteria",
        "owner",
    }

    self.assertEqual(
        set(tender) - set(self.initial_data),
        tender_fields,
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

    pq_entity = deepcopy(tender["procuringEntity"])
    pq_entity["kind"] = "defense"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"procuringEntity": pq_entity}}
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
        status=422,
    )
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "dateModified", "description": "Rogue field"}]
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
        {"data": {"items": [data["items"][0], data["items"][0]]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    item0 = response.json["data"]["items"][0]
    item1 = response.json["data"]["items"][1]
    self.assertNotEqual(item0.pop("id"), item1.pop("id"))
    self.assertEqual(item0, item1)

    # check patching profile in items
    item0["profile"] = "10000-000-10"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"items": [item0]}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]["items"]), 1)

    # check patching agreement in draft status
    agreement_2 = deepcopy(test_agreement_pq_data)
    agreement_2["id"] = agreement_2_id = uuid4().hex
    self.mongodb.agreements.save(agreement_2, insert=True)
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token), {"data": {"agreement": {"id": agreement_2_id}}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["agreement"]["id"], agreement_2_id)

    data = deepcopy(item0)
    data["classification"] = {
        "scheme": "ДК021",
        "id": "55523100-3",
        "description": "Послуги з харчування у школах",
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], owner_token),
        {"data": {"items": [data]}},
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
        response.json["errors"][0], {"location": "body", "name": "guarantee", "description": "Rogue field"}
    )


def required_field_deletion(self):
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {
            "data": {
                "tenderPeriod": {
                    "startDate": None,
                    "endDate": tender["tenderPeriod"]["endDate"],
                }
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
                "description": {"startDate": ["This field is required."]},
                "location": "body",
                "name": "tenderPeriod",
            }
        ],
    )


def patch_tender_status(self):
    cur_status = "active.tendering"
    patch_status = "cancelled"
    self.create_tender()
    self.set_status(cur_status)
    data = {
        "data": {
            "status": patch_status,
        }
    }
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(self.tender_id, self.tender_token), data, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
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


def invalid_tender_conditions(self):
    # create tender
    response = self.app.post_json("/tenders", {"data": self.initial_data, "config": self.initial_config})
    tender_id = self.tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]
    # switch to active.tendering
    self.set_status("active.tendering")
    # cancellation
    cancellation = deepcopy(test_tender_pq_cancellation)
    cancellation.update(
        {
            "reason": "invalid conditions",
            "reasonType": "noDemand",
        }
    )
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
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

    response = self.app.get(f"/tenders/{tender_id}")
    tender = response.json["data"]

    rrs = set_bid_responses(tender["criteria"])

    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    resp = self.app.post_json(
        "/tenders/{}/bids".format(tender_id),
        {
            "data": {
                "tenderers": [test_tender_pq_organization],
                "value": {"amount": 500},
                "requirementResponses": rrs,
            }
        },
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
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True}},
    )
    self.assertNotEqual(response.json["data"]["date"], award_date)

    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]

    self.assertEqual(set(contract.keys()), {"id", "status", "awardID", "date", "value"})

    cancellation = deepcopy(test_tender_pq_cancellation)
    cancellation.update(
        {
            "reason": "invalid conditions",
            "reasonType": "noDemand",
        }
    )

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(tender_id, owner_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]
    response = self.app.post_json(
        "/tenders/{}/cancellations/{}/documents?acc_token={}".format(
            self.tender_id, cancellation_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
    )

    response = self.app.patch_json(
        "/tenders/{}/cancellations/{}?acc_token={}".format(tender_id, cancellation_id, owner_token),
        {"data": {"status": "active"}},
    )

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract_id))
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.get("/contracts/{}".format(contract_id))
    self.assertEqual(response.json["data"]["status"], "cancelled")


def one_invalid_bid_tender(self):
    tender_id = self.tender_id
    owner_token = self.tender_token

    response = self.app.get(f"/tenders/{tender_id}")
    tender = response.json["data"]

    rrs = set_bid_responses(tender["criteria"])

    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid, token = self.create_bid(
        self.tender_id,
        {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": rrs,
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
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
    )
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "unsuccessful")


def first_bid_tender(self):
    tender_id = self.tender_id
    owner_token = self.tender_token

    response = self.app.get(f"/tenders/{tender_id}")
    tender = response.json["data"]

    rrs = set_bid_responses(tender["criteria"])

    # create bid
    bid, bid_token1 = self.create_bid(
        self.tender_id,
        {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 450},
            "requirementResponses": rrs,
        },
    )
    bid_1 = bid["id"]

    # create second bid
    bid, bid_token2 = self.create_bid(
        self.tender_id,
        {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 300},
            "requirementResponses": rrs,
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
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "unsuccessful", "qualified": False}},
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
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True}},
    )
    # get contract id
    response = self.app.get("/tenders/{}".format(tender_id))
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]

    activate_econtract(self, contract_id, owner_token, bid_token1)
    # check status
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}".format(tender_id))
    self.assertEqual(response.json["data"]["status"], "complete")


def lost_contract_for_active_award(self):
    tender_id = self.tender_id
    owner_token = self.tender_token

    response = self.app.get(f"/tenders/{tender_id}")
    tender = response.json["data"]

    rrs = set_bid_responses(tender["criteria"])

    # create bid
    self.app.authorization = ("Basic", ("broker", ""))
    bid, bid_token = self.create_bid(
        self.tender_id,
        {
            "tenderers": [test_tender_pq_organization],
            "value": {"amount": 500},
            "requirementResponses": rrs,
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
        "/tenders/{}/awards/{}?acc_token={}".format(tender_id, award_id, owner_token),
        {"data": {"status": "active", "qualified": True}},
    )
    # lost contract
    tender = self.mongodb.tenders.get(tender_id)
    self.mongodb.contracts.delete(tender["contracts"][0]["id"])
    del tender["contracts"]
    self.mongodb.tenders.save(tender)

    # create lost contract
    response = self.check_chronograph()
    self.assertEqual(response.json["data"]["status"], "active.awarded")
    self.assertIn("contracts", response.json["data"])
    self.assertNotIn("next_check", response.json["data"])
    contract = response.json["data"]["contracts"][-1]
    contract_id = contract["id"]
    activate_econtract(self, contract_id, owner_token, bid_token)

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
    self.add_sign_doc(tender_id, tender_token)

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

    test_criteria = deepcopy(test_tender_pq_criteria)
    set_tender_criteria(test_criteria, tender.get("lots", []), items)

    response = self.app.patch_json(
        patch_request_path,
        {
            "data": {
                "status": self.primary_tender_status,
                "criteria": test_criteria,
            }
        },
    )
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


def draft_activation_validations(self):
    self.add_sign_doc(self.tender_id, self.tender_token)

    # tender item has not active profile
    profile = deepcopy(test_tender_pq_short_profile)
    profile["status"] = "hidden"

    response_200 = Mock()
    response_200.status_code = 200
    response_200.json = Mock(return_value={"data": profile})

    with patch("openprocurement.api.utils.requests.get", Mock(return_value=response_200)):
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"status": "active.tendering"}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(
            response.json["errors"][0]["description"], f"Profiles {profile['id']}: hidden not in ('active',)"
        )

    # agreement in profile not equals agreement in tender
    profile["status"] = "active"
    profile["agreementID"] = uuid4().hex

    with patch_market(profile, test_tender_pq_category):
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"status": "active.tendering"}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.json["errors"][0]["description"], "Tender agreement doesn't match profile agreement")

    # agreementType mismatch
    agreement = deepcopy(test_agreement_pq_data)
    agreement["agreementType"] = "internationalFinancialInstitutions"
    self.mongodb.agreements.save(agreement)
    with patch_market(test_tender_pq_short_profile, test_tender_pq_category):
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"status": "active.tendering"}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.json["errors"][0]["description"], "Agreement type mismatch.")

    # not active agreement
    agreement["agreementType"] = "electronicCatalogue"
    agreement["status"] = "pending"
    self.mongodb.agreements.save(agreement)
    with patch_market(test_tender_pq_short_profile, test_tender_pq_category):
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"status": "active.tendering"}},
            status=422,
        )
        self.assertEqual(response.status, "422 Unprocessable Entity")
        self.assertEqual(response.json["errors"][0]["description"], "Agreement status is not active")


def switch_draft_to_tendering_success(self):
    tender_prev = self.app.get(f"/tenders/{self.tender_id}?acc_token={self.tender_token}").json["data"]

    self.add_sign_doc(self.tender_id, self.tender_token)

    profile = deepcopy(test_tender_pq_short_profile)
    category = deepcopy(test_tender_pq_category)

    response_200_profile = Mock()
    response_200_profile.status_code = 200
    response_200_profile.json = Mock(return_value={"data": profile})

    response_200_category = Mock()
    response_200_category.status_code = 200
    response_200_category.json = Mock(return_value={"data": category})

    expected_profile_url = f"/api/profiles/{profile['id']}"
    expected_category_url = f"/api/categories/{category['id']}"

    def mock_get_side_effect(url, *args, **kwargs):
        if expected_profile_url in url:
            return response_200_profile
        elif expected_category_url in url:
            return response_200_category
        raise ValueError(f"Unexpected URL: {url}")

    mock_get = Mock(side_effect=mock_get_side_effect)

    with patch("openprocurement.api.utils.requests.get", mock_get):
        response = self.app.patch_json(
            f"/tenders/{self.tender_id}?acc_token={self.tender_token}",
            {"data": {"status": "active.tendering"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "active.tendering")
        self.assertNotEqual(response.json["data"]["date"], tender_prev["date"])
        self.assertNotEqual(response.json["data"]["dateModified"], tender_prev["dateModified"])
        self.assertNotEqual(
            response.json["data"]["tenderPeriod"]["startDate"],
            tender_prev["tenderPeriod"]["startDate"],
        )
        self.assertIn("contractTemplateName", response.json["data"])

        # check there are no extra market calls
        self.assertEqual(mock_get.call_count, 2)
        self.assertIn(expected_profile_url, mock_get.call_args_list[0][0][0])
        self.assertIn(expected_category_url, mock_get.call_args_list[1][0][0])


def tender_delivery_milestones(self):
    data = deepcopy(self.initial_data)
    data["milestones"] = [
        {
            "id": "c" * 32,
            "title": "signingTheContract",
            "type": "delivery",
            "duration": {"days": 1500, "type": "calendar"},
            "sequenceNumber": 1,
            "code": "postpayment",
            "percentage": 10,
        }
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
    data["milestones"][-1]["relatedLot"] = uuid4().hex
    response = self.app.post_json("/tenders", {"data": data, "config": self.initial_config}, status=422)
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": ["relatedLot should be one of the lots."],
            }
        ],
    )
    del data["milestones"][-1]["relatedLot"]
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
                "description": "Sum of the delivery milestone percentages 10.0 is not equal 100.",
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


def tender_finance_milestones(self):
    data = deepcopy(self.initial_data)

    # test creation
    data["milestones"] = test_tender_pq_milestones
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

    patch_milestones = deepcopy(tender["milestones"])
    patch_milestones[0]["title"] = "submissionDateOfApplications"
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"milestones": patch_milestones}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["milestones"][0]["title"], "submissionDateOfApplications")

    patch_milestones[0]["percentage"] = 70
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"milestones": patch_milestones}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "milestones",
                "description": "Sum of the financing milestone percentages 124.45 is not equal 100.",
            }
        ],
    )

    patch_milestones[0]["percentage"] = 45.55
    patch_milestones[0]["sequenceNumber"] = 3
    response = self.app.patch_json(
        "/tenders/{}?acc_token={}".format(tender["id"], token),
        {"data": {"milestones": patch_milestones}},
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
                        "sequenceNumber": "Field should contain incrementing sequence numbers starting from 1 for tender/lot separately"
                    }
                ],
            }
        ],
    )


def create_tender_pq_from_dps_invalid_agreement(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"

    config = deepcopy(self.initial_config)
    config.update({"hasPreSelectionAgreement": True})

    response = self.app.post_json(
        "/tenders",
        {
            "data": data,
            "config": config,
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    self.tender_id = tender_id
    add_criteria(self, criteria=test_tender_pq_criteria)
    self.add_sign_doc(tender_id, owner_token)

    # Invalid agreement type
    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement["agreementType"] = "invalid"
    self.mongodb.agreements.save(agreement)

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={owner_token}",
        {"data": {"status": "active.tendering"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "agreement", "description": "Agreement type mismatch."}],
    )

    # DPS agreement with hasItems set to True is forbidden
    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement.pop("items")
    agreement["agreementType"] = DPS_TYPE
    agreement["hasItems"] = False
    self.mongodb.agreements.save(agreement)

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={owner_token}",
        {"data": {"status": "active.tendering"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "agreement", "description": "Agreement without items is not allowed."}],
    )


def create_tender_pq_from_dps_invalid_items(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"

    config = deepcopy(self.initial_config)
    config.update({"hasPreSelectionAgreement": True})

    response = self.app.post_json(
        "/tenders",
        {
            "data": self.initial_data,
            "config": config,
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    tender_id = response.json["data"]["id"]
    owner_token = response.json["access"]["token"]

    self.tender_id = tender_id

    # description mismatch

    items = deepcopy(self.initial_data["items"])
    items[0]["description"] = "different from agreement item description"

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={owner_token}",
        {"data": {"items": items}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "items",
                "description": "Item description 'different from agreement item description' not found in agreement items",
            }
        ],
    )

    # classification.id mismatch

    items = deepcopy(self.initial_data["items"])
    items[0]["classification"]["id"] = "33611000-6"

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={owner_token}",
        {
            "data": {
                "items": items,
                "contractTemplateName": get_contract_template_name({"items": items}),
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "items",
                "description": "Item classification.id '33611000-6' not found in agreement items",
            }
        ],
    )

    # unit.code mismatch

    items = deepcopy(self.initial_data["items"])
    items[0]["unit"]["code"] = "GM"

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={owner_token}",
        {"data": {"items": items}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "items",
                "description": "Item unit.code 'GM' not found in agreement items",
            }
        ],
    )

    # Combination mismatch
    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement_item = deepcopy(agreement["items"][0])
    agreement_item["description"] = "лікарські засоби"
    agreement_item["classification"]["id"] = "33611000-6"
    agreement["items"].append(agreement_item)
    self.mongodb.agreements.save(agreement)

    items = deepcopy(self.initial_data["items"])
    items[0]["classification"]["id"] = "33611000-6"

    response = self.app.patch_json(
        f"/tenders/{tender_id}?acc_token={owner_token}",
        {
            "data": {
                "items": items,
                "contractTemplateName": get_contract_template_name({"items": items}),
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "items",
                "description": "Item not found in agreement items: ('Комп’ютерне обладнання', 'ДК021', '33611000-6', 'KGM')",
            }
        ],
    )


def validate_restricted_from_agreement(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"

    config = deepcopy(self.initial_config)
    config.update({"hasPreSelectionAgreement": True})

    # Non restricted agreement
    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement["config"] = {"restricted": False}
    self.mongodb.agreements.save(agreement)

    config = deepcopy(self.initial_config)
    config.update({"hasPreSelectionAgreement": True, "restricted": True})

    self.app.authorization = ("Basic", ("brokerr", ""))
    response = self.app.post_json(
        "/tenders",
        {
            "data": self.initial_data,
            "config": config,
        },
        status=422,
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "config.restricted", "description": "Value must be False."}],
    )

    # Restricted agreement
    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement["config"] = {"restricted": True}
    self.mongodb.agreements.save(agreement)

    config["restricted"] = False

    response = self.app.post_json(
        "/tenders",
        {
            "data": self.initial_data,
            "config": config,
        },
        status=422,
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "config.restricted", "description": "Value must be True."}],
    )

    # restricted PQ from broker
    config["restricted"] = True
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.post_json(
        "/tenders",
        {
            "data": self.initial_data,
            "config": config,
        },
        status=403,
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "url",
                "name": "accreditation",
                "description": "Broker Accreditation level does not permit tender restricted data access",
            }
        ],
    )

    # restricted PQ from brokerr
    self.app.authorization = ("Basic", ("brokerr", ""))
    response = self.app.post_json(
        "/tenders",
        {
            "data": self.initial_data,
            "config": config,
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    tender_id = response.json["data"]["id"]

    # check masked items
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get(f"/tenders/{tender_id}")
    self.assertEqual(response.json["data"]["items"][0]["deliveryAddress"]["streetAddress"], "Приховано")


def validate_procuring_entity_match(self):
    data = deepcopy(self.initial_data)
    data["status"] = "draft"

    config = deepcopy(self.initial_config)
    config.update({"hasPreSelectionAgreement": True})

    # Successful tender creation for equal procuring entities
    response = self.app.post_json(
        "/tenders",
        {
            "data": data,
            "config": config,
        },
    )
    self.assertEqual(response.status, "201 Created")

    # Failed tender creation for different procuring entities (both are not defense)
    data["procuringEntity"]["identifier"]["id"] = "1234567890"
    response = self.app.post_json(
        "/tenders",
        {
            "data": data,
            "config": config,
        },
        status=422,
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "agreement",
                "description": "tender.procuringEntity.identifier (scheme or id), doesnt match tender.agreements[0].procuringEntity.identifier (scheme of id)",
            }
        ],
    )

    # Failed tender creation for different procuring entities (tender one is defense)
    data["procuringEntity"]["identifier"]["id"] = "1234567890"
    data["procuringEntity"]["kind"] = "defense"
    response = self.app.post_json(
        "/tenders",
        {
            "data": data,
            "config": config,
        },
        status=422,
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "agreement",
                "description": "tender.procuringEntity.identifier (scheme or id), doesnt match tender.agreements[0].procuringEntity.identifier (scheme of id)",
            }
        ],
    )

    # Failed tender creation for different procuring entities (agreement one is defense)
    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement["procuringEntity"]["kind"] = "other"
    self.mongodb.agreements.save(agreement)
    data["procuringEntity"]["identifier"]["id"] = "1234567890"
    data["procuringEntity"]["kind"] = "defense"
    response = self.app.post_json(
        "/tenders",
        {
            "data": data,
            "config": config,
        },
        status=422,
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "agreement",
                "description": "tender.procuringEntity.identifier (scheme or id), doesnt match tender.agreements[0].procuringEntity.identifier (scheme of id)",
            }
        ],
    )

    # Failed tender creation for different procuring entities (both are defense)
    agreement = self.mongodb.agreements.get(self.agreement_id)
    agreement["procuringEntity"]["kind"] = "defense"
    self.mongodb.agreements.save(agreement)
    data["procuringEntity"]["identifier"]["id"] = "1234567890"
    data["procuringEntity"]["kind"] = "defense"
    response = self.app.post_json(
        "/tenders",
        {
            "data": data,
            "config": config,
        },
    )
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.status, "201 Created")
