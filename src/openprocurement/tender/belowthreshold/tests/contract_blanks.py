# -*- coding: utf-8 -*-
import jmespath
from datetime import timedelta
from copy import deepcopy
from openprocurement.api.utils import get_now
from unittest.mock import patch
from openprocurement.tender.belowthreshold.tests.base import test_claim, test_cancellation
from openprocurement.tender.belowthreshold.utils import prepare_tender_item_for_contract
from openprocurement.tender.core.tests.cancellation import activate_cancellation_after_2020_04_19

# TenderContractResourceTest
from openprocurement.api.constants import RELEASE_2020_04_19

def create_tender_contract_invalid(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/some_id/contracts",
        {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    request_path = "/tenders/{}/contracts".format(self.tender_id)

    response = self.app.post(request_path, "data", status=415)
    self.assertEqual(response.status, "415 Unsupported Media Type")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Content-Type header should be one of ['application/json']",
                "location": "header",
                "name": "Content-Type",
            }
        ],
    )

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

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Rogue field", "location": "body", "name": "invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"awardID": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{"description": ["awardID should be one of awards"], "location": "body", "name": "awardID"}],
    )


def create_tender_contract(self):
    self.app.authorization = ("Basic", ("token", ""))
    tender = self.db.get(self.tender_id)
    contract_items = [prepare_tender_item_for_contract(i) for i in deepcopy(tender["items"])]
    for item in contract_items:
        item["quantity"] += 0.5

    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {
            "data": {
                "title": "contract title",
                "description": "contract description",
                "awardID": self.award_id,
                "value": {
                    "amount": self.award_value["amount"],
                    "valueAddedTaxIncluded": self.award_value["valueAddedTaxIncluded"],
                    "currency": self.award_value["currency"],
                    "amountNet": self.award_value["amount"],
                },
                "suppliers": self.award_suppliers,
                "items": contract_items,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]
    self.assertIn("id", contract)
    self.assertIn("value", contract)
    self.assertIn("suppliers", contract)
    self.assertIn(contract["id"], response.headers["Location"])
    self.assertEqual(contract["items"], contract_items)

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "terminated"
    self.db.save(tender)

    self.set_status("unsuccessful")

    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add contract in current (unsuccessful) tender status"
    )

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (unsuccessful) tender status"
    )


def patch_tender_multi_contracts(self):
    contracts_response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contracts = contracts_response.json["data"]
    # 1st contract contains 1 item, 2nd contract contains 2 items
    self.assertEqual(len(contracts), 2)
    self.assertEqual(len(contracts[0]["items"]), 1)
    self.assertEqual(len(contracts[1]["items"]), 2)

    self.assertEqual(contracts[0]["value"]["amount"], 0)
    self.assertEqual(contracts[1]["value"]["amount"], 0)

    self.assertEqual(contracts[0]["value"]["valueAddedTaxIncluded"], True)
    self.assertEqual(contracts[1]["value"]["valueAddedTaxIncluded"], True)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contracts[0]["id"], self.tender_token),
        {"data": {"value": {"amount": 200}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    self.assertEqual(
        response.json["errors"], [
            {
                'location': 'body',
                'name': 'value',
                'description': 'Amount should be greater than amountNet and differ by no more than 20.0%'
             }
        ]
    )
    # patch 1st contract
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contracts[0]["id"], self.tender_token),
        {"data": {"value": {"amount": 200, "amountNet": 195}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 200)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 195)

    # patch 2nd contract
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contracts[1]["id"], self.tender_token),
        {"data": {"value": {"amount": 400, "amountNet": 390}}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    self.assertEqual(
        response.json["errors"], [
            {
                'location': 'body',
                'name': 'value',
                'description': 'Amount should be less or equal to awarded amount'
            }
        ]
    )

    # 1st contract.value + 2nd contract.value <= award.amount.value
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contracts[1]["id"], self.tender_token),
        {"data": {"value": {"amount": 190, "amountNet": 185}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 190)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 185)

    # prepare contract for activating
    doc = self.db.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.db.save(doc)

    # in case any contract become active and there are no pending contracts -> tender should have complete status
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contracts[0]["id"], self.tender_token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertNotEqual(response.json["data"]["status"], "complete")  # because second contract still in pending

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contracts[1]["id"], self.tender_token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "complete")


