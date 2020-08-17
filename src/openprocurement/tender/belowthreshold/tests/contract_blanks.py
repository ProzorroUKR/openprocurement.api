# -*- coding: utf-8 -*-
import jmespath
from datetime import timedelta
from copy import deepcopy
from openprocurement.api.utils import get_now

from openprocurement.tender.belowthreshold.tests.base import test_claim, test_cancellation, test_tender_data, test_organization, test_tender_full_document_data
from openprocurement.tender.core.tests.base import change_auth
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
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
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

    response = self.app.post_json(request_path, {"data": {"invalid_field": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Rogue field", u"location": u"body", u"name": u"invalid_field"}]
    )

    response = self.app.post_json(request_path, {"data": {"awardID": "invalid_value"}}, status=422)
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [{u"description": [u"awardID should be one of awards"], u"location": u"body", u"name": u"awardID"}],
    )


def create_tender_contract(self):
    self.app.authorization = ("Basic", ("token", ""))
    contract_items = deepcopy(self.award_items)
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

    token = self.initial_bids_tokens.values()[0]
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
                u"description": [
                    u"Contract signature date should be after award complaint period end date ({})".format(
                        i["complaintPeriod"]["endDate"]
                    )
                ],
                u"location": u"body",
                u"name": u"dateSigned",
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
                u"description": [u"Contract signature date can't be in the future"],
                u"location": u"body",
                u"name": u"dateSigned",
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
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
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
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
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


def patch_tender_contract_status_by_owner(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    contract_id = contract["id"]
    self.set_status("active.awarded")

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
    self.assertEqual(response.json["data"]["status"], u"active")


def patch_tender_contract_status_by_supplier(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    contract_id = contract["id"]
    self.set_status("active.awarded")

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
        [{u'description': u'Supplier can change status to `pending`', u'location': u'body', u'name': u'data'}]
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"value": {"amount": 10000}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{u'description': u'Supplier can change status to `pending`', u'location': u'body', u'name': u'data'}]
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
        [{u'description': u'Supplier can change status to `pending`', u'location': u'body', u'name': u'data'}]
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"value": {"amount": 10000}, "status": "pending"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertNotEqual(response.json["data"]["value"]["amount"], u"10000")
    self.assertEqual(response.json["data"]["status"], u"pending")

    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract_id))
    self.assertNotEqual(response.json["data"]["value"]["amount"], u"10000")

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "active"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], u"active")


