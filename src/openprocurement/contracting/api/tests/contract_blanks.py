# -*- coding: utf-8 -*-
import mock
from uuid import uuid4
from copy import deepcopy
from datetime import timedelta
from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.contracting.api.models import Contract
from openprocurement.api.utils import get_now
from openprocurement.contracting.api.tests.data import documents
from openprocurement.tender.core.tests.base import change_auth


def simple_add_contract(self):
    u = Contract(self.initial_data)
    u.contractID = "UA-C"

    assert u.id == self.initial_data["id"]
    assert u.doc_id == self.initial_data["id"]
    assert u.rev is None

    u.store(self.db)

    assert u.id == self.initial_data["id"]
    assert u.rev is not None

    fromdb = self.db.get(u.id)

    assert u.contractID == fromdb["contractID"]
    assert u.doc_type == "Contract"

    u.delete_instance(self.db)


def empty_listing(self):
    response = self.app.get("/contracts")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertNotIn('{\n    "', response.body)
    self.assertNotIn("callback({", response.body)
    self.assertEqual(response.json["next_page"]["offset"], "")
    self.assertNotIn("prev_page", response.json)

    response = self.app.get("/contracts?opt_jsonp=callback")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertNotIn('{\n    "', response.body)
    self.assertIn("callback({", response.body)

    response = self.app.get("/contracts?opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body)
    self.assertNotIn("callback({", response.body)

    response = self.app.get("/contracts?opt_jsonp=callback&opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('{\n    "', response.body)
    self.assertIn("callback({", response.body)

    response = self.app.get("/contracts?offset=2015-01-01T00:00:00+02:00&descending=1&limit=10")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertIn("descending=1", response.json["next_page"]["uri"])
    self.assertIn("limit=10", response.json["next_page"]["uri"])
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertIn("limit=10", response.json["prev_page"]["uri"])

    response = self.app.get("/contracts?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertEqual(response.json["next_page"]["offset"], "")
    self.assertNotIn("prev_page", response.json)

    response = self.app.get("/contracts?feed=changes&offset=0", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": u"Offset expired/invalid", u"location": u"params", u"name": u"offset"}],
    )

    response = self.app.get("/contracts?feed=changes&descending=1&limit=10")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertIn("descending=1", response.json["next_page"]["uri"])
    self.assertIn("limit=10", response.json["next_page"]["uri"])
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertIn("limit=10", response.json["prev_page"]["uri"])


def listing(self):
    response = self.app.get("/contracts")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    contracts = []

    for i in range(3):
        data = deepcopy(self.initial_data)
        data["id"] = uuid4().hex
        offset = get_now().isoformat()
        with change_auth(self.app, ("Basic", ("contracting", ""))) as app:
            response = self.app.post_json("/contracts", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        contracts.append(response.json["data"])

    ids = ",".join([i["id"] for i in contracts])

    while True:
        response = self.app.get("/contracts")
        self.assertEqual(response.status, "200 OK")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in contracts]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in contracts])
    )
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in contracts]))

    response = self.app.get("/contracts?offset={}".format(offset))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/contracts?limit=2")
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

    response = self.app.get("/contracts", params=[("opt_fields", "contractID")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"contractID"]))
    self.assertIn("opt_fields=contractID", response.json["next_page"]["uri"])

    response = self.app.get("/contracts?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in contracts]))
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in contracts], reverse=True)
    )

    response = self.app.get("/contracts?descending=1&limit=2")
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

    test_contract_data2 = deepcopy(self.initial_data)
    test_contract_data2["mode"] = "test"
    with change_auth(self.app, ("Basic", ("contracting", ""))) as app:
        response = self.app.post_json("/contracts", {"data": test_contract_data2})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    while True:
        response = self.app.get("/contracts?mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/contracts?mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)

    response = self.app.get("/contracts?mode=_all_&opt_fields=status")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def listing_changes(self):
    response = self.app.get("/contracts?feed=changes")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    contracts = []

    for i in range(3):
        data = deepcopy(self.initial_data)
        data["status"] = "active"
        data["id"] = uuid4().hex
        with change_auth(self.app, ("Basic", ("contracting", ""))) as app:
            response = self.app.post_json("/contracts", {"data": data})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        contracts.append(response.json["data"])

    ids = ",".join([i["id"] for i in contracts])

    while True:
        response = self.app.get("/contracts?feed=changes")
        self.assertEqual(response.status, "200 OK")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in contracts]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in contracts])
    )
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in contracts]))

    response = self.app.get("/contracts?feed=changes&limit=2")
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

    response = self.app.get("/contracts?feed=changes", params=[("opt_fields", "contractID")])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified", u"contractID"]))
    self.assertIn("opt_fields=contractID", response.json["next_page"]["uri"])

    response = self.app.get("/contracts?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set([u"id", u"dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in contracts]))
    self.assertEqual(
        [i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in contracts], reverse=True)
    )

    response = self.app.get("/contracts?feed=changes&descending=1&limit=2")
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

    test_contract_data2 = self.initial_data.copy()
    test_contract_data2["mode"] = "test"
    test_contract_data2["status"] = "active"
    with change_auth(self.app, ("Basic", ("contracting", ""))) as app:
        response = self.app.post_json("/contracts", {"data": test_contract_data2})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    while True:
        response = self.app.get("/contracts?feed=changes&mode=test")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    response = self.app.get("/contracts?feed=changes&mode=_all_")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 4)


