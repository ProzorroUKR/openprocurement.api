from copy import deepcopy
from datetime import datetime, timedelta
from uuid import uuid4

from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.utils import get_now
from openprocurement.contracting.core.tests.data import documents
from openprocurement.contracting.econtract.tests.data import test_signer_info
from openprocurement.contracting.econtract.tests.utils import create_contract


def simple_add_contract(self):
    u = deepcopy(self.initial_data)
    u["dateModified"] = get_now().isoformat()
    u["contractID"] = "UA-C"

    # assert u["id"] == self.initial_data["id"]
    # assert u["doc_id"] == self.initial_data["id"]
    # assert u["rev"] is None

    self.mongodb.contracts.save(u, insert=True)

    assert u["_id"] == self.initial_data["id"]
    # assert u.rev is not None

    fromdb = self.mongodb.contracts.get(u["_id"])

    assert u["contractID"] == fromdb["contractID"]
    assert "doc_type" not in u

    self.mongodb.contracts.delete(u["_id"])


def empty_listing(self):
    response = self.app.get("/contracts")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertNotIn('{\n    "', response.body.decode())
    self.assertNotIn("callback({", response.body.decode())
    self.assertEqual(response.json["next_page"]["offset"], "")
    self.assertNotIn("prev_page", response.json)

    response = self.app.get("/contracts?opt_jsonp=callback")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertNotIn('{\n    "', response.body.decode())
    self.assertIn("callback({", response.body.decode())

    response = self.app.get("/contracts?opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "', response.body.decode())
    self.assertNotIn("callback({", response.body.decode())

    response = self.app.get("/contracts?opt_jsonp=callback&opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('{\n    "', response.body.decode())
    self.assertIn("callback({", response.body.decode())

    offset = datetime.fromisoformat("2015-01-01T00:00:00+02:00").timestamp()
    response = self.app.get(f"/contracts?offset={offset}&descending=1&limit=10")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], [])
    self.assertIn("descending=1", response.json["next_page"]["uri"])
    self.assertIn("limit=10", response.json["next_page"]["uri"])
    self.assertNotIn("descending=1", response.json["prev_page"]["uri"])
    self.assertIn("limit=10", response.json["prev_page"]["uri"])

    response = self.app.get("/contracts?offset=latest", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": "Invalid offset provided: latest", "location": "querystring", "name": "offset"}],
    )

    response = self.app.get("/contracts?descending=1&limit=10")
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
        contracts.append(create_contract(self, data))

    ids = ",".join([i["id"] for i in contracts])

    response = self.app.get("/contracts")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))

    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in contracts})
    self.assertEqual({i["dateModified"] for i in response.json["data"]}, {i["dateModified"] for i in contracts})
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in contracts]))

    response = self.app.get("/contracts?limit=1")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("prev_page", response.json)
    self.assertEqual(len(response.json["data"]), 1)
    offset = response.json["next_page"]["offset"]

    response = self.app.get(f"/contracts?offset={offset}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 2)

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
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "contractID"})
    self.assertIn("opt_fields=contractID", response.json["next_page"]["uri"])

    response = self.app.get("/contracts?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in contracts})
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
    create_contract(self, test_contract_data2)

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
        contracts.append(create_contract(self, data))

    ids = ",".join([i["id"] for i in contracts])

    while True:
        response = self.app.get("/contracts?feed=changes")
        self.assertEqual(response.status, "200 OK")
        self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))
        if len(response.json["data"]) == 3:
            break

    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in contracts})
    self.assertEqual({i["dateModified"] for i in response.json["data"]}, {i["dateModified"] for i in contracts})
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
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified", "contractID"})
    self.assertIn("opt_fields=contractID", response.json["next_page"]["uri"])

    response = self.app.get("/contracts?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), {"id", "dateModified"})
    self.assertEqual({i["id"] for i in response.json["data"]}, {i["id"] for i in contracts})
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
    create_contract(self, test_contract_data2)

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

    contract = create_contract(self, self.initial_data)
    self.assertEqual(contract["id"], self.initial_data["id"])

    response = self.app.get(f"/contracts/{contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], contract)

    response = self.app.get(f"/contracts/{contract['id']}?opt_jsonp=callback")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/javascript")
    self.assertIn('callback({"data": {"', response.body.decode())

    response = self.app.get(f"/contracts/{contract['id']}?opt_pretty=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn('{\n    "data": {\n        "', response.body.decode())


def not_found(self):
    response = self.app.get("/contracts")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    contract = create_contract(self, self.initial_data)
    self.assertEqual(contract["id"], self.initial_data["id"])

    while True:
        response = self.app.get("/contracts")
        self.assertEqual(response.status, "200 OK")
        if len(response.json["data"]) == 1:
            break
    self.assertEqual(len(response.json["data"]), 1)

    tender_id = self.initial_data["tender_id"]
    response = self.app.get(f"/contracts/{tender_id}", status=404)
    self.assertEqual(response.status, "404 Not Found")

    data = self.initial_data.copy()
    data["id"] = uuid4().hex
    create_contract(self, data)

    response = self.app.get(f"/contracts/{data['id']}")
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/contracts/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.patch_json("/contracts/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])


def put_transaction_to_contract(self):
    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    tender_token = self.initial_data["tender_token"]
    credentials_url = f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}"
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.put_json(
        f"/contracts/{self.contract['id']}/transactions/{12345}?acc_token={'fake_token'}", {"data": ""}, status=403
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}])

    response = self.app.put_json(
        f"/contracts/{self.contract['id']}/transactions/{12345}?acc_token={self.tender_token}",
        {
            "data": {
                "date": "2020-05-20T18:47:47.136678+02:00",
                "value": {"amount": 500, "currency": "UAH"},
                "payer": {
                    "bankAccount": {
                        "id": 789,
                        "scheme": "IBAN",
                    },
                    "name": "payer1",
                },
                "payee": {
                    "bankAccount": {
                        "id": 888,
                        "scheme": "IBAN",
                    },
                    "name": "payee1",
                },
                "status": 0,
            }
        },
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
                    "name": "payer1",
                },
                'value': {'currency': 'UAH', 'amount': 500.0},
                'payee': {
                    "bankAccount": {
                        "id": "888",
                        "scheme": "IBAN",
                    },
                    "name": "payee1",
                },
                'date': '2020-05-20T18:47:47.136678+02:00',
                'id': '12345',
            }
        ],
    )

    response = self.app.put_json(
        f"/contracts/{self.contract['id']}/transactions/{12345}?acc_token={self.tender_token}",
        {
            "data": {
                "date": "2020-05-20T18:47:47.136678+02:00",
                "value": {"amount": 500, "currency": "UAH"},
                "payer": {
                    "bankAccount": {
                        "id": 800000000,
                        "scheme": "IBAN",
                    },
                    "name": "payer_should_not_applied1",
                },
                "payee": {
                    "bankAccount": {
                        "id": 90000000,
                        "scheme": "IBAN",
                    },
                    "name": "payee_should_not_applied1",
                },
                "status": "new_status_123",
            }
        },
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
                    "name": "payer1",
                },
                'value': {'currency': 'UAH', 'amount': 500.0},
                'payee': {
                    "bankAccount": {
                        "id": "888",
                        "scheme": "IBAN",
                    },
                    "name": "payee1",
                },
                'date': '2020-05-20T18:47:47.136678+02:00',
                'id': '12345',
            }
        ],
    )

    response = self.app.put_json(
        f"/contracts/{self.contract['id']}/transactions/{90800777}?acc_token={self.tender_token}",
        {
            "data": {
                "date": "2020-06-10T10:47:47.136678+02:00",
                "value": {"amount": 14500.5, "currency": "UAH"},
                "payer": {
                    "bankAccount": {
                        "id": 78999,
                        "scheme": "IBAN",
                    },
                    "name": "payer2",
                },
                "payee": {
                    "bankAccount": {
                        "id": 199000,
                        "scheme": "IBAN",
                    },
                    "name": "payee2",
                },
                "status": -1,
            }
        },
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
                    "name": "payer1",
                },
                'value': {'currency': 'UAH', 'amount': 500.0},
                'payee': {
                    "bankAccount": {
                        "id": "888",
                        "scheme": "IBAN",
                    },
                    "name": "payee1",
                },
                'date': '2020-05-20T18:47:47.136678+02:00',
                'id': '12345',
            },
            {
                'status': 'canceled',
                'payer': {
                    "bankAccount": {
                        "id": "78999",
                        "scheme": "IBAN",
                    },
                    "name": "payer2",
                },
                'value': {'currency': 'UAH', 'amount': 14500.5},
                'payee': {
                    "bankAccount": {
                        "id": "199000",
                        "scheme": "IBAN",
                    },
                    'name': 'payee2',
                },
                'date': '2020-06-10T10:47:47.136678+02:00',
                'id': '90800777',
            },
        ],
    )

    response = self.app.put_json(
        f"/contracts/{self.contract['id']}/transactions/{111122}?acc_token={self.tender_token}",
        {
            "data": {
                "date": "2020-06-10T10:47:47.136678+02:00",
                "value": {
                    "amount": 18500.5,
                    "currency": "UAH",
                },
            }
        },
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {'description': ['This field is required.'], 'location': 'body', 'name': 'payer'},
            {'description': ['This field is required.'], 'location': 'body', 'name': 'payee'},
            {'description': ['This field is required.'], 'location': 'body', 'name': 'status'},
        ],
    )

    response = self.app.put_json(
        f"/contracts/{self.contract['id']}/transactions/{3444444}?acc_token={self.tender_token}",
        {
            "data": {
                "date": "2020-06-10T10:47:47.136678+02:00",
                "value": {"amount": 14500.5, "currency": "UAH"},
                "payer": {
                    "bankAccount": {
                        "id": "789",
                        "scheme": "IBAN",
                    },
                    "name": "payer2",
                },
                "payee": "payee_invalid_structure",
                "status": "Accepted_status_123",
            }
        },
        status=422,
    )

    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': [
                    'Please use a mapping for this field or OrganizationReference instance instead of str.'
                ],
                'location': 'body',
                'name': 'payee',
            }
        ],
    )
    response = self.app.get(f"/contracts/{self.contract['id']}")
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
                    "name": "payer1",
                },
                'value': {'currency': 'UAH', 'amount': 500.0},
                'payee': {
                    "bankAccount": {
                        "id": "888",
                        "scheme": "IBAN",
                    },
                    "name": "payee1",
                },
                'date': '2020-05-20T18:47:47.136678+02:00',
                'id': '12345',
            },
            {
                'status': 'canceled',
                'payer': {
                    "bankAccount": {
                        "id": "78999",
                        "scheme": "IBAN",
                    },
                    "name": "payer2",
                },
                'value': {'currency': 'UAH', 'amount': 14500.5},
                'payee': {
                    "bankAccount": {
                        "id": "199000",
                        "scheme": "IBAN",
                    },
                    "name": "payee2",
                },
                'date': '2020-06-10T10:47:47.136678+02:00',
                'id': '90800777',
            },
        ],
    )
    response = self.app.get(f"/contracts/{self.contract['id']}/transactions/{2222222}", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(
        response.json["errors"], [{'description': 'Not Found', 'location': 'url', 'name': 'transaction_id'}]
    )

    response = self.app.put_json(
        f"/contracts/{self.contract['id']}/transactions/{5555}?acc_token={self.tender_token}",
        {
            "data": {
                "date": "2020-06-10T10:47:47.136678+02:00",
                "value": {"amount": 14500.5, "currency": "UAH"},
                "payer": {
                    "bankAccount": {
                        "id": "789",
                        "scheme": "INCORRECT_SCHEMA",
                    },
                    "name": "payer2",
                },
                "payee": {"bankAccount": {"id": "789"}, "name": "payee2"},
                "status": 0,
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': {'bankAccount': {'scheme': ["Value must be one of ['IBAN']."]}},
                'location': 'body',
                'name': 'payer',
            },
            {
                'description': {'bankAccount': {'scheme': ["This field is required."]}},
                'location': 'body',
                'name': 'payee',
            },
        ],
    )

    response = self.app.get(f"/contracts/{self.contract['id']}/transactions/{12345}")
    self.assertEqual(
        response.json['data'],
        {
            'status': 'new_status_123',
            'payer': {
                "bankAccount": {
                    "id": "789",
                    "scheme": "IBAN",
                },
                'name': 'payer1',
            },
            'value': {'currency': 'UAH', 'amount': 500.0},
            'payee': {
                "bankAccount": {
                    "id": "888",
                    "scheme": "IBAN",
                },
                'name': 'payee1',
            },
            'date': '2020-05-20T18:47:47.136678+02:00',
            'id': '12345',
        },
    )


def create_contract_transfer_token(self):
    contract = create_contract(self, self.initial_data)
    self.assertNotIn("transfer_token", contract)


def contract_date_signed(self):
    # TODO: write dateSigned tests in pending and active statuses
    pass


def contract_status_change(self):
    tender_token = self.initial_data["tender_token"]

    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    # pending > active allowed

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={tender_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")

    # response = self.app.patch_json(
    #     f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}", {"data": ""}
    # )
    # self.assertEqual(response.status, "200 OK")
    # token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {
            "data": {
                "value": {**self.contract["value"], "amountNet": self.contract["value"]["amountNet"] - 1},
                "title": "Changed title",
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amountNet"], self.contract["value"]["amountNet"] - 1)
    self.assertEqual(response.json["data"]["title"], "Changed title")

    response = self.app.get(f"/tenders/{self.tender_id}/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amountNet"], self.contract["value"]["amountNet"] - 1)
    self.assertNotIn("title", response.json["data"])

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"description": "Changed description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["description"], "Changed description")

    response = self.app.get(f"/tenders/{self.tender_id}/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("description", response.json["data"])

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/buyer/signer_info?acc_token={self.tender_token}", {"data": test_signer_info}
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/suppliers/signer_info?acc_token={self.bid_token}", {"data": test_signer_info}
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.get(f"/tenders/{self.tender_id}/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertEqual(response.json["data"]["status"], self.contract["status"])

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get(f"/tenders/{self.tender_id}/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "complete")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": {**self.contract["value"], "amountNet": self.contract["value"]["amountNet"] + 3}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amountNet"], self.contract["value"]["amountNet"] + 3)

    response = self.app.get(f"/tenders/{self.tender_id}/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amountNet"], self.contract["value"]["amountNet"] - 1)

    # active > cancelled not allowed
    # response = self.app.patch_json(
    #     f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
    #     {"data": {"status": "cancelled"}},
    # )
    # self.assertEqual(response.status, "422 Unprocessable Entity")
    # self.assertEqual(response.json["errors"], [])

    # active > terminated allowed
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"status": "terminated"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't terminate contract while 'amountPaid' is not set",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {
            "data": {
                "status": "terminated",
                "amountPaid": {"amount": 100, "amountNet": 90, "valueAddedTaxIncluded": True, "currency": "UAH"},
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "terminated")

    response = self.app.get(f"/tenders/{self.tender_id}/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    # terminated > active not allowed
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}", {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")


def contract_items_change(self):
    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    items = response.json["data"]["items"]

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": {"amountNet": self.contract["value"]["amountNet"] - 1}}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "value", "description": {"amount": ["This field is required."]}}],
    )

    item = self.contract["items"][0]
    # try to delete field which is forbidden to patch
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"items": [{**item, "quantity": 12, "unit": None}]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Forbidden to delete fields {'unit'}",
            }
        ],
    )
    # try to modify field which is forbidden to patch
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"items": [{**item, "quantity": 12, "description": "тапочки для тараканів"}]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Updated could be only ('unit', 'quantity') in item, description change forbidden",
            }
        ],
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {
            "data": {
                "items": [
                    {**item, "unit": {**item["unit"], "value": {**item["unit"]["value"], "amount": 22}}, "quantity": 10}
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["amount"], 22)
    self.assertEqual(response.json["data"]["items"][0]["quantity"], 10)

    self.set_status("active")

    # try to delete field in nested object during patch
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {
            "data": {
                "items": [
                    {
                        **item,
                        "deliveryAddress": {
                            "countryName": "Україна",
                            "streetAddress": "вул. Банкова 1",
                            "region": "м. Київ",
                            "locality": "м. Київ",
                            "countryName_en": "Ukraine",
                        },
                    }
                ]
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Forbidden to delete fields in deliveryAddress: {'postalCode'}",
            }
        ],
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"items": [{**item, "quantity": 12, "description": "тапочки для тараканів"}]}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "items",
                "description": "Total amount of unit values must be no more than contract.value.amount and no less than net contract amount",
            }
        ],
    )
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"items": [{**item, "quantity": 2, "description": "тапочки для тараканів"}]}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "items",
                "description": "Total amount of unit values must be no more than contract.value.amount and no less than net contract amount",
            }
        ],
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {
            "data": {
                "items": [{**item, "quantity": -1, "description": "тапочки для тараканів"}],
            }
        },
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
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

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {
            "data": {
                "items": [
                    {
                        **item,
                        "quantity": 12,
                        "description": "тапочки для тараканів",
                        "unit": {
                            "code": "KGM",
                            "name": "кг",
                            "value": {"currency": "UAH", "amount": 18.2394, "valueAddedTaxIncluded": True},
                        },
                    }
                ]
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["quantity"], 12)
    self.assertEqual(
        response.json["data"]["items"][0]["classification"],
        {"scheme": "CPV", "description": "Cartons", "id": "44617100-9"},
    )
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["amount"], 18.2394)
    self.assertEqual(response.json["data"]["items"][0]["description"], "тапочки для тараканів")

    # add one more item
    old_item = deepcopy(items[0])
    item = deepcopy(old_item)
    item["quantity"] = 11
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"items": [old_item, item]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "items", "description": ["Item id should be uniq for all items"]}],
    )

    item_patch_fields = (
        "description",
        "description_en",
        "description_ru",
        "unit",
        "deliveryDate",
        "deliveryAddress",
        "deliveryLocation",
        "quantity",
    )

    # try to change classification
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"items": [{**old_item, "classification": {"id": "19433000-0", "description": "Cartons"}}]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": f"Updated could be only {item_patch_fields} in item, "
                f"classification change forbidden",
            }
        ],
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"items": [old_item]}},
    )
    self.assertEqual(response.status, "200 OK")
    # self.assertEqual(response.json, None)

    # try to add additional classification
    item_classific = deepcopy(self.initial_data["items"][0]["classification"])
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {
            "data": {
                "items": [
                    {
                        **old_item,
                        "additionalClassifications": [old_item["additionalClassifications"][0], item_classific],
                    }
                ]
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": f"Updated could be only {item_patch_fields} in item, "
                f"additionalClassifications change forbidden",
            }
        ],
    )

    # update item fields
    startDate = get_now().isoformat()
    endDate = (get_now() + timedelta(days=90)).isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {
            "data": {
                "items": [
                    {
                        **old_item,
                        "quantity": 5.005,
                        "deliveryAddress": {
                            **old_item["deliveryAddress"],
                            "postalCode": "79011",
                            "streetAddress": "вул. Літаючого Хом’яка",
                        },
                        "deliveryDate": {"startDate": startDate, "endDate": endDate},
                    }
                ]
            }
        },
    )
    self.assertEqual(response.json["data"]["items"][0]["quantity"], 5.005)
    self.assertEqual(response.json["data"]["items"][0]["deliveryAddress"]["postalCode"], "79011")
    self.assertEqual(response.json["data"]["items"][0]["deliveryAddress"]["streetAddress"], "вул. Літаючого Хом’яка")
    self.assertEqual(response.json["data"]["items"][0]["deliveryAddress"]["region"], "м. Київ")
    self.assertEqual(response.json["data"]["items"][0]["deliveryAddress"]["locality"], "м. Київ")
    self.assertEqual(response.json["data"]["items"][0]["deliveryAddress"]["countryName"], "Україна")
    self.assertEqual(response.json["data"]["items"][0]["deliveryDate"]["startDate"], startDate)
    self.assertEqual(response.json["data"]["items"][0]["deliveryDate"]["endDate"], endDate)

    # try to remove all items
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}", {"data": {"items": []}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")