def patch_tender_multi_contracts_cancelled(self):
    contracts_response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contracts = contracts_response.json["data"]
    self.assertEqual(len(contracts), 2)

    # cancel 1st contract
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contracts[0]["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # try to cancel 2nd contract
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contracts[1]["id"], self.tender_token),
        {"data": {"status": "cancelled"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [
            {
                "location": "body",
                "name": "data",
                "description": (
                    "Can't update contract status from pending to cancelled for last not "
                    "cancelled contract. Cancel award instead."
                )
            }
        ]
    )

    # check 2nd contract not cancelled
    response = self.app.get(
        "/tenders/{}/contracts/{}".format(self.tender_id, contracts[1]["id"]),
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    # cancel award
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.tender_token
        ),
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    # check 2nd contract also cancelled
    response = self.app.get(
        "/tenders/{}/contracts/{}".format(self.tender_id, contracts[1]["id"]),
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")


def patch_tender_multi_contracts_active_cancelled(self):
    contracts_response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contracts = contracts_response.json["data"]
    self.assertEqual(len(contracts), 2)

    # patch 1st contract
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contracts[0]["id"], self.tender_token),
        {"data": {"value": {"amount": 200, "amountNet": 195}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 200)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 195)

    # prepare contract for activating
    doc = self.db.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.db.save(doc)

    # activate 1st contract
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contracts[0]["id"], self.tender_token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")

    # try to cancel award
    response = self.app.patch_json(
        "/tenders/{}/awards/{}?acc_token={}".format(
            self.tender_id, self.award_id, self.tender_token
        ),
        {"data": {"status": "cancelled"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [
            {
                "location": "body",
                "name": "data",
                "description": "Can\'t cancel award contract in active status"
            }
        ]
    )


def create_tender_contract_in_complete_status(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]
    self.assertIn("id", contract)
    self.assertIn(contract["id"], response.headers["Location"])

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "terminated"
    self.db.save(tender)

    self.set_status("complete")

    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't add contract in current (complete) tender status"
    )

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (complete) tender status"
    )


def patch_tender_contract(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    self.assertEqual(contract["value"]["amount"], contract["value"]["amountNet"])

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Can't sign contract before stand-still period end (", response.json["errors"][0]["description"])

    self.set_status("complete", {"status": "active.awarded"})

    token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
        {
            "data": test_claim
        },
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    tender = self.db.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.db.save(tender)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amountNet": contract["value"]["amount"] - 1}}},
    )
    self.assertEqual(response.status, "200 OK")

    self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {
            "data": {
                "contractID": "myselfID",
                "items": [{"description": "New Description"}],
                "suppliers": [{"name": "New Name"}],
            }
        },
    )

    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract["id"]))
    self.assertEqual(response.json["data"]["contractID"], contract["contractID"])
    self.assertEqual(response.json["data"]["items"], contract["items"])
    self.assertEqual(response.json["data"]["suppliers"], contract["suppliers"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"currency": "USD"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"dateSigned": i["complaintPeriod"]["endDate"]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    "Contract signature date should be after award complaint period end date ({})".format(
                        i["complaintPeriod"]["endDate"]
                    )
                ],
                "location": "body",
                "name": "dateSigned",
            }
        ],
    )

    one_hour_in_furure = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"dateSigned": one_hour_in_furure}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": ["Contract signature date can't be in the future"],
                "location": "body",
                "name": "dateSigned",
            }
        ],
    )

    custom_signature_date = get_now().isoformat()
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"dateSigned": custom_signature_date}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], self.tender_token
        ),
        {"data": {"status": "answered", "resolutionType": "resolved", "resolution": "resolution text " * 2}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "answered")
    self.assertEqual(response.json["data"]["resolutionType"], "resolved")
    self.assertEqual(response.json["data"]["resolution"], "resolution text " * 2)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't sign contract before reviewing all complaints")

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], owner_token
        ),
        {"data": {"satisfied": True, "status": "resolved"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "resolved")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 232}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"contractID": "myselfID"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"items": [{"description": "New Description"}]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"suppliers": [{"name": "New Name"}]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/some_id?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": {"status": "active"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}]
    )

    response = self.app.patch_json(
        "/tenders/some_id/contracts/some_id?acc_token={}".format(self.tender_token),
        {"data": {"status": "active"}},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["contractID"], contract["contractID"])
    self.assertEqual(response.json["data"]["items"], contract["items"])
    self.assertEqual(response.json["data"]["suppliers"], contract["suppliers"])
    self.assertEqual(response.json["data"]["dateSigned"], custom_signature_date)