def get_contract(self):
    response = self.app.get("/contracts")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/contracts", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    contract = response.json["data"]
    self.assertEqual(contract["id"], self.initial_data["id"])

    response = self.app.get("/contracts/{}".format(contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], contract)

    response = self.app.get("/contracts/{}?opt_jsonp=callback".format(contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"data": {"', response.body)

    response = self.app.get("/contracts/{}?opt_pretty=1".format(contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "data": {\n        "', response.body)


def not_found(self):
    response = self.app.get("/contracts")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/contracts", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    contract = response.json["data"]
    self.assertEqual(contract["id"], self.initial_data["id"])

    while True:
        response = self.app.get("/contracts")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    tender_id = self.initial_data["tender_id"]
    response = self.app.get("/contracts/{}".format(tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")

    from openprocurement.tender.belowthreshold.tests.base import test_tender_data

    with change_auth(self.app, ("Basic", ("broker1", ""))):
        response = self.app.post_json("/tenders", {"data": test_tender_data})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]

    response = self.app.get("/contracts/{}".format(tender["id"]), status=404)
    self.assertEqual(response.status, "404 Not Found")

    data = deepcopy(self.initial_data)
    data["id"] = uuid4().hex
    data["tender_id"] = tender["id"]
    response = self.app.post_json("/contracts", {"data": data})
    self.assertEqual(response.status, "201 Created")

    response = self.app.get("/contracts/{}".format(tender["id"]), status=404)
    self.assertEqual(response.status, "404 Not Found")

    response = self.app.get("/contracts/{}".format(data["id"]))
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/contracts/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )

    response = self.app.patch_json("/contracts/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )


def create_contract_invalid(self):
    request_path = "/contracts"
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


def create_contract_generated(self):
    data = self.initial_data.copy()
    data.update({"id": uuid4().hex, "doc_id": uuid4().hex, "contractID": uuid4().hex})
    response = self.app.post_json("/contracts", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]
    self.assertEqual(
        set(contract),
        set(
            [
                u"id",
                u"dateModified",
                u"contractID",
                u"status",
                u"suppliers",
                u"contractNumber",
                u"period",
                u"dateSigned",
                u"value",
                u"awardID",
                u"items",
                u"owner",
                u"tender_id",
                u"procuringEntity",
            ]
        ),
    )
    self.assertEqual(data["id"], contract["id"])
    self.assertNotEqual(data["doc_id"], contract["id"])
    self.assertEqual(data["contractID"], contract["contractID"])


def create_contract(self):
    response = self.app.get("/contracts")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    response = self.app.post_json("/contracts", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]
    self.assertEqual(contract["status"], "active")

    response = self.app.get("/contracts/{}".format(contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(set(response.json["data"]), set(contract))
    self.assertEqual(response.json["data"], contract)

    # test eu contract create
    data = deepcopy(self.initial_data)
    data["id"] = uuid4().hex
    additionalContactPoint = {"name": u"Державне управління справами2", "telephone": u"0440000001"}
    data["procuringEntity"]["additionalContactPoints"] = [additionalContactPoint]
    data["procuringEntity"]["contactPoint"]["availableLanguage"] = "en"
    response = self.app.post_json("/contracts", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]
    self.assertEqual(contract["status"], "active")
    self.assertEqual(contract["procuringEntity"]["contactPoint"]["availableLanguage"], "en")
    self.assertEqual(contract["procuringEntity"]["additionalContactPoints"], [additionalContactPoint])

    data = deepcopy(self.initial_data)
    data["id"] = uuid4().hex
    response = self.app.post_json("/contracts?opt_jsonp=callback", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"', response.body)

    data["id"] = uuid4().hex
    response = self.app.post_json("/contracts?opt_pretty=1", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body)

    data["id"] = uuid4().hex
    response = self.app.post_json("/contracts", {"data": data, "options": {"pretty": True}})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body)

    # broker has no permissions to create contract
    with change_auth(self.app, ("Basic", ("broker", ""))):
        response = self.app.post_json("/contracts", {"data": self.initial_data}, status=403)
        self.assertEqual(response.status, "403 Forbidden")


def put_transaction_to_contract(self):

    response = self.app.get("/contracts/{}".format(self.contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    tender_token = self.initial_data["tender_token"]
    credentials_url = "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token)
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.put_json(
        "/contracts/{}/transactions/{}?acc_token={}".format(self.contract["id"], 12345, 'fake_token'),
        {"data": ""}, status=403
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}]
    )

    response = self.app.put_json(
        "/contracts/{}/transactions/{}?acc_token={}".format(self.contract["id"], 12345, token),
        {
            "data": {
                "date": "2020-05-20T18:47:47.136678+02:00",
                "value": {
                    "amount": 500,
                    "currency": "UAH"
                },
                "payer": {
                    "bankAccount": {
                        "id": 789,
                        "scheme": "IBAN",
                    },
                    "name": "payer1"
                },
                "payee": {
                    "bankAccount": {
                        "id": 888,
                        "scheme": "IBAN",
                    },
                    "name": "payee1"
                },
                "status": 0
            }
        }
    )

    self.assertEqual(
        response.json['data']['implementation']['transactions'],
        [
            {
                'status': 'successful',
                'payer': {
                    "bankAccount": {
                        "id": "789",
                        "scheme": "IBAN",
                    },
                    "name": "payer1"
                },
                'value': {
                    'currency': 'UAH', 
                    'amount': 500.0
                },
                'payee': {
                    "bankAccount": {
                        "id": "888",
                        "scheme": "IBAN",
                    },
                    "name": "payee1"
                },
                'date': '2020-05-20T18:47:47.136678+02:00',
                'id': '12345'
            }
        ]
    )

    response = self.app.put_json(
        "/contracts/{}/transactions/{}?acc_token={}".format(self.contract["id"], 12345, token),
        {"data": {
            "date": "2020-05-20T18:47:47.136678+02:00",
            "value": {
                "amount": 500,
                "currency": "UAH"
            },
            "payer": {
                "bankAccount": {
                        "id": 800000000,
                        "scheme": "IBAN",
                    },
                "name": "payer_should_not_applied1"
            },
            "payee": {
                "bankAccount": {
                        "id": 90000000,
                        "scheme": "IBAN",
                    },
                "name": "payee_should_not_applied1"
            },
            "status": "new_status_123"
        }
        }
    )
    self.assertEqual(response.status, "200 OK")

    self.assertEqual(
        response.json['data']['implementation']['transactions'],
        [
            {
                'status': 'new_status_123',
                'payer': {
                    "bankAccount": {
                        "id": "789",
                        "scheme": "IBAN",
                    },
                    "name": "payer1"
                },
                'value': {
                    'currency': 'UAH', 'amount': 500.0
                },
                'payee': {
                    "bankAccount": {
                        "id": "888",
                        "scheme": "IBAN",
                    },
                    "name": "payee1"
                },
                'date': '2020-05-20T18:47:47.136678+02:00',
                'id': '12345'
            }
        ]
    )

    response = self.app.put_json(
        "/contracts/{}/transactions/{}?acc_token={}".format(self.contract["id"], 90800777, token),
        {"data": {
            "date": "2020-06-10T10:47:47.136678+02:00",
            "value": {
                "amount": 14500.5,
                "currency": "UAH"
            },
            "payer": {
                "bankAccount": {
                    "id": 78999,
                    "scheme": "IBAN",
                },
                "name": "payer2"
            },
            "payee": {
                "bankAccount": {
                    "id": 199000,
                    "scheme": "IBAN",
                },
                "name": "payee2"
            },
            "status": -1
        }
        }
    )
    self.assertEqual(response.status, "200 OK")
    
    self.assertEqual(
        response.json['data']['implementation']['transactions'],
        [
            {
                'status': 'new_status_123',
                'payer': {
                    "bankAccount": {
                        "id": "789",
                        "scheme": "IBAN",
                    },
                    "name": "payer1"
                },
                'value': {
                    'currency': 'UAH', 'amount': 500.0
                },
                'payee': {
                    "bankAccount": {
                        "id": "888",
                        "scheme": "IBAN",
                    },
                    "name": "payee1"
                },
                'date': '2020-05-20T18:47:47.136678+02:00',
                'id': '12345'
            },
            {
                'status': 'canceled',
                'payer': {
                    "bankAccount": {
                        "id": "78999",
                        "scheme": "IBAN",
                    },
                    "name": "payer2"
                },
                'value': {
                    'currency': 'UAH', 'amount': 14500.5
                },
                'payee': {
                    "bankAccount": {
                        "id": "199000",
                        "scheme": "IBAN",
                    },
                    'name': 'payee2'
                },
                'date': '2020-06-10T10:47:47.136678+02:00',
                'id': '90800777'
            }
        ]
    )

    response = self.app.put_json(
        "/contracts/{}/transactions/{}?acc_token={}".format(self.contract["id"], 111122, token),
        {
            "data": {
                "date": "2020-06-10T10:47:47.136678+02:00",
                "value": {
                    "amount": 18500.5,
                    "currency": "UAH",
                },
            }
        }, status=422
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u'description': [u'This field is required.'], u'location': u'body', u'name': u'status'
            },
            {
                u'description': [u'This field is required.'], u'location': u'body', u'name': u'payee'
            },
            {
                u'description': [u'This field is required.'], u'location': u'body', u'name': u'payer'
            }
        ]
    )

    response = self.app.put_json(
        "/contracts/{}/transactions/{}?acc_token={}".format(self.contract["id"], 3444444, token),
        {
            "data": {
                "date": "2020-06-10T10:47:47.136678+02:00",
                "value": {
                    "amount": 14500.5,
                    "currency": "UAH"
                },
                "payer": {
                    "bankAccount": {
                        "id": "789",
                        "scheme": "IBAN",
                    },
                    "name": "payer2"
                },
                "payee": "payee_invalid_structure",
                "status": "Accepted_status_123"
            }
        }, status=422
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u'description': [
                    u'Please use a mapping for this field or OrganizationReference instance instead of unicode.'
                ],
                u'location': u'body', u'name': u'payee'
            }
        ]
    )
    response = self.app.get("/contracts/{}".format(self.contract['id']))
    self.assertEqual(response.status, "200 OK")

    self.assertEqual(
        response.json['data']['implementation']['transactions'],
        [
            {
                'status': 'new_status_123',
                'payer': {
                    "bankAccount": {
                        "id": "789",
                        "scheme": "IBAN",
                    },
                    "name": "payer1"
                },
                'value': {
                    'currency': 'UAH', 'amount': 500.0
                },
                'payee': {
                    "bankAccount": {
                        "id": "888",
                        "scheme": "IBAN",
                    },
                    "name": "payee1"
                },
                'date': '2020-05-20T18:47:47.136678+02:00',
                'id': '12345'
            },
            {
                'status': 'canceled',
                'payer': {
                    "bankAccount": {
                        "id": "78999",
                        "scheme": "IBAN",
                    },
                    "name": "payer2"
                },
                'value': {
                    'currency': 'UAH', 'amount': 14500.5
                },
                'payee': {
                    "bankAccount": {
                        "id": "199000",
                        "scheme": "IBAN",
                    },
                    "name": "payee2"
                },
                'date': '2020-06-10T10:47:47.136678+02:00',
                'id': '90800777'
            }
        ]
    )
    response = self.app.get("/contracts/{}/transactions/{}".format(self.contract['id'], 2222222), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body", "name": "data",
                "description": "Transaction does not exist"
            }
        ]
    )

    response = self.app.put_json(
        "/contracts/{}/transactions/{}?acc_token={}".format(self.contract["id"], 5555, token),
        {
            "data": {
                "date": "2020-06-10T10:47:47.136678+02:00",
                "value": {
                    "amount": 14500.5,
                    "currency": "UAH"
                },
                "payer": {
                    "bankAccount": {
                        "id": "789",
                        "scheme": "INCORRECT_SCHEMA",
                    },
                    "name": "payer2"
                },
                "payee": {
                    "bankAccount": {
                        "id": "789"
                    },
                    "name": "payee2"
                },
                "status": 0
            }
        }, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': {
                    'bankAccount': {
                        'scheme': ["This field is required."]
                    }
                },
                'location': 'body',
                'name': 'payee'
            },
            {
                'description': {
                    'bankAccount': {
                        'scheme': ["Value must be one of ['IBAN']."]
                    }  
                },
                'location': 'body', 
                'name': 'payer'
            }
        ]
    )

    response = self.app.get("/contracts/{}/transactions/{}".format(self.contract['id'], 12345))
    self.assertEqual(
        response.json['data'],
        {
            'status': 'new_status_123',
            'payer': {
                "bankAccount": {
                    "id": "789",
                    "scheme": "IBAN",
                },
                'name': 'payer1'
            },
            'value': {
                'currency': 'UAH', 'amount': 500.0
            },
            'payee': {
                "bankAccount": {
                    "id": "888",
                    "scheme": "IBAN",
                },
                'name': 'payee1'
            },
            'date': '2020-05-20T18:47:47.136678+02:00',
            'id': '12345'
        }
    )


