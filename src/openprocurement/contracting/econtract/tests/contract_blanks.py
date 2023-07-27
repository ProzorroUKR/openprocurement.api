from uuid import uuid4
from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import ROUTE_PREFIX
from openprocurement.api.utils import get_now
from openprocurement.contracting.api.tests.data import documents
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.contracting.econtract.tests.utils import create_contract
from openprocurement.contracting.econtract.tests.data import signer_info


def listing(self):
    response = self.app.get("/contracts")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 0)

    contracts = []

    for i in range(3):
        data = deepcopy(self.initial_data)
        data["id"] = uuid4().hex
        offset = get_now().timestamp()
        contracts.append(create_contract(self, data))

    ids = ",".join([i["id"] for i in contracts])

    response = self.app.get("/contracts")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertTrue(ids.startswith(",".join([i["id"] for i in response.json["data"]])))

    self.assertEqual(",".join([i["id"] for i in response.json["data"]]), ids)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
    self.assertEqual(set([i["id"] for i in response.json["data"]]), set([i["id"] for i in contracts]))
    self.assertEqual(
        set([i["dateModified"] for i in response.json["data"]]), set([i["dateModified"] for i in contracts])
    )
    self.assertEqual([i["dateModified"] for i in response.json["data"]], sorted([i["dateModified"] for i in contracts]))

    response = self.app.get(f"/contracts?offset={offset}")
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
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "contractID"]))
    self.assertIn("opt_fields=contractID", response.json["next_page"]["uri"])

    response = self.app.get("/contracts?descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
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
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
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
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified", "contractID"]))
    self.assertIn("opt_fields=contractID", response.json["next_page"]["uri"])

    response = self.app.get("/contracts?feed=changes&descending=1")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 3)
    self.assertEqual(set(response.json["data"][0]), set(["id", "dateModified"]))
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

    from openprocurement.tender.belowthreshold.tests.base import (
        test_tender_below_data,
        test_tender_below_config,
    )

    with change_auth(self.app, ("Basic", ("broker1", ""))):
        response = self.app.post_json("/tenders", {"data": test_tender_below_data, "config": test_tender_below_config})
    self.assertEqual(response.status, "201 Created")
    tender = response.json["data"]

    response = self.app.get(f"/contracts/{tender['id']}", status=404)
    self.assertEqual(response.status, "404 Not Found")

    data = deepcopy(self.initial_data)
    data["id"] = uuid4().hex
    data["tender_id"] = tender["id"]
    create_contract(self, data)

    response = self.app.get(f"/contracts/{tender['id']}", status=404)
    self.assertEqual(response.status, "404 Not Found")

    response = self.app.get(f"/contracts/{data['id']}")
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/contracts/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}]
    )

    response = self.app.patch_json("/contracts/some_id", {"data": {}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}]
    )


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
        f"/contracts/{self.contract['id']}/transactions/{12345}?acc_token={'fake_token'}",
        {"data": ""}, status=403
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}]
    )

    response = self.app.put_json(
        f"/contracts/{self.contract['id']}/transactions/{12345}?acc_token={token}",
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
        f"/contracts/{self.contract['id']}/transactions/{12345}?acc_token={token}",
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
        f"/contracts/{self.contract['id']}/transactions/{90800777}?acc_token={token}",
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
        f"/contracts/{self.contract['id']}/transactions/{111122}?acc_token={token}",
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
                'description': ['This field is required.'], 'location': 'body', 'name': 'payer'
            },
            {
                'description': ['This field is required.'], 'location': 'body', 'name': 'payee'
            },
            {
                'description': ['This field is required.'], 'location': 'body', 'name': 'status'
            }
        ]
    )

    response = self.app.put_json(
        f"/contracts/{self.contract['id']}/transactions/{3444444}?acc_token={token}",
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
                'description': [
                    'Please use a mapping for this field or OrganizationReference instance instead of str.'
                ],
                'location': 'body', 'name': 'payee'
            }
        ]
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
    response = self.app.get(f"/contracts/{self.contract['id']}/transactions/{2222222}", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(
        response.json["errors"],
        [{'description': 'Not Found', 'location': 'url', 'name': 'transaction_id'}]
    )

    response = self.app.put_json(
        f"/contracts/{self.contract['id']}/transactions/{5555}?acc_token={token}",
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
                        'scheme': ["Value must be one of ['IBAN']."]
                    }  
                },
                'location': 'body', 
                'name': 'payer'
            },
            {
                'description': {
                    'bankAccount': {
                        'scheme': ["This field is required."]
                    }
                },
                'location': 'body',
                'name': 'payee'
            },
        ]
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

    contract = create_contract(self, self.initial_data)
    self.assertNotIn("transfer_token", contract)