def patch_tender_contract_rationale_simple(self):
    # make tender procurementMethodRationale simple
    doc = self.db.get(self.tender_id)
    doc["procurementMethodRationale"] = "simple"
    self.db.save(doc)

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    self.assertEqual(contract["value"]["amount"], contract["value"]["amountNet"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {
            "data": {
                "value": {
                    "amountNet": contract["value"]["amount"] - 1
                }
            }
        },
    )
    self.assertEqual(response.status, "200 OK")

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(
            self.tender_id,
            contract["id"],
            self.tender_token
        ),
        {
            "data": {
                "status": "active"
            }
        },
        status=200,
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get(
        "/tenders/{}".format(self.tender_id)
    )
    self.assertEqual(response.json["data"]["status"], "complete")


def patch_tender_contract_value(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 501}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount should be less or equal to awarded amount")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 502, "amountNet": 501}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount should be less or equal to awarded amount")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 238}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be greater than amountNet and differ by no more than 20.0%",
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 100, "amountNet": 80}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be greater than amountNet and differ by no more than 20.0%",
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 238, "amountNet": 238}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be greater than amountNet and differ by no more than 20.0%",
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 100, "amountNet": 85}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 100)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 85)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": False}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount and amountNet should be equal")


def patch_tender_contract_value_vat_not_included(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"currency": "USD"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 468}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount and amountNet should be equal")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 600, "amountNet": 600}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount should be less or equal to awarded amount")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"amount": 400, "amountNet": 400}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 400)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 400)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": {"valueAddedTaxIncluded": True}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be greater than amountNet and differ by no more than 20.0%",
    )


def patch_contract_single_item_unit_value(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    contract_id = contract["id"]
    self.assertEqual(len(contract["items"]), 1)
    expected_item_unit_currency = contract["items"][0]["unit"]["value"]["currency"]  # "UAH"
    expected_item_quantity = contract["items"][0]["quantity"]

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {
            "items": [
                {
                    "unit": {
                        "value": {
                            "amount": 2000,  # all Item fields except amount will be ignored by edit_contract role
                            "currency": "GBP",
                        },
                    },
                    "quantity": 100500
                }
            ]
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["amount"], 2000.0)
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["currency"], expected_item_unit_currency)
    self.assertEqual(response.json["data"]["items"][0]["quantity"], expected_item_quantity)

    # prepare contract
    doc = self.db.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.db.save(doc)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{
            "description": "Total amount of unit values can't be greater than contract.value.amount",
            "location": "body",
            "name": "data"
        }]
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {
            "items": [
                {
                    "unit": {
                        "value": {
                            "amount": 15
                        },
                    }
                }
            ]
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["amount"], 15.0)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active"}}, status=200
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {
            "items": [
                {
                    "unit": {
                        "value": {
                            "amount": 555555
                        },
                    }
                }
            ]
        }}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{
            "description": "Can't update contract in current (complete) tender status",
            "location": "body",
            "name": "data"
        }]
    )


def patch_contract_single_item_unit_value_with_status(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    contract_id = contract["id"]
    self.assertEqual(len(contract["items"]), 1)
    expected_item_unit_currency = contract["items"][0]["unit"]["value"]["currency"]  # "UAH"
    expected_item_quantity = contract["items"][0]["quantity"]

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {
            "items": [
                {
                    "unit": {
                        "value": {
                            "amount": 2000,  # all Item fields except amount will be ignored by edit_contract role
                            "currency": "GBP",
                        },
                    },
                    "quantity": 100500
                }
            ]
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["amount"], 2000.0)
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["currency"], expected_item_unit_currency)
    self.assertEqual(response.json["data"]["items"][0]["quantity"], expected_item_quantity)

    # prepare contract
    doc = self.db.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.db.save(doc)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{
            "description": "Total amount of unit values can't be greater than contract.value.amount",
            "location": "body",
            "name": "data"
        }]
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {
            "status": "active",
            "items": [
                {
                    "unit": {
                        "value": {
                            "amount": 15
                        },
                    }
                }
            ]
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["amount"], 15.0)
    self.assertEqual(response.json["data"]["status"], "active")