def create_contract_transfer_token(self):
    response = self.app.post_json("/contracts", {"data": self.initial_data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("transfer_token", response.json["data"])

    response = self.app.get("/contracts/{}".format(response.json["data"]["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertNotIn("transfer_token", response.json["data"])


def contract_status_change(self):
    tender_token = self.initial_data["tender_token"]

    response = self.app.get("/contracts/{}".format(self.contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token), {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"amountNet": self.contract["value"]["amount"] - 1}}},
    )
    # active > terminated allowed
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token), {"data": {"status": "terminated"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can't terminate contract while 'amountPaid' is not set",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {
            "data": {
                "status": "terminated",
                "amountPaid": {"amount": 100, "amountNet": 90, "valueAddedTaxIncluded": True, "currency": "UAH"},
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "terminated")

    # terminated > active not allowed
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token), {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")


def contract_items_change(self):
    tender_token = self.initial_data["tender_token"]

    response = self.app.patch_json(
        "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token), {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.get("/contracts/{}".format(self.contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    items = response.json["data"]["items"]

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"amountNet": self.contract["value"]["amount"] - 1}}},
    )

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"items": [{"quantity": 12, "description": "тапочки для тараканів"}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["quantity"], 12)
    self.assertEqual(response.json["data"]["items"][0]["description"], u"тапочки для тараканів")

    # add one more item
    item = deepcopy(items[0])
    item["quantity"] = 11
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token), {"data": {"items": [{}, item]}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "items", "description": ["Item id should be uniq for all items"]}],
    )

    # try to change classification
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"items": [{"classification": {"id": "19433000-0"}}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json, None)

    # add additional classification
    item_classific = deepcopy(self.initial_data["items"][0]["classification"])
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"items": [{"additionalClassifications": [{}, item_classific]}]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json, None)

    # update item fields
    startDate = get_now().isoformat()
    endDate = (get_now() + timedelta(days=90)).isoformat()
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {
            "data": {
                "items": [
                    {
                        "quantity": 0.005,
                        "deliveryAddress": {u"postalCode": u"79011", u"streetAddress": u"вул. Літаючого Хом’яка"},
                        "deliveryDate": {u"startDate": startDate, u"endDate": endDate},
                    }
                ]
            }
        },
    )
    self.assertEqual(response.json["data"]["items"][0]["quantity"], 0.005)
    self.assertEqual(response.json["data"]["items"][0]["deliveryAddress"]["postalCode"], u"79011")
    self.assertEqual(response.json["data"]["items"][0]["deliveryAddress"]["streetAddress"], u"вул. Літаючого Хом’яка")
    self.assertEqual(response.json["data"]["items"][0]["deliveryAddress"]["region"], u"м. Київ")
    self.assertEqual(response.json["data"]["items"][0]["deliveryAddress"]["locality"], u"м. Київ")
    self.assertEqual(response.json["data"]["items"][0]["deliveryAddress"]["countryName"], u"Україна")
    self.assertEqual(response.json["data"]["items"][0]["deliveryDate"]["startDate"], startDate)
    self.assertEqual(response.json["data"]["items"][0]["deliveryDate"]["endDate"], endDate)

    # try to remove all items
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token), {"data": {"items": []}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")


@mock.patch("openprocurement.contracting.api.validation.VAT_FROM", get_now() - timedelta(days=1))
def patch_tender_contract(self):
    response = self.app.patch_json(
        "/contracts/{}".format(self.contract["id"]), {"data": {"title": "New Title"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    tender_token = self.initial_data["tender_token"]
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], tender_token),
        {"data": {"title": "New Title"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    credentials_url = "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token)
    response = self.app.patch_json(credentials_url, {"data": ""})

    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"amountNet": self.contract["value"]["amount"] - 1}}},
    )

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token), {"data": {"title": "New Title"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "New Title")

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"amountPaid": {"amount": 100, "amountNet": 90}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["amountPaid"]["amount"], 100)
    self.assertEqual(response.json["data"]["amountPaid"]["amountNet"], 90)
    self.assertEqual(response.json["data"]["amountPaid"]["currency"], "UAH")
    self.assertEqual(response.json["data"]["amountPaid"]["valueAddedTaxIncluded"], True)

    custom_period_start_date = get_now().isoformat()
    custom_period_end_date = (get_now() + timedelta(days=3)).isoformat()
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"period": {"startDate": custom_period_start_date, "endDate": custom_period_end_date}}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"status": "terminated", "amountPaid": {"amount": 90, "amountNet": 80}, "terminationDetails": "sink"}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token), {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token), {"data": {"title": "fff"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json("/contracts/some_id", {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )

    response = self.app.get("/contracts/{}".format(self.contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "terminated")
    self.assertEqual(response.json["data"]["value"]["amount"], 238)
    self.assertEqual(response.json["data"]["period"]["startDate"], custom_period_start_date)
    self.assertEqual(response.json["data"]["period"]["endDate"], custom_period_end_date)
    self.assertEqual(response.json["data"]["amountPaid"]["amount"], 90)
    self.assertEqual(response.json["data"]["amountPaid"]["amountNet"], 80)
    self.assertEqual(response.json["data"]["terminationDetails"], "sink")


@mock.patch("openprocurement.contracting.api.validation.VAT_FROM", get_now() - timedelta(days=1))
def patch_tender_contract_readonly(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token)
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"currency": "USD"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"valueAddedTaxIncluded": False}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update valueAddedTaxIncluded for contract value")


@mock.patch("openprocurement.contracting.api.validation.VAT_FROM", get_now() + timedelta(days=1))
def patch_tender_contract_readonly_before_vat(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token)
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"currency": "USD"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"valueAddedTaxIncluded": False, "amount": 238, "amountNet": 238}}},
    )
    self.assertEqual(response.status, "200 OK")