def contract_update_add_remove_items(self):
    tender_token = self.initial_data["tender_token"]

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}", {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    items = response.json["data"]["items"]

    # try to remove one item
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}", {"data": {"items": [items[0]]}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "data", "description": "Can't change items list length"}]
    )

    # try to remove all items
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}", {"data": {"items": []}}, status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "items", "description": ['Please provide at least 1 item.']}],
    )

    # try to add item
    new_item = deepcopy(items[0])
    new_item['id'] = "new_id"
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {
            "data": {
                "items": [
                    items[0],
                    items[1],
                    new_item,
                ]
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "data", "description": "Can't change items list length"}]
    )


def patch_tender_contract(self):
    response = self.app.patch_json(f"/contracts/{self.contract['id']}", {"data": {"title": "New Title"}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")

    tender_token = self.initial_data["tender_token"]
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={tender_token}",
        {"data": {"title": "New Title"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "New Title")

    credentials_url = f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}"
    response = self.app.patch_json(credentials_url, {"data": ""})

    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {
            "data": {
                "value": {
                    **self.contract["value"],
                    "amount": self.contract["value"]["amount"] - 10,
                    "amountNet": self.contract["value"]["amountNet"] - 1,
                }
            }
        },
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}", {"data": {"title": "New Title!!!"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "New Title!!!")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"amountPaid": {"amount": 100, "amountNet": 90}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{'description': 'Rogue field', 'location': 'body', 'name': 'amountPaid'}],
    )

    custom_period_start_date = get_now().isoformat()
    custom_period_end_date = (get_now() + timedelta(days=3)).isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"period": {"startDate": custom_period_start_date, "endDate": custom_period_end_date}}},
    )
    self.assertEqual(response.status, "200 OK")

    self.set_status("active")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"amountPaid": {"amount": 100, "amountNet": 90}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["amountPaid"]["amount"], 100)
    self.assertEqual(response.json["data"]["amountPaid"]["amountNet"], 90)
    self.assertEqual(response.json["data"]["amountPaid"]["currency"], "UAH")
    self.assertEqual(response.json["data"]["amountPaid"]["valueAddedTaxIncluded"], True)

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"status": "terminated", "amountPaid": {"amount": 90, "amountNet": 80}, "terminationDetails": "sink"}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}", {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}", {"data": {"title": "fff"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json("/contracts/some_id", {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "terminated")
    self.assertEqual(response.json["data"]["value"]["amount"], self.contract["value"]["amount"] - 10)
    self.assertEqual(response.json["data"]["period"]["startDate"], custom_period_start_date)
    self.assertEqual(response.json["data"]["period"]["endDate"], custom_period_end_date)
    self.assertEqual(response.json["data"]["amountPaid"]["amount"], 90)
    self.assertEqual(response.json["data"]["amountPaid"]["amountNet"], 80)
    self.assertEqual(response.json["data"]["terminationDetails"], "sink")


def patch_tender_contract_readonly(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}"
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"value": {**self.contract["value"], "currency": "USD"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")


def patch_tender_contract_value_vat_change(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}"
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    # check that contract.value.valueAddedTaxIncluded is True
    self.assertEqual(
        response.json["data"]["value"]["valueAddedTaxIncluded"],
        True,
    )

    # set contract.amountPaid
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"amountPaid": {"amount": 238, "amountNet": 200}}},
    )

    # check contract.amountPaid.valueAddedTaxIncluded
    # copied from contract.value.valueAddedTaxIncluded
    # if it was not set in request
    self.assertEqual(
        response.json["data"]["amountPaid"]["valueAddedTaxIncluded"],
        response.json["data"]["value"]["valueAddedTaxIncluded"],
    )

    # check contract.items.unit.value.valueAddedTaxIncluded is False
    for item in response.json["data"]["items"]:
        self.assertEqual(
            item["unit"]["value"]["valueAddedTaxIncluded"],
            False,
        )
    contract_items = response.json["data"]["items"]
    contract_items[0]["unit"]["value"]["amount"] = 21.64
    contract_items[0]["quantity"] = 11  # 11 * 21.64 = 238.04

    # change contract.value.valueAddedTaxIncluded from True to False
    print("HERE")
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"value": {"valueAddedTaxIncluded": False, "amount": 238, "amountNet": 238}, "items": contract_items}},
    )
    contract = response.json["data"]
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(contract["value"]["amount"], 238)
    self.assertEqual(contract["value"]["amountNet"], 238)

    # check that contract.value.valueAddedTaxIncluded is False
    self.assertEqual(
        response.json["data"]["value"]["valueAddedTaxIncluded"],
        False,
    )

    # check contract.items.unit.value.valueAddedTaxIncluded
    # updated from contract.value.valueAddedTaxIncluded
    for item in response.json["data"]["items"]:
        self.assertEqual(
            item["unit"]["value"]["valueAddedTaxIncluded"],
            response.json["data"]["value"]["valueAddedTaxIncluded"],
        )

    # check contract.amountPaid.valueAddedTaxIncluded
    # was not updated with contract.value.valueAddedTaxIncluded
    self.assertNotEqual(
        response.json["data"]["amountPaid"]["valueAddedTaxIncluded"],
        response.json["data"]["value"]["valueAddedTaxIncluded"],
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"amountPaid": {"valueAddedTaxIncluded": False, "amount": 238, "amountNet": 239}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount and amountNet should be equal")


def patch_tender_contract_identical(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}"
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"amountPaid": {"amount": 100, "amountNet": 90, "currency": "USD"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "currency of amountPaid should be identical to currency of value of contract",
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"amountPaid": {"amount": 100, "amountNet": 90}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertIn("amountPaid", response.json["data"])

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}", {"data": {"amountPaid": None}}
    )
    self.assertEqual(response.status, "200 OK")