def patch_contract_single_item_unit_value_round(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    contract_id = contract["id"]
    self.assertEqual(len(contract["items"]), 1)
    quantity = contract["items"][0]["quantity"]

    # prepare contract
    doc = self.db.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.db.save(doc)

    unit_value_amount = doc['contracts'][0]['value']['amount'] / quantity + 0.001

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {
            "status": "active",
            "items": [
                {
                    "unit": {
                        "value": {
                            "amount": unit_value_amount
                        },
                    }
                }
            ]
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["amount"], unit_value_amount)
    self.assertEqual(response.json["data"]["status"], "active")


@patch("openprocurement.tender.core.validation.UNIT_PRICE_REQUIRED_FROM", get_now() - timedelta(days=1))
def patch_contract_multi_items_unit_value(self):

    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))

    contract_items = []
    for i in range(3):
        item = deepcopy(self.initial_data["items"][0])
        item['id'] = str(i+1)*10
        del item['unit']['value']
        contract_items.append(item)

    contract_items[0]['quantity'] = 10
    contract_items[0]['unit']['value'] = {
        "amount": 200,
        "currency": "UAH",
    }

    contract_items[1]['quantity'] = 8

    contract_items[2]['quantity'] = 0
    contract_items[2]['unit']['value'] = {
        "amount": 100,
        "currency": "UAH",
    }

    contract_items = [prepare_tender_item_for_contract(i) for i in contract_items]

    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {
            "data": {
                "title": "contract title",
                "description": "contract description",
                "awardID": self.award_id,
                "value": {
                    "amount": 300,
                    "valueAddedTaxIncluded": True,
                    "currency": 'UAH',
                    "amountNet": 285,
                },
                "suppliers": self.award_suppliers,
                "items": contract_items,
            }
        },
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]
    contract_id = contract['id']
    self.assertEqual(len(contract["items"]), 3)

    if self.initial_status != 'active.awarded':
        self.set_status("complete", {"status": "active.awarded"})

    # prepare contract
    doc = self.db.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if doc['contracts'][1]['value']['valueAddedTaxIncluded']:
        doc['contracts'][1]['value']['amountNet'] = str(float(doc['contracts'][1]['value']['amount']) - 1)
    self.db.save(doc)

    self.app.authorization = auth

    contracts_response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    self.assertEqual(contracts_response.status, "200 OK")
    contracts = contracts_response.json["data"]
    self.assertEqual(len(contracts), 2)
    total_contracts_amount = sum(
        [contract["value"]["amount"] for contract in contracts
         if contract["awardID"] == self.award_id]
    )

    if total_contracts_amount > self.award_value["amount"]:

        response = self.app.patch_json(
            "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
            {"data": {"status": "active"}}, status=403
        )
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{
                "description": "Amount should be less or equal to awarded amount",
                "location": "body",
                "name": "value"
            }]
        )

        response = self.app.patch_json(
            "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contracts[0]["id"], self.tender_token),
            {"data": {"value": {"amount": 100, "amountNet": 95}}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["value"]["amount"], 100)
        self.assertEqual(response.json["data"]["value"]["amountNet"], 95)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{
            "description": "Item.unit.value.amount should be updated to 0 if item.quantity equal to 0",
            "location": "body",
            "name": "data"
        }]
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {
            "items": [
                {}, {},
                {
                    "unit": {
                        "value": {
                            "amount": 0
                        },
                    }
                }
            ]
        }},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['items'][2]["unit"]["value"]["amount"], 0.0)
    self.assertEqual(response.json["data"]["status"], "pending")

    unit_value_amount_sum = sum([
        item['unit']['value']['amount'] * item['quantity']
        for item in response.json['data']['items'] if item['unit'].get('value')
    ])
    self.assertEqual(unit_value_amount_sum, 2000)  # 10 * 200 for first item

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"], [{
            "description": "Total amount of unit values can't be greater than contract.value.amount",
            "location": "body",
            "name": "data"
        }]
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {
            "items": [
                {
                    "unit": {
                        "value": {
                            "amount": 7.56345
                        },
                    }
                },
                {}, {}
            ]
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['items'][0]["unit"]["value"]["amount"], 7.56345)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active"}},
        status=403
    )
    self.assertEqual(
        response.json["errors"], [{
            "description": "Can't activate contract while unit.value is not set for each item",
            "location": "body",
            "name": "data"
        }]
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {
            "items": [
                {},
                {
                    "unit": {
                        "value": {
                            "amount": 10
                        },
                    }
                },
                {}
            ]
        }},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['items'][1]["unit"]["value"]["amount"], 10.0)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")