def patch_tender_contract_status_by_others(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    contract_id = contract["id"]
    self.set_status("active.awarded")

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
                     [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}])

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
                     [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}])


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
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )

    response = self.app.get("/tenders/some_id/contracts/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
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
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
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

    self.set_status("complete", extra={"status": "active.awarded"})

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
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.post(
        "/tenders/{}/contracts/some_id/documents?acc_token={}".format(self.tender_id, self.tender_token),
        status=404,
        upload_files=[("file", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        status=404,
        upload_files=[("invalid_value", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])

    response = self.app.get("/tenders/some_id/contracts/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )
    response = self.app.get("/tenders/{}/contracts/some_id/documents".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )

    response = self.app.get("/tenders/some_id/contracts/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.get("/tenders/{}/contracts/some_id/documents/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/some_id".format(self.tender_id, self.contract_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
    )

    response = self.app.put(
        "/tenders/some_id/contracts/some_id/documents/some_id?acc_token={}".format(self.tender_token),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"tender_id"}]
    )

    response = self.app.put(
        "/tenders/{}/contracts/some_id/documents/some_id?acc_token={}".format(self.tender_id, self.tender_token),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"contract_id"}]
    )

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/some_id?acc_token={}".format(
            self.tender_id, self.contract_id, self.tender_token
        ),
        status=404,
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"document_id"}]
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
        upload_files=[("file", "name.doc", "content")],
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
        upload_files=[("file", "contract.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Tender onwer can't add document in current contract status",
                       u'location': u'body',
                       u'name': u'data'}])

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
        response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
    )

    if self.docservice:
        response = self.app.get("/tenders/{}/contracts/{}/documents/{}?download={}".format(self.tender_id, self.contract_id, doc_id, key))
        self.assertEqual(response.status, "302 Moved Temporarily")
        self.assertIn("http://localhost/get/", response.location)
        self.assertIn("Signature=", response.location)
        self.assertIn("KeyID=", response.location)
        self.assertNotIn("Expires=", response.location)
    else:
        response = self.app.get(
            "/tenders/{}/contracts/{}/documents/{}?download=some_id".format(self.tender_id, self.contract_id, doc_id),
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
        )
        response = self.app.get("/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/pkcs7-signature")
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, "content")
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
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add document in current contract status")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", "content")],
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

    tender_document = deepcopy(test_tender_full_document_data)
    tender_document["url"] = self.generate_docservice_url()
    doc["documents"] = [tender_document]
    tender_document_id = doc["documents"][0]["id"]
    self.db.save(doc)

    #Tender owner
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "contract_first_document.doc", "content")],
        status=201,
    )
    contract_doc_id = response.json["data"]["id"]
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # Supplier
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't add document in current contract status",
                       u'location': u'body',
                       u'name': u'data'}])

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
        upload_files=[("file", "contract_first_document.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't add contract documents",
                       u'location': u'body',
                       u'name': u'data'}])
    # Supplier
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't add tender documents",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": tender_document_id,
            }
        },
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"relatedItem should be one of contract documents",
                       u'location': u'body',
                       u'name': u'data'}])

    # Supplier
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "document",
                "relatedItem": "0"*32,
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
                u"location": u"body",
                u"name": u"relatedItem",
                u"description": [

                    u'relatedItem should be one of documents'
                ]
            }
        ]
    )

    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can add only 'application/pkcs7-signature' document format files",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=201
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("supplier_first_document_sign.pkcs7", response.json["data"]["title"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]

    response = self.app.get("/tenders/{}/contracts/{}/documents".format(self.tender_id, self.contract_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][-1]["id"])
    self.assertEqual("supplier_first_document_sign.pkcs7", response.json["data"][-1]["title"])

    response = self.app.get("/tenders/{}/contracts/{}/documents?all=true".format(self.tender_id, self.contract_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"][-1]["id"])
    self.assertEqual("supplier_first_document_sign.pkcs7", response.json["data"][-1]["title"])

    if self.docservice:
        response = self.app.get("/tenders/{}/contracts/{}/documents/{}?download={}".format(self.tender_id, self.contract_id, doc_id, key))
        self.assertEqual(response.status, "302 Moved Temporarily")
        self.assertIn("http://localhost/get/", response.location)
        self.assertIn("Signature=", response.location)
        self.assertIn("KeyID=", response.location)
        self.assertNotIn("Expires=", response.location)
    else:
        response = self.app.get(
            "/tenders/{}/contracts/{}/documents/{}?download=some_id".format(self.tender_id, self.contract_id, doc_id),
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
        )
        response = self.app.get("/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/pkcs7-signature")
        self.assertEqual(response.content_length, 7)
        self.assertEqual(response.body, "content")

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("supplier_first_document_sign.pkcs7", response.json["data"]["title"])

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Supplier can't add document in current contract status")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", "content")],
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
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}])

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
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{"location": "url", "name": "permission", "description": "Forbidden"}])

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")