def patch_tender_contract_without_value(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}"
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    contract_doc = self.mongodb.contracts.get(self.contract["id"])
    del contract_doc['value']
    self.mongodb.contracts.save(contract_doc)

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"amountPaid": {"amount": 100, "amountNet": 100, "valueAddedTaxIncluded": False}}},
    )


def patch_tender_contract_value_amount(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}"
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"value": {**self.contract["value"], "amount": 235, "amountNet": 237}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be equal or greater than amountNet and differ by no more than 20.0%",
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"value": {"amount": 235, "amountNet": 100}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be equal or greater than amountNet and differ by no more than 20.0%",
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"value": {"amount": 235, "amountNet": 201}}},
    )
    self.assertEqual(response.status, "200 OK")

    self.assertEqual(response.json["data"]["value"]["amount"], 235)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 201)
    self.assertEqual(response.json["data"]["value"]["currency"], "UAH")
    self.assertEqual(response.json["data"]["value"]["valueAddedTaxIncluded"], True)

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {
            "data": {
                "status": "terminated",
                "amountPaid": {"amount": 100, "amountNet": 100},
                "terminationDetails": "sink",
            }
        },
    )
    self.assertEqual(response.status, "200 OK")


def patch_tender_contract_amount_paid_zero(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}"
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"amountPaid": {"amount": 0, "amountNet": 0}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["amountPaid"]["amount"], 0)
    self.assertEqual(response.json["data"]["amountPaid"]["amountNet"], 0)
    self.assertEqual(response.json["data"]["amountPaid"]["valueAddedTaxIncluded"], True)