def patch_tender_contract_status_by_owner(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    contract_id = contract["id"]
    self.set_status("complete", {"status": "active.awarded"})

    # prepare contract
    doc = self.db.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.db.save(doc)

    # Tender onwer
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")


def patch_tender_contract_status_by_supplier(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    contract_id = contract["id"]
    self.set_status("complete", {"status": "active.awarded"})

    doc = self.db.get(self.tender_id)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id=='{}'].owner_token".format(bid_id), doc)[0]

    for bid in doc.get("bids", []):
        if bid["id"] == bid_id and bid["status"] == "pending":
            bid["status"] = "active"
    for i in doc.get("awards", []):
        if "complaintPeriod" in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if doc["contracts"][0]["value"]["valueAddedTaxIncluded"]:
        doc["contracts"][0]["value"]["amountNet"] = str(float(doc["contracts"][0]["value"]["amount"]) - 1)
    self.db.save(doc)

    # Supplier
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"status": "pending.winner-signing"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{'description': 'Supplier can change status to `pending`', 'location': 'body', 'name': 'data'}]
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"value": {"amount": 10000}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{'description': 'Supplier can change status to `pending`', 'location': 'body', 'name': 'data'}]
    )

    # Tender onwer
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")


    # Supplier
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"status": "active"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{'description': 'Supplier can change status to `pending`', 'location': 'body', 'name': 'data'}]
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"value": {"amount": 10000}, "status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotEqual(response.json["data"]["value"]["amount"], "10000")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract_id))
    self.assertNotEqual(response.json["data"]["value"]["amount"], "10000")

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")


def patch_tender_contract_status_by_others(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    contract_id = contract["id"]
    self.set_status("complete", {"status": "active.awarded"})

    doc = self.db.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if 'value' in doc['contracts'][0] and doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.db.save(doc)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id!='{}'].owner_token".format(bid_id), doc)[0]

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"status": "pending.winner-signing"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"status": "pending"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])