def contract_status_change(self):
    tender_token = self.initial_data["tender_token"]

    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={tender_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}", {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {
            "value": {**self.contract["value"], "amountNet": self.contract["value"]["amount"] - 1}}
        },
    )
    # active > terminated allowed
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}", {"data": {"status": "terminated"}}, status=403
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
        f"/contracts/{self.contract['id']}?acc_token={token}",
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
        f"/contracts/{self.contract['id']}?acc_token={token}", {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")


def contract_administrator_change(self):
    supplier = self.contract["suppliers"][0]
    buyer = self.contract["buyer"]
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}",
        {
            "data": {
                "mode": "test",
                "suppliers": [{
                    **supplier,
                    "contactPoint": {**supplier["contactPoint"], "email": "fff@gmail.com"},
                    "address": {**supplier["address"], "postalCode": "79014"}
                }],
                "buyer": {
                    **buyer,
                    "identifier": {**buyer["identifier"], "id": "11111111"},
                    "contactPoint": {**buyer["contactPoint"], "telephone": "+102"}},
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["mode"], "test")
    self.assertEqual(response.json["data"]["buyer"]["identifier"]["id"], "11111111")
    self.assertEqual(response.json["data"]["buyer"]["contactPoint"]["telephone"], "+102")
    self.assertEqual(response.json["data"]["suppliers"][0]["contactPoint"]["email"], "fff@gmail.com")
    self.assertEqual(
        response.json["data"]["suppliers"][0]["contactPoint"]["telephone"], "+380322916930"
    )  # old field value left untouchable
    self.assertEqual(response.json["data"]["suppliers"][0]["address"]["postalCode"], "79014")
    self.assertEqual(
        response.json["data"]["suppliers"][0]["address"]["countryName"], "Україна"
    )  # old field value left untouchable

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
    self.assertEqual(response.json["data"]["value"]["amount"], 238)
    self.assertEqual(response.json["data"]["id"], self.initial_data["id"])
    self.assertEqual(response.json["data"]["owner"], self.initial_data["owner"])
    self.assertEqual(response.json["data"]["contractID"], self.initial_data["contractID"])


def create_contract_w_documents(self):
    data = deepcopy(self.initial_data)
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
    tender_token = self.initial_data["tender_token"]

    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")
    self.assertNotIn("items", response.json["data"])

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={tender_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}/credentials?acc_token={tender_token}", {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    token = response.json["access"]["token"]

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"value": {**self.contract["value"], "amountNet": self.contract["value"]["amount"] - 1}}},
    )

    # active > terminated allowed
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}", {"data": {"status": "terminated"}}, status=403
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
        f"/contracts/{self.contract['id']}?acc_token={token}",
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
        f"/contracts/{self.contract['id']}?acc_token={token}", {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")


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
        [{
            "location": "body",
            "name": "data",
            "description": "signerInfo field for buyer and suppliers is required for contract in `active` status"
        }]
    )


def patch_tender_contract(self):
    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}", {"data": {"title": "New Title"}}, status=403
    )
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
        {"data": {"value": {**self.contract["value"], "amountNet": self.contract["value"]["amount"] - 1}}},
    )

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}", {"data": {"title": "New Title"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["title"], "New Title")

    response = self.app.patch_json(
        f"/contracts/{self.contract['id']}?acc_token={token}",
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
        f"/contracts/{self.contract['id']}?acc_token={token}",
        {"data": {"period": {"startDate": custom_period_start_date, "endDate": custom_period_end_date}}},
    )
    self.assertEqual(response.status, "200 OK")

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
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}]
    )

    response = self.app.get(f"/contracts/{self.contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "terminated")
    self.assertEqual(response.json["data"]["value"]["amount"], 238)
    self.assertEqual(response.json["data"]["period"]["startDate"], custom_period_start_date)
    self.assertEqual(response.json["data"]["period"]["endDate"], custom_period_end_date)
    self.assertEqual(response.json["data"]["amountPaid"]["amount"], 90)
    self.assertEqual(response.json["data"]["amountPaid"]["amountNet"], 80)
    self.assertEqual(response.json["data"]["terminationDetails"], "sink")