def patch_tender_contract_period(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}"
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")

    previous_period = {
        "startDate": "2016-02-20T18:47:47.155143+02:00",
        "endDate": "2016-06-15T18:47:47.155143+02:00",
    }

    contract_doc = self.mongodb.contracts.get(self.contract["id"])
    contract_doc['period'] = previous_period
    self.mongodb.contracts.save(contract_doc)

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={tender_token}",
        {
            "data": {
                "period": {
                    "startDate": "2016-06-10T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertNotEqual(
        response.json["data"]["period"]["startDate"],
        previous_period["startDate"],
    )
    self.assertIn("endDate", response.json["data"]["period"])

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={tender_token}",
        {
            "data": {
                "period": {
                    "endDate": "2016-06-20T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertNotEqual(
        response.json["data"]["period"]["endDate"],
        previous_period["endDate"],
    )
    self.assertIn("startDate", response.json["data"]["period"])

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={tender_token}",
        {
            "data": {
                "period": {
                    "endDate": "2016-06-01T18:47:47.155143+02:00",
                },
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "period should begin before its end",
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={tender_token}",
        {
            "data": {
                "period": {
                    "startDate": "2016-03-20T18:47:47.155143+02:00",
                    "endDate": "2016-06-20T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["period"]["startDate"], "2016-03-20T18:47:47.155143+02:00")


def patch_tender_contract_single_request(self):
    tender_token = self.initial_data["tender_token"]
    credentials_url = f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}"
    response = self.app.patch_json(credentials_url, {"data": ""})
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    self.assertEqual(response.json["data"]["value"]["valueAddedTaxIncluded"], True)
    contract_items = response.json["data"]["items"]
    contract_items[0]["unit"]["value"]["amount"] = 16.7
    contract_items[0]["quantity"] = 15  # 15 * 16.7 = 250.5

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {
            "data": {
                "value": {"valueAddedTaxIncluded": False, "amount": 250, "amountNet": 250},
                "amountPaid": {"valueAddedTaxIncluded": False, "amount": 100, "amountNet": 100},
                "status": "terminated",
                "terminationDetails": "sink",
                "items": contract_items,
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["valueAddedTaxIncluded"], False)
    self.assertEqual(response.json["data"]["amountPaid"]["valueAddedTaxIncluded"], False)


def patch_tender_contract_wo_amount_net(self):
    tender_token = self.initial_data["tender_token"]

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}", {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"value": {**self.contract["value"], "amount": self.contract["value"]["amount"] - 1}}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"description": {"amountNet": "This field is required."}, "location": "body", "name": "value"}],
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"value": {"amount": 235, "amountNet": 200}}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"amountPaid": {"amount": 235}, "status": "terminated", "terminationDetails": "sink"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"description": {"amountNet": "This field is required."}, "location": "body", "name": "amountPaid"}],
    )


def contract_administrator_change(self):
    supplier = self.contract["suppliers"][0]
    buyer = self.contract["buyer"]
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}",
        {
            "data": {
                "mode": "test",
                "suppliers": [{**supplier, "address": {**supplier["address"], "postalCode": "79014"}}],
                "buyer": {
                    **buyer,
                    "identifier": {**buyer["identifier"], "id": "11111111"},
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["mode"], "test")
    self.assertEqual(response.json["data"]["buyer"]["identifier"]["id"], "11111111")
    self.assertEqual(response.json["data"]["suppliers"][0]["address"]["postalCode"], "79014")
    # administrator has permissions to update only: mode, procuringEntity, suppliers
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}",
        {
            "data": {
                "value": {"amount": 100500},
                "id": "1234" * 8,
                "owner": "kapitoshka",
                "contractID": "UA-00-00-00",
                "dateSigned": get_now().isoformat(),
            }
        },
        status=422,
    )
    self.assertIn({'description': 'Rogue field', 'location': 'body', 'name': 'owner'}, response.json["errors"])
    self.assertIn({'description': 'Rogue field', 'location': 'body', 'name': 'value'}, response.json["errors"])
    self.assertIn({'description': 'Rogue field', 'location': 'body', 'name': 'dateSigned'}, response.json["errors"])
    self.assertIn({'description': 'Rogue field', 'location': 'body', 'name': 'contractID'}, response.json["errors"])
    self.assertIn({'description': 'Rogue field', 'location': 'body', 'name': 'id'}, response.json["errors"])

    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.json["data"]["value"]["amount"], self.contract["value"]["amount"])
    self.assertEqual(response.json["data"]["id"], self.initial_data["id"])
    self.assertEqual(response.json["data"]["owner"], self.initial_data["owner"])
    self.assertEqual(response.json["data"]["contractID"], self.initial_data["contractID"])


def get_credentials(self):
    response = self.app.get(
        f"/contracts/{self.contract_id}/credentials?acc_token={self.initial_data['tender_token']}",
        status=405,
    )
    self.assertEqual(response.status, "405 Method Not Allowed")


def generate_credentials(self):
    tender_token = self.initial_data["tender_token"]
    response = self.app.patch_json(f"/contracts/{self.contract_id}/credentials?acc_token={tender_token}", {"data": ""})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["id"], self.initial_data["id"])
    self.assertNotIn("tender_token", response.json["data"])
    self.assertNotIn("owner_token", response.json["data"])
    self.assertEqual(response.json["data"]["owner"], "broker")
    self.assertEqual(len(response.json["access"]["token"]), 32)
    token1 = response.json["access"]["token"]

    # try second time generation
    response = self.app.patch_json(f"/contracts/{self.contract_id}/credentials?acc_token={tender_token}", {"data": ""})
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["id"], self.initial_data["id"])
    self.assertEqual(len(response.json["access"]["token"]), 32)
    token2 = response.json["access"]["token"]
    self.assertNotEqual(token1, token2)

    # first access token is non-workable
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={token1}", {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token2}",
        {"data": {"value": {**self.contract["value"], "amountNet": self.contract["value"]["amountNet"] - 1}}},
    )
    # terminated contract is also protected
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={token2}",
        {"data": {"status": "terminated", "amountPaid": {"amount": 100, "amountNet": 90}}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/credentials?acc_token={tender_token}", {"data": ""}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't generate credentials in current (terminated) contract status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def create_contract_w_documents(self):
    data = self.initial_data.copy()
    data["documents"] = documents
    contract = create_contract(self, data)
    self.assertEqual(contract["status"], "pending")
    for index, doc in enumerate(documents):
        self.assertEqual(contract["documents"][index]["id"], doc["id"])
        self.assertEqual(contract["documents"][index]["datePublished"], doc["datePublished"])
        self.assertEqual(contract["documents"][index]["dateModified"], doc["dateModified"])

    self.assertNotIn("Signature=", contract["documents"][-1]["url"])
    self.assertNotIn("KeyID=", contract["documents"][-1]["url"])
    self.assertNotIn("Expires=", contract["documents"][-1]["url"])

    contract = self.mongodb.contracts.get(contract["id"])
    self.assertNotIn(
        "Prefix=ce536c5f46d543ec81ffa86ce4c77c8b%2F9c8b66120d4c415cb334bbad33f94ba9", contract["documents"][-1]["url"]
    )
    self.assertNotIn("/da839a4c3d7a41d2852d17f90aa14f47?", contract["documents"][-1]["url"])
    self.assertNotIn("Signature=", contract["documents"][-1]["url"])
    self.assertNotIn("KeyID=", contract["documents"][-1]["url"])
    self.assertNotIn("Expires=", contract["documents"][-1]["url"])


def contract_wo_items_status_change(self):
    response = self.app.get(f"/contracts/{self.contract_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertNotIn("items", response.json["data"])

    # pending > terminated disallowed

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"status": "terminated"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{"location": "body", "name": "data", "description": "Can't update contract status"}]
    )

    # set signerInfo for buyer
    response = self.app.put_json(
        f"/contracts/{self.contract['id']}/buyer/signer_info?acc_token={self.tender_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    # set signerInfo for suppliers
    response = self.app.put_json(
        f"/contracts/{self.contract['id']}/suppliers/signer_info?acc_token={self.bid_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    # pending > active allowed

    contract_value = {**self.contract["value"], "amountNet": self.contract["value"]["amountNet"] - 1}
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
        {
            "data": {
                "status": "active",
                "value": contract_value,
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    # active > terminated allowed
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"status": "terminated"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't terminate contract while 'amountPaid' is not set",
                "location": "body",
                "name": "data",
            }
        ],
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
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
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}", {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")