@mock.patch("openprocurement.contracting.api.validation.VAT_FROM", get_now() - timedelta(days=1))
def patch_tender_contract_identical(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token)
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"amountPaid": {"amount": 100, "amountNet": 90, "valueAddedTaxIncluded": False}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "valueAddedTaxIncluded of amountPaid should be identical to valueAddedTaxIncluded of value of contract",
    )

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"amountPaid": {"amount": 100, "amountNet": 90, "currency": "USD"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "currency of amountPaid should be identical to currency of value of contract",
    )

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"amountPaid": {"amount": 100, "amountNet": 90}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("amountPaid", response.json["data"])

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token), {"data": {"amountPaid": None}}
    )
    self.assertEqual(response.status, "200 OK")

def patch_tender_without_value(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token)
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    contract_doc = self.db.get(self.contract["id"])
    del contract_doc['value']
    self.db.save(contract_doc)

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"amountPaid": {"amount": 100, "amountNet": 100, "valueAddedTaxIncluded": False}}},
    )


@mock.patch("openprocurement.contracting.api.validation.VAT_FROM", get_now() - timedelta(days=1))
def patch_tender_contract_amount(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token)
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"amount": 235}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be greater than amountNet and differ by no more than 20.0%",
    )

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"amount": 235, "amountNet": 100}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be greater than amountNet and differ by no more than 20.0%",
    )

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"amount": 235, "amountNet": 230}}},
    )
    self.assertEqual(response.status, "200 OK")

    self.assertEqual(response.json["data"]["value"]["amount"], 235)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 230)
    self.assertEqual(response.json["data"]["value"]["currency"], "UAH")
    self.assertEqual(response.json["data"]["value"]["valueAddedTaxIncluded"], True)

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {
            "data": {
                "status": "terminated",
                "amountPaid": {"amount": 100, "amountNet": 100},
                "terminationDetails": "sink",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be greater than amountNet and differ by no more than 20.0%",
    )


@mock.patch("openprocurement.contracting.api.validation.VAT_FROM", get_now() - timedelta(days=1))
def patch_tender_contract_amount_paid_zero(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token)
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"amountNet": self.contract["value"]["amount"] - 1}}},
    )

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"amountPaid": {"amount": 0, "amountNet": 0}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["amountPaid"]["amount"], 0)
    self.assertEqual(response.json["data"]["amountPaid"]["amountNet"], 0)
    self.assertEqual(response.json["data"]["amountPaid"]["valueAddedTaxIncluded"], True)