def put_tender_contract_document(self):
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", "content")],
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
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])

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
        upload_files=[("file", "name.doc", "content2")],
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
        upload_files=[("file", "name.doc", "content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]
   
    if self.docservice:
        response = self.app.get("/tenders/{}/contracts/{}/documents/{}?download={}".format(self.tender_id, self.contract_id, doc_id, key))
        self.assertEqual(response.status, "302 Moved Temporarily")
        self.assertIn("http://localhost/get/", response.location)
        self.assertIn("Signature=", response.location)
        self.assertIn("KeyID=", response.location)
        self.assertNotIn("Expires=", response.location)
    else:
        response = self.app.get(
            "/tenders/{}/contracts/{}/documents/{}?download=some_id".format(self.tender_id, self.contract_id, doc_id),
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
        )
        response = self.app.get("/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/pkcs7-signature")
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, "content2")

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
   
    if self.docservice:
        response = self.app.get("/tenders/{}/contracts/{}/documents/{}?download={}".format(self.tender_id, self.contract_id, doc_id, key))
        self.assertEqual(response.status, "302 Moved Temporarily")
        self.assertIn("http://localhost/get/", response.location)
        self.assertIn("Signature=", response.location)
        self.assertIn("KeyID=", response.location)
        self.assertNotIn("Expires=", response.location)
    else:
        response = self.app.get("/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/pkcs7-signature")
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, "content3")
        
    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "name.doc", "content3")],
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
        upload_files=[("file", "name.doc", "content3")],
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

    tender_document = deepcopy(test_tender_full_document_data)
    tender_document["url"] = self.generate_docservice_url()
    doc["documents"] = [tender_document]
    tender_document_id = doc["documents"][0]["id"]
    self.db.save(doc)

    #Tender owner
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "contract_first_document.doc", "content")],
        status=201,
    )
    contract_doc_id = response.json["data"]["id"]
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # Supplier
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
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
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=201
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    # Supplier
    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
        upload_files=[("file", "contract_first_document.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't update contract documents",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.put_json(
    "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't update tender documents",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
        {
            "data": {
                "title": u"supplier_first_document_sign_updated.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can update only 'application/pkcs7-signature' document format files",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
            {
            "data": {
                "title": u"supplier_first_document_sign_updated.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": "0"*32,
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
                u"location": u"body",
                u"name": u"relatedItem",
                u'description': [u'relatedItem should be one of documents']
            }
        ]
    )
    # Supplier
    response = self.app.put_json(
     "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": tender_document_id,
            }
        },
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"relatedItem should be one of contract documents",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
        {
            "data": {
                "title": u"supplier_first_document_sign_updated.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=200
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    if self.docservice:
        response = self.app.get("/tenders/{}/contracts/{}/documents/{}?download={}".format(self.tender_id, self.contract_id, doc_id, key))
        self.assertEqual(response.status, "302 Moved Temporarily")
        self.assertIn("http://localhost/get/", response.location)
        self.assertIn("Signature=", response.location)
        self.assertIn("KeyID=", response.location)
        self.assertNotIn("Expires=", response.location)
    else:
        response = self.app.get(
            "/tenders/{}/contracts/{}/documents/{}?download=some_id".format(self.tender_id, self.contract_id, doc_id),
            status=404,
        )
        self.assertEqual(response.status, "404 Not Found")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(
            response.json["errors"], [{u"description": u"Not Found", u"location": u"url", u"name": u"download"}]
        )
        response = self.app.get("/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/pkcs7-signature")
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, "content2")

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("supplier_first_document_sign_updated.pkcs7", response.json["data"]["title"])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        "content3",
        content_type="application/msword",
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can update only 'application/pkcs7-signature' document format files",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        "content3",
        content_type="application/pkcs7-signature",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = response.json["data"]["url"].split("?")[-1]

    if self.docservice:
        response = self.app.get("/tenders/{}/contracts/{}/documents/{}?download={}".format(self.tender_id, self.contract_id, doc_id, key))
        self.assertEqual(response.status, "302 Moved Temporarily")
        self.assertIn("http://localhost/get/", response.location)
        self.assertIn("Signature=", response.location)
        self.assertIn("KeyID=", response.location)
        self.assertNotIn("Expires=", response.location)
    else:
        response = self.app.get("/tenders/{}/contracts/{}/documents/{}?{}".format(self.tender_id, self.contract_id, doc_id))
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/pkcs7-signature")
        self.assertEqual(response.content_length, 8)
        self.assertEqual(response.body, "content3")

    tender = self.db.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.db.save(tender)

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        upload_files=[("file", "name.doc", "content3")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"],
                     "Supplier can't update document in current contract status")

    self.set_status(self.forbidden_document_modification_actions_status)

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign_updated1.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=403
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
        upload_files=[("file", "name.doc", "content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}])

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
        upload_files=[("file", "name.doc", "content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}])


def patch_tender_contract_document(self):
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", "content")],
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

    tender_document = deepcopy(test_tender_full_document_data)
    tender_document["url"] = self.generate_docservice_url()
    doc["documents"] = [tender_document]
    tender_document_id = doc["documents"][0]["id"]
    self.db.save(doc)

    #Tender owner
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "contract_first_document.doc", "content")],
        status=201,
    )
    contract_doc_id = response.json["data"]["id"]
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # Supplier
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't add document in current contract status",
                       u'location': u'body',
                       u'name': u'data'}])

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Supplier
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=201
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("supplier_first_document_sign.pkcs7", response.json["data"]["title"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]

    # Supplier
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        {"data": {"format": "application/msword"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can update only 'application/pkcs7-signature' document format files",
                       u'location': u'body',
                       u'name': u'data'}])

    # Supplier
    response = self.app.patch_json(
    "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "tender",
                "relatedItem": self.tender_id
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't update tender documents",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.patch_json(
     "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": tender_document_id,
            }
        },
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"relatedItem should be one of contract documents",
                       u'location': u'body',
                       u'name': u'data'}])
    # Supplier
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        {"data": {"relatedItem": "0"*32}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"location": u"body",
                u"name": u"relatedItem",
                u"description": [
                            u'relatedItem should be one of documents'
                        ]
            }
        ]
    )
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        {"data": {"description": "description"}},
        status=200
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("description", response.json["data"]["description"])

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