def contract_validate_signer_info(self):
    response = self.app.get(f"/contracts/{self.contract_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertNotIn("items", response.json["data"])

    # set contractTemplateName
    contract_document = self.mongodb.contracts.get(self.contract_id)
    contract_document["contractTemplateName"] = "test"
    self.mongodb.contracts.save(contract_document)

    # if contractTemplateName is set, signerInfo is required in active status on activation
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'location': 'body',
                'name': 'data',
                'description': 'signerInfo field for buyer and suppliers is required for contract in `active` status',
            }
        ],
    )

    # set signerInfo for buyer
    response = self.app.put_json(
        f"/contracts/{self.contract_id}/buyer/signer_info?acc_token={self.tender_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    # set signerInfo for suppliers
    response = self.app.put_json(
        f"/contracts/{self.contract_id}/suppliers/signer_info?acc_token={self.bid_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    # activate contract
    contract_value = {**self.contract["value"], "amountNet": self.contract["value"]["amountNet"] - 1}
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
        {
            "data": {
                "status": "active",
                "value": contract_value,
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")


def contract_token_invalid(self):
    response = self.app.patch_json(f"/contracts/{self.contract_id}?acc_token={'fake token'}", {"data": {}}, status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}])

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={'токен з кирилицею'}", {"data": {}}, status=422
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


def generate_credentials_invalid(self):
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/credentials?acc_token=fake token", {"data": ""}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}])

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/credentials?acc_token=токен з кирилицею",
        {"data": ""},
        status=422,
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


def contract_cancelled(self):
    tender_token = self.initial_data["tender_token"]

    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    # if only one active contract for tender pending > cancelled disallowed
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={tender_token}",
        {"data": {"status": "cancelled"}},
        status=403,
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can't update contract status"}],
    )

    # response = self.app.patch_json(
    #     f"/contracts/{self.contract['id']}?acc_token={tender_token}",
    #     {"data": {"status": "cancelled"}},
    # )
    # self.assertEqual(response.status, "200 OK")
    # self.assertEqual(response.json["data"]["status"], "cancelled")
    #
    # response = self.app.get(f"/tenders/{self.tender_id}")
    # self.assertEqual(response.status, "200 OK")
    # self.assertEqual(response.json["data"]["status"], "active.awarded")
    #
    # response = self.app.get(f"/tenders/{self.tender_id}/awards/{self.contract['awardID']}")
    # self.assertEqual(response.status, "200 OK")
    # self.assertEqual(response.json["data"]["status"], "active")
    #
    # response = self.app.get(f"/tenders/{self.tender_id}/contracts/{self.contract['id']}")
    # self.assertEqual(response.status, "200 OK")
    # self.assertEqual(response.json["data"]["status"], "cancelled")


def cancel_tender_award(self):
    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{self.contract['awardID']}?acc_token={self.tender_token}",
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.get(f"/tenders/{self.tender_id}/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")


def contract_activate(self):
    tender_token = self.initial_data["tender_token"]

    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}", {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "signerInfo field for buyer and suppliers is required for contract in `active` status",
            }
        ],
    )

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/buyer/signer_info?acc_token={self.tender_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/suppliers/signer_info?acc_token={self.bid_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "period is required for contract in `active` status",
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
        {
            "data": {
                "status": "active",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "contractNumber is required for contract in `active` status",
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
        {
            "data": {
                "status": "active",
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