def get_tender_contract(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"], contract)

    response = self.app.get("/tenders/{}/contracts/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}]
    )

    response = self.app.get("/tenders/some_id/contracts/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


def get_tender_contracts(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"][-1], contract)

    response = self.app.get("/tenders/some_id/contracts", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )


# Tender2LotContractResourceTest


def lot2_patch_tender_contract(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))

    response = self.app.post_json(
        "/tenders/{}/contracts".format(self.tender_id),
        {"data": {"title": "contract title", "description": "contract description", "awardID": self.award_id}},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    contract = response.json["data"]
    self.app.authorization = auth

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Can't sign contract before stand-still period end (", response.json["errors"][0]["description"])

    self.set_status("complete", {"status": "active.awarded"})

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update contract only in active lot status")


def lot2_patch_tender_contract_rationale_simple(self):
    # make tender procurementMethodRationale simple
    doc = self.db.get(self.tender_id)
    doc["procurementMethodRationale"] = "simple"
    self.db.save(doc)

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {
            "data": {
                "status": "active"
            }
        },
        status=200,
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    # check if lot complete after contract activated
    response = self.app.get(
        "/tenders/{}".format(self.tender_id)
    )
    tender = response.json["data"]
    active_award = [award for award in tender["awards"] if award["id"] == self.award_id][0]
    completed_lot = [lot for lot in tender["lots"] if lot["id"] == active_award["lotID"]][0]
    self.assertEqual(completed_lot["status"], "complete")


# TenderContractDocumentResourceTest


def not_found(self):
    response = self.app.post(
        "/tenders/some_id/contracts/some_id/documents?acc_token={}".format(self.tender_token),
        status=404,
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.post(
        "/tenders/{}/contracts/some_id/documents?acc_token={}".format(self.tender_id, self.tender_token),
        status=404,
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}]
    )

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        status=404,
        upload_files=[("invalid_value", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "body", "name": "file"}])

    response = self.app.get("/tenders/some_id/contracts/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.get("/tenders/{}/contracts/some_id/documents".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}]
    )

    response = self.app.get("/tenders/some_id/contracts/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.get("/tenders/{}/contracts/some_id/documents/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}]
    )

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/some_id".format(self.tender_id, self.contract_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
    )

    response = self.app.put(
        "/tenders/some_id/contracts/some_id/documents/some_id?acc_token={}".format(self.tender_token),
        status=404,
        upload_files=[("file", "name.doc", b"content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}]
    )

    response = self.app.put(
        "/tenders/{}/contracts/some_id/documents/some_id?acc_token={}".format(self.tender_id, self.tender_token),
        status=404,
        upload_files=[("file", "name.doc", b"content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}]
    )

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/some_id?acc_token={}".format(
            self.tender_id, self.contract_id, self.tender_token
        ),
        status=404,
        upload_files=[("file", "name.doc", b"content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}]
    )


def create_tender_contract_document(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    self.assertEqual(response.json["data"]["status"], "pending")

    doc = self.db.get(self.tender_id)
    for i in doc.get("awards", []):
        if "complaintPeriod" in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if 'value' in doc["contracts"][0] and doc["contracts"][0]["value"]["valueAddedTaxIncluded"]:
        doc["contracts"][0]["value"]["amountNet"] = str(float(doc["contracts"][0]["value"]["amount"]) - 1)
    self.db.save(doc)

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get("/tenders/{}/contracts/{}/documents".format(self.tender_id, self.contract_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get("/tenders/{}/contracts/{}/documents?all=true".format(self.tender_id, self.contract_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "contract.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{'description': "Tender onwer can't add document in current contract status",
                       'location': 'body',
                       'name': 'data'}])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")


    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?download=some_id".format(self.tender_id, self.contract_id, doc_id),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}]
    )

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, b"content")

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add document in current contract status")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add document in current ({}) tender status".format(
            self.forbidden_contract_document_modification_actions_status
        ),
    )


def create_tender_contract_document_by_supplier(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    contract = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "pending")
    doc = self.db.get(self.tender_id)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id=='{}'].owner_token".format(bid_id), doc)[0]

    for bid in doc.get("bids", []):
        if bid["id"] == bid_id and bid["status"] == "pending":
            bid["status"] = "active"
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if 'value' in doc['contracts'][0] and doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.db.save(doc)

    # Supplier
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{'description': "Supplier can't add document in current contract status",
                       'location': 'body',
                       'name': 'data'}])

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Supplier
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get("/tenders/{}/contracts/{}/documents".format(self.tender_id, self.contract_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get("/tenders/{}/contracts/{}/documents?all=true".format(self.tender_id, self.contract_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][0]["id"])
    self.assertEqual("name.doc", response.json["data"][0]["title"])

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?download=some_id".format(self.tender_id, self.contract_id, doc_id),
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}]
    )

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 7)
    self.assertEqual(response.body, b"content")

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Supplier can't add document in current contract status")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Supplier can't add document in current contract status")


def create_tender_contract_document_by_others(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    contract = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "pending")

    doc = self.db.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if 'value' in doc['contracts'][0] and doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.db.save(doc)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id!='{}'].owner_token".format(bid_id), doc)[0]

    # Bid owner
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Bid onwer
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{"location": "url", "name": "permission", "description": "Forbidden"}])

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")


def put_tender_contract_document(self):
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        status=404,
        upload_files=[("invalid_name", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "body", "name": "file"}])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", b"content2")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Tender onwer can't update document in current contract status")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", b"content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, b"content2")

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        "content3",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, b"content3")

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", b"content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update document in current contract status")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", b"content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document in current ({}) tender status".format(
            self.forbidden_contract_document_modification_actions_status
        ),
    )