def create_contract_documents_by_render_bot(self):
    self.add_contract_proforma_document()
    with change_auth(self.app, ("Basic", ("rBot", ""))):

        contract_pdf_json = {
            "title": u"contract.pdf",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/pdf",
            "documentOf": "document",
            "documentType": "contract",
            "relatedItem": self.proforma_doc_id
        }
        response = self.app.post_json("/tenders/{}/contracts/{}/documents".format(self.tender_id, self.contract_id),
                                      {"data": contract_pdf_json})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["documentType"], contract_pdf_json["documentType"])
        self.assertEqual(response.json["data"]["relatedItem"], contract_pdf_json["relatedItem"])
        self.assertEqual(response.json["data"]["documentOf"], "document")
        contract_id = response.json["data"]["id"]

        contract_data_json = {
            "title": u"contractData.json",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/json",
            "documentOf": "document",
            "documentType": "contractData",
            "relatedItem": contract_id
        }

        response = self.app.post_json("/tenders/{}/contracts/{}/documents".format(self.tender_id, self.contract_id),
                                      {"data": contract_data_json})
        self.assertEqual(response.status, "201 Created")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["data"]["documentType"], contract_data_json["documentType"])
        self.assertEqual(response.json["data"]["relatedItem"], contract_data_json["relatedItem"])
        self.assertEqual(response.json["data"]["documentOf"], "document")


def create_contract_documents_by_render_bot_invalid(self):
    with change_auth(self.app, ("Basic", ("rBot", ""))):
        contract_data_json = {
            "title": u"contractData.json",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/json",
            "documentType": "contractData",
        }

        response = self.app.post_json("/tenders/{}/contracts/{}/documents".format(self.tender_id, self.contract_id),
                                      {"data": contract_data_json},
                                      status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"],
                         [{u'description': u'relatedItem should be one of tender contractProforma documents',
                           u'location': u'body',
                           u'name': u'data'}])

        contract_pdf_json = {
            "title": u"contract.pdf",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/pdf",
            "documentType": "contract",
        }
        response = self.app.post_json("/tenders/{}/contracts/{}/documents".format(self.tender_id, self.contract_id),
                                      {"data": contract_pdf_json},
                                      status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"],
                         [{u'description': u'relatedItem should be one of tender contractProforma documents',
                           u'location': u'body',
                           u'name': u'data'}])

        tender = self.db.get(self.tender_id)
        tender["contracts"][-1]["status"] = "cancelled"
        self.db.save(tender)

        self.add_contract_proforma_document()
        contract_data_json = {
            "title": u"contractData.json",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/json",
            "documentType": "contractData",
            "relatedItem": self.proforma_doc_id,
            "documentOf": "document"
        }

        response = self.app.post_json("/tenders/{}/contracts/{}/documents".format(self.tender_id, self.contract_id),
                                      {"data": contract_data_json},
                                      status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"],
                         [{u'description': u"Can't add document in current contract status",
                           u'location': u'body',
                           u'name': u'data'}])

        contract_pdf_json = {
            "title": u"contract.pdf",
            "url": self.generate_docservice_url(),
            "hash": "md5:" + "0" * 32,
            "format": "application/pdf",
            "documentType": "contract",
            "relatedItem": self.proforma_doc_id,
            "documentOf": "document"
        }
        response = self.app.post_json("/tenders/{}/contracts/{}/documents".format(self.tender_id, self.contract_id),
                                      {"data": contract_pdf_json},
                                      status=403)
        self.assertEqual(response.status, "403 Forbidden")
        self.assertEqual(response.content_type, "application/json")
        self.assertEqual(response.json["errors"],
                         [{u'description': u"Can't add document in current contract status",
                           u'location': u'body',
                           u'name': u'data'}])


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
        upload_files=[("file", "name.doc", "content")],
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
        upload_files=[("file", "name.doc", "content")],
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
        upload_files=[("file", "name.doc", "content")],
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

    tender_document = deepcopy(test_tender_full_document_data)
    tender_document["url"] = self.generate_docservice_url()
    doc["documents"] = [tender_document]
    tender_document_id = doc["documents"][0]["id"]
    self.db.save(doc)

    #Tender owner
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "contract_first_document.doc", "content")],
        status=201,
    )
    contract_doc_id = response.json["data"]["id"]
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # Supplier
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first1.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status = 403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't add document in current contract status",
                       u'location': u'body',
                       u'name': u'data'}])

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
        upload_files=[("file", "contract_first_document.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't add contract documents",
                       u'location': u'body',
                       u'name': u'data'}])

    # Supplier
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't add tender documents",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": tender_document_id,
            }
        },
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"relatedItem should be one of contract documents",
                       u'location': u'body',
                       u'name': u'data'}])

    # Supplier
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "document",
                "relatedItem": "0"*32,
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
                u"location": u"body",
                u"name": u"relatedItem",
                u"description": [

                    u'relatedItem should be one of documents'
                ]
            }
        ]
    )

    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can add only 'application/pkcs7-signature' document format files",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=201
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("supplier_first_document_sign.pkcs7", response.json["data"]["title"])
    key = response.json["data"]["url"].split("/")[-1].split("?")[0]

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
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=403
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
        upload_files=[("file", "name.doc", "content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}])

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
        upload_files=[("file", "name.doc", "content")],
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u'Forbidden', u'location': u'url', u'name': u'permission'}])