@mock.patch("openprocurement.contracting.api.validation.VAT_FROM", get_now() + timedelta(days=1))
def patch_tender_contract_before_vat(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token)
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"amountPaid": {"amount": 100, "amountNet": 90}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["valueAddedTaxIncluded"], True)
    self.assertEqual(response.json["data"]["amountPaid"]["valueAddedTaxIncluded"], True)

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"amountPaid": {"valueAddedTaxIncluded": False}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "valueAddedTaxIncluded of amountPaid should be identical to valueAddedTaxIncluded of value of contract",
    )

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"valueAddedTaxIncluded": False, "amount": 238, "amountNet": 238}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["valueAddedTaxIncluded"], False)
    self.assertEqual(response.json["data"]["amountPaid"]["valueAddedTaxIncluded"], False)

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"status": "terminated", "terminationDetails": "sink"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount and amountNet should be equal")

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {
            "data": {
                "amountPaid": {"amount": 238, "amountNet": 238},
                "status": "terminated",
                "terminationDetails": "sink",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")


@mock.patch("openprocurement.contracting.api.validation.VAT_FROM", get_now() + timedelta(days=1))
def patch_tender_contract_before_vat_single_request(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token)
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    self.assertEqual(response.json["data"]["value"]["valueAddedTaxIncluded"], True)

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {
            "data": {
                "value": {"valueAddedTaxIncluded": "False", "amount": 200, "amountNet": 200},
                "amountPaid": {"valueAddedTaxIncluded": "False", "amount": 100, "amountNet": 100},
                "status": "terminated",
                "terminationDetails": "sink",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["valueAddedTaxIncluded"], False)
    self.assertEqual(response.json["data"]["amountPaid"]["valueAddedTaxIncluded"], False)


def patch_tender_contract_wo_amount_net(self):
    tender_token = self.initial_data["tender_token"]

    response = self.app.patch_json(
        "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token), {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"amount": 235}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"amountNet": u"This field is required."}, u"location": u"body", u"name": u"value"}],
    )

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"amount": 235, "amountNet": 234}}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"amountPaid": {"amount": 235}, "status": "terminated", "terminationDetails": "sink"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{u"description": {u"amountNet": u"This field is required."}, u"location": u"body", u"name": u"amountPaid"}],
    )