def put_tender_contract_document_by_supplier(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    contract = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "pending")
    doc = self.db.get(self.tender_id)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id=='{}'].owner_token".format(bid_id), doc)[0]

    for bid in doc.get("bids", []):
        if bid["id"] == bid_id and bid["status"] == "pending":
            bid["status"] = "active"
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if 'value' in doc['contracts'][0] and doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.db.save(doc)

    # Supplier
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Supplier can't add document in current contract status")

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Supplier
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        status=404,
        upload_files=[("invalid_name", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "body", "name": "file"}])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        upload_files=[("file", "name.doc", b"content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, b"content2")

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        b"content3",
        content_type="application/msword",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/msword")
    self.assertEqual(response.content_length, 8)
    self.assertEqual(response.body, b"content3")

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        upload_files=[("file", "name.doc", b"content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Supplier can't update document in current contract status")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        upload_files=[("file", "name.doc", b"content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Supplier can't update document in current contract status")


def put_tender_contract_document_by_others(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    contract = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "pending")
    doc = self.db.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if 'value' in doc['contracts'][0] and doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.db.save(doc)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id!='{}'].owner_token".format(bid_id), doc)[0]

    # Bid onwer
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Bid owner
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])


def patch_tender_contract_document(self):
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Tender onwer can't update document in current contract status")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update document in current contract status")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document in current ({}) tender status".format(
            self.forbidden_contract_document_modification_actions_status
        ),
    )


def patch_tender_contract_document_by_supplier(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    contract = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "pending")
    doc = self.db.get(self.tender_id)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id=='{}'].owner_token".format(bid_id), doc)[0]

    for bid in doc.get("bids", []):
        if bid["id"] == bid_id and bid["status"] == "pending":
            bid["status"] = "active"
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if 'value' in doc['contracts'][0] and doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.db.save(doc)

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Supplier can't add document in current contract status")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("document description", response.json["data"]["description"])

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update document in current contract status")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update document in current ({}) tender status".format(
            self.forbidden_contract_document_modification_actions_status
        ),
    )


# Tender2LotContractDocumentResourceTest


def lot2_create_tender_contract_document(self):
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Tender onwer can't add document in current contract status")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = response.json["data"]["url"].split("?")[-1]

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token), {"data": cancellation},
    )

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, response.json['data']['id'])

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add document only in active lot status")


def lot2_create_tender_contract_document_by_supplier(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    contract = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "pending")
    doc = self.db.get(self.tender_id)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id=='{}'].owner_token".format(bid_id), doc)[0]

    # Supplier
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Supplier can't add document in current contract status")

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Supplier
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = response.json["data"]["url"].split("?")[-1]

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, response.json['data']['id'])

    # Supplier
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can add document only in active lot status")


def lot2_create_tender_contract_document_by_others(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    contract = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "pending")
    doc = self.db.get(self.tender_id)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id!='{}'].owner_token".format(bid_id), doc)[0]

    # Bid owner
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Bid owner
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])


def lot2_put_tender_contract_document(self):
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        status=404,
        upload_files=[("invalid_name", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "body", "name": "file"}])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", b"content2")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Tender onwer can't update document in current contract status")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", b"content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, response.json['data']['id'])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", b"content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only in active lot status")


def lot2_put_tender_contract_document_by_supplier(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    contract = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "pending")
    doc = self.db.get(self.tender_id)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id=='{}'].owner_token".format(bid_id), doc)[0]

    # Supplier
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Supplier can't add document in current contract status")

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Supplier
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        status=404,
        upload_files=[("invalid_name", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "body", "name": "file"}])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        upload_files=[("file", "name.doc", b"content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    # Tender owner
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, response.json['data']['id'])

    # Supplier
    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        upload_files=[("file", "name.doc", b"content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only in active lot status")


def lot2_patch_tender_contract_document(self):
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Tender onwer can't update document in current contract status")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })
    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token),
        {"data": cancellation},
    )

    if RELEASE_2020_04_19 < get_now():
        activate_cancellation_after_2020_04_19(self, response.json['data']['id'])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"description": "new document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only in active lot status")


def lot2_patch_tender_contract_document_by_supplier(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    contract = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "pending")
    doc = self.db.get(self.tender_id)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id=='{}'].owner_token".format(bid_id), doc)[0]

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Supplier
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        {"data": {"description": "document description"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    # Supplier
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        {"data": {"description": "document description"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Supplier can't update document in current contract status")

    # Tender owner
    cancellation = dict(**test_cancellation)
    cancellation.update({
        "status": "active",
        "cancellationOf": "lot",
        "relatedLot": self.initial_lots[0]["id"],
    })

    response = self.app.post_json(
        "/tenders/{}/cancellations?acc_token={}".format(self.tender_id, self.tender_token), {"data": cancellation},
    )

    # Supplier
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        {"data": {"description": "new document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Supplier can't update document in current contract status")