def lot2_put_tender_contract_document(self):
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", "content")],
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
        upload_files=[("invalid_name", "name.doc", "content")],
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{u"description": u"Not Found", u"location": u"body", u"name": u"file"}])

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
        upload_files=[("file", "name.doc", "content2")],
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
        upload_files=[("file", "name.doc", "content2")],
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
        upload_files=[("file", "name.doc", "content3")],
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

    tender_document = deepcopy(test_tender_full_document_data)
    tender_document["url"] = self.generate_docservice_url()
    doc["documents"] = [tender_document]
    tender_document_id = doc["documents"][0]["id"]
    self.db.save(doc)

    #Tender owner
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "contract_first_document.doc", "content")],
        status=201,
    )
    contract_doc_id = response.json["data"]["id"]
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    # Supplier
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
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
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=201
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    # Supplier
    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
        upload_files=[("file", "contract_first_document.doc", "content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't update contract documents",
                       u'location': u'body',
                       u'name': u'data'}])

    # Supplier
    response = self.app.put_json(
    "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't update tender documents",
                       u'location': u'body',
                       u'name': u'data'}])

    # Supplier
    response = self.app.put_json(
     "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": tender_document_id,
            }
        },
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"relatedItem should be one of contract documents",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
        {
            "data": {
                "title": u"supplier_first_document_sign_updated.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can update only 'application/pkcs7-signature' document format files",
                       u'location': u'body',
                       u'name': u'data'}])

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
            {
            "data": {
                "title": u"supplier_first_document_sign_updated.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": "0"*32,
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
                u"location": u"body",
                u"name": u"relatedItem",
                u"description": [u'relatedItem should be one of documents']
            }
        ]
    )

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
        {
            "data": {
                "title": u"supplier_first_document_sign_updated.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=200
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
        upload_files=[("file", "name.doc", "content3")],
        status=403,
    )
    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign_updated.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=403
    )

    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can update document only in active lot status")