def contract_administrator_change(self):
    response = self.app.patch_json(
        "/contracts/{}".format(self.contract["id"]),
        {
            "data": {
                "mode": u"test",
                "suppliers": [{"contactPoint": {"email": "fff@gmail.com"}, "address": {"postalCode": "79014"}}],
                "procuringEntity": {"identifier": {"id": "11111111"}, "contactPoint": {"telephone": "102"}},
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["mode"], u"test")
    self.assertEqual(response.json["data"]["procuringEntity"]["identifier"]["id"], "11111111")
    self.assertEqual(response.json["data"]["procuringEntity"]["contactPoint"]["telephone"], "102")
    self.assertEqual(response.json["data"]["suppliers"][0]["contactPoint"]["email"], "fff@gmail.com")
    self.assertEqual(
        response.json["data"]["suppliers"][0]["contactPoint"]["telephone"], "+380 (322) 91-69-30"
    )  # old field value left untouchable
    self.assertEqual(response.json["data"]["suppliers"][0]["address"]["postalCode"], "79014")
    self.assertEqual(
        response.json["data"]["suppliers"][0]["address"]["countryName"], u"Україна"
    )  # old field value left untouchable

    # administrator has permissions to update only: mode, procuringEntity, suppliers
    response = self.app.patch_json(
        "/contracts/{}".format(self.contract["id"]),
        {
            "data": {
                "value": {"amount": 100500},
                "id": "1234" * 8,
                "owner": "kapitoshka",
                "contractID": "UA-00-00-00",
                "dateSigned": get_now().isoformat(),
            }
        },
    )
    self.assertEqual(response.body, "null")

    response = self.app.get("/contracts/{}".format(self.contract["id"]))
    self.assertEqual(response.json["data"]["value"]["amount"], 238)
    self.assertEqual(response.json["data"]["id"], self.initial_data["id"])
    self.assertEqual(response.json["data"]["owner"], self.initial_data["owner"])
    self.assertEqual(response.json["data"]["contractID"], self.initial_data["contractID"])
    self.assertEqual(response.json["data"]["dateSigned"], self.initial_data["dateSigned"])


def get_credentials(self):
    response = self.app.get(
        "/contracts/{0}/credentials?acc_token={1}".format(self.contract_id, self.initial_data["tender_token"]),
        status=405,
    )
    self.assertEqual(response.status, "405 Method Not Allowed")


def generate_credentials(self):
    tender_token = self.initial_data["tender_token"]
    response = self.app.patch_json(
        "/contracts/{0}/credentials?acc_token={1}".format(self.contract_id, tender_token), {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["id"], self.initial_data["id"])
    self.assertNotIn("tender_token", response.json["data"])
    self.assertNotIn("owner_token", response.json["data"])
    self.assertEqual(response.json["data"]["owner"], "broker")
    self.assertEqual(len(response.json["access"]["token"]), 32)
    token1 = response.json["access"]["token"]

    # try second time generation
    response = self.app.patch_json(
        "/contracts/{0}/credentials?acc_token={1}".format(self.contract_id, tender_token), {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["id"], self.initial_data["id"])
    self.assertEqual(len(response.json["access"]["token"]), 32)
    token2 = response.json["access"]["token"]
    self.assertNotEqual(token1, token2)

    # first access token is non-workable
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract_id, token1), {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token2),
        {"data": {"value": {"amountNet": self.contract["value"]["amount"] - 1}}},
    )
    # terminated contract is also protected
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract_id, token2),
        {"data": {"status": "terminated", "amountPaid": {"amount": 100, "amountNet": 90}}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/contracts/{0}/credentials?acc_token={1}".format(self.contract_id, tender_token), {"data": ""}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can't generate credentials in current (terminated) contract status",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )


def create_contract_w_documents(self):
    data = deepcopy(self.initial_data)
    data["documents"] = documents
    response = self.app.post_json("/contracts", {"data": data})
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]
    self.assertEqual(contract["status"], "active")
    for index, doc in enumerate(documents):
        self.assertEqual(response.json["data"]["documents"][index]["id"], doc["id"])
        self.assertEqual(response.json["data"]["documents"][index]["datePublished"], doc["datePublished"])
        self.assertEqual(response.json["data"]["documents"][index]["dateModified"], doc["dateModified"])
        if 'author' in doc:
            self.assertEqual(response.json["data"]["documents"][index]["author"], doc["author"])

    self.assertIn("Signature=", response.json["data"]["documents"][-1]["url"])
    self.assertIn("KeyID=", response.json["data"]["documents"][-1]["url"])
    self.assertNotIn("Expires=", response.json["data"]["documents"][-1]["url"])

    contract = self.db.get(contract["id"])
    self.assertIn(
        "Prefix=ce536c5f46d543ec81ffa86ce4c77c8b%2F9c8b66120d4c415cb334bbad33f94ba9", contract["documents"][-1]["url"]
    )
    self.assertIn("/da839a4c3d7a41d2852d17f90aa14f47?", contract["documents"][-1]["url"])
    self.assertIn("Signature=", contract["documents"][-1]["url"])
    self.assertIn("KeyID=", contract["documents"][-1]["url"])
    self.assertNotIn("Expires=", contract["documents"][-1]["url"])