def lot2_patch_tender_contract_document(self):
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "name.doc", "content")],
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
    for bid in doc.get("bids", []):
        if bid["id"] == bid_id and bid["status"] == "pending":
            bid["status"] = "active"
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if 'value' in doc['contracts'][0] and doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)

    tender_document = deepcopy(test_tender_full_document_data)
    tender_document["url"] = self.generate_docservice_url()
    doc["documents"] = [tender_document]
    tender_document_id = doc["documents"][0]["id"]
    self.db.save(doc)

    #Tender owner
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "contract_first_document.doc", "content")],
        status=201,
    )
    contract_doc_id = response.json["data"]["id"]
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # Supplier
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't add document in current contract status",
                       u'location': u'body',
                       u'name': u'data'}])

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Supplier
    response = self.app.post_json(
    "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": contract_doc_id,
            }
        },
        status=201
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    # Supplier
    response = self.app.patch_json(
    "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "tender",
                "relatedItem": self.tender_id
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't update tender documents",
                       u'location': u'body',
                       u'name': u'data'}])
    # Supplier
    response = self.app.patch_json(
     "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.pkcs7",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/pkcs7-signature",
                "documentOf": "document",
                "relatedItem": tender_document_id,
            }
        },
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"relatedItem should be one of contract documents",
                       u'location': u'body',
                       u'name': u'data'}])
    # Supplier
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        {"data": {"format": "application/msword"}},
        status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can update only 'application/pkcs7-signature' document format files",
                       u'location': u'body',
                       u'name': u'data'}])

    # Supplier
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        {"data": {"relatedItem": "0"*32}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"],
        [
            {
                u"location": u"body",
                u"name": u"relatedItem",
                u"description": [
                            u'relatedItem should be one of documents'
                        ]
            }
        ]
    )

    # Supplier
    response = self.app.patch_json(
    "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token),
    {
            "data": {
                "title": u"supplier_first_document_sign.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
                "documentOf": "tender",
                "relatedItem": self.tender_id
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"],
                     [{u'description': u"Supplier can't update tender documents",
                       u'location': u'body',
                       u'name': u'data'}])
    # Supplier
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        {"data": {"description": "document description"}},
        status=200
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


def create_contract_document_contract_data_by_owner(self):
    self.add_contract_proforma_document()
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "contractData.json", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"documentType": "contractData", "documentOf": "document", "relatedItem": self.proforma_doc_id}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(response.json["data"]["author"], "tender_owner")
    self.assertEqual(response.json["data"]["documentOf"], "document")
    self.assertEqual(response.json["data"]["relatedItem"], self.proforma_doc_id)


def create_contract_document_second_contract_data_by_owner_fail(self):
    self.add_contract_proforma_document()
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "contractData.json", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"documentType": "contractData", "documentOf": "document", "relatedItem": self.proforma_doc_id}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(response.json["data"]["author"], "tender_owner")
    self.assertEqual(response.json["data"]["documentOf"], "document")
    self.assertEqual(response.json["data"]["relatedItem"], self.proforma_doc_id)

    #second contractData
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "contractData.json", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"documentType": "contractData", "documentOf": "document", "relatedItem": self.proforma_doc_id}},
        status=422
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json['errors'],
        [{"location": "body",
          "name": "contracts",
          "description": [{"documents": ["Allow only one document with documentType 'contractData' per contract."]}]}]
    )


def put_contract_document_contract_data_by_owner(self):
    self.add_contract_proforma_document()
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "contractData.json", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"documentType": "contractData", "documentOf": "document", "relatedItem": self.proforma_doc_id}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(response.json["data"]["author"], "tender_owner")
    self.assertEqual(response.json["data"]["documentOf"], "document")
    self.assertEqual(response.json["data"]["relatedItem"], self.proforma_doc_id)

    response = self.app.put(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        upload_files=[("file", "new_contractData.json", "content2")],
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(response.json["data"]["author"], "tender_owner")
    self.assertEqual(response.json["data"]["documentOf"], "document")
    self.assertEqual(response.json["data"]["relatedItem"], self.proforma_doc_id)
    self.assertEqual(response.json["data"]["title"], "new_contractData.json")
    self.assertEqual(len(response.json["data"]["previousVersions"]), 1)


def put_contract_document_contract_data_by_rbot(self):
    self.add_contract_proforma_document()
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        upload_files=[("file", "contractData.json", "content")],
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"documentType": "contractData", "documentOf": "document", "relatedItem": self.proforma_doc_id}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(response.json["data"]["author"], "tender_owner")
    self.assertEqual(response.json["data"]["documentOf"], "document")
    self.assertEqual(response.json["data"]["relatedItem"], self.proforma_doc_id)


    with change_auth(self.app, ("Basic", ("rBot", ""))):
        response = self.app.put(
            "/tenders/{}/contracts/{}/documents/{}".format(
                self.tender_id, self.contract_id, doc_id
            ),
            upload_files=[("file", "bot_contractData.json", "content3")],
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual(response.json["data"]["author"], "renderer_bots")
    self.assertEqual(response.json["data"]["documentOf"], "document")
    self.assertEqual(response.json["data"]["relatedItem"], self.proforma_doc_id)
    self.assertEqual(response.json["data"]["title"], "bot_contractData.json")
    self.assertEqual(len(response.json["data"]["previousVersions"]), 1)
    self.assertEqual(response.json["data"]["previousVersions"][0]["author"], "tender_owner")