def contract_wo_items_status_change(self):
    tender_token = self.initial_data["tender_token"]

    response = self.app.get("/contracts/{}".format(self.contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertNotIn("items", response.json["data"])

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        "/contracts/{}/credentials?acc_token={}".format(self.contract["id"], tender_token), {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {"data": {"value": {"amountNet": self.contract["value"]["amount"] - 1}}},
    )

    # active > terminated allowed
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token), {"data": {"status": "terminated"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"description": u"Can't terminate contract while 'amountPaid' is not set",
                u"location": u"body",
                u"name": u"data",
            }
        ],
    )

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token),
        {
            "data": {
                "status": "terminated",
                "amountPaid": {"amount": 100, "amountNet": 99, "valueAddedTaxIncluded": True, "currency": "UAH"},
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "terminated")

    # terminated > active not allowed
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract["id"], token), {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")


def contract_token_invalid(self):
    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract_id, "fake token"), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Forbidden", u"location": u"url", u"name": u"permission"}]
    )

    response = self.app.patch_json(
        "/contracts/{}?acc_token={}".format(self.contract_id, "токен з кирилицею"), {"data": {}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Forbidden", u"location": u"url", u"name": u"permission"}]
    )


def generate_credentials_invalid(self):
    response = self.app.patch_json(
        "/contracts/{0}/credentials?acc_token={1}".format(self.contract_id, "fake token"), {"data": ""}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Forbidden", u"location": u"url", u"name": u"permission"}]
    )

    response = self.app.patch_json(
        "/contracts/{0}/credentials?acc_token={1}".format(self.contract_id, "токен з кирилицею"),
        {"data": ""},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Forbidden", u"location": u"url", u"name": u"permission"}]
    )


def skip_address_validation(self):
    initial_data = deepcopy(self.initial_data)
    initial_data["items"][0]["deliveryAddress"]["countryName"] = "any country"
    initial_data["items"][0]["deliveryAddress"]["region"] = "any region"
    u = Contract(self.initial_data)
    u.contractID = "UA-C"
    u.store(self.db)
    assert u.rev is not None
