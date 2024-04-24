from copy import deepcopy
from datetime import timedelta

import jmespath

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.procedure.utils import to_decimal
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.procedure.utils import (
    prepare_tender_item_for_contract,
)
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_draft_complaint,
)
from openprocurement.tender.core.tests.utils import change_auth

# TenderContractResourceTest


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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

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
    tender = self.mongodb.tenders.get(self.tender_id)
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


def patch_tender_contract(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    self.assertEqual(to_decimal(contract["value"]["amountNet"]), self.expected_contract_amount)
    tender = self.mongodb.tenders.get(self.tender_id)

    old_tender_date_modified = tender["dateModified"]
    old_date = contract["date"]

    value = contract["value"]
    items = deepcopy(contract["items"])
    value["amountNet"] = value["amount"] - 1
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")

    tender = self.mongodb.tenders.get(self.tender_id)

    self.assertNotEqual(tender["dateModified"], old_tender_date_modified)
    self.assertEqual(response.json["data"]["date"], old_date)

    items[0]["description"] = "New Description"
    fake_suppliers_data = [{"name": "New Name"}]

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"items": items, "suppliers": fake_suppliers_data}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0], {"location": "body", "name": "suppliers", "description": "Rogue field"}
    )

    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract["id"]))
    self.assertNotEqual(items, response.json["data"]["items"])
    self.assertNotEqual(fake_suppliers_data, response.json["data"]["suppliers"])

    patch_fields = {
        "currency": "USD",
        "amountPerformance": 0,
        "yearlyPaymentsPercentage": 0,
        "annualCostsReduction": 0,
        "contractDuration": {"years": 9},
    }
    for field, field_value in patch_fields.items():
        new_value = dict(value)
        new_value[field] = field_value
        response = self.app.patch_json(
            "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
            {"data": {"value": new_value}},
            status=403,
        )
        new_value.pop(field)
        self.assertEqual(response.status_code, 403, field)
        self.assertEqual(response.json["errors"][0]["description"], "Can't update {} for contract value".format(field))

    value["amountNet"] = float(self.expected_contract_amount) + 1
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": value}},
        status=403,
    )
    self.assertEqual(response.status_code, 403)
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be equal or greater than amountNet and differ by no more than 20.0%",
    )

    value["amountNet"] = 10
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": value}},
        status=403,
    )
    self.assertEqual(response.status_code, 403)
    self.assertIn(
        "Amount should be equal or greater than amountNet and differ by no more than 20.0%",
        response.json["errors"][0]["description"],
    )

    value["amountNet"] = float(self.expected_contract_amount) - 1
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": value}},
    )
    self.assertEqual(response.status_code, 200)

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Can't sign contract before stand-still period end (", response.json["errors"][0]["description"])

    self.set_status("complete", {"status": "active.awarded"})

    token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

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

    one_hour_in_future = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"dateSigned": one_hour_in_future}},
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
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't sign contract before reviewing all complaints")

    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "invalid", "rejectReason": "buyerViolationsCorrected"}},
        )
        self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {
            "data": {
                "status": "active",
                "contractNumber": "123",
                "period": {
                    "startDate": "2023-03-18T18:47:47.155143+02:00",
                    "endDate": "2023-05-18T18:47:47.155143+02:00",
                },
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    new_value["annualCostsReduction"] = [780.5] * 21
    new_value["yearlyPaymentsPercentage"] = 0.9
    new_value["contractDuration"] = {"years": 10}
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {
            "data": {
                "value": value,
                "title": "New Title",
                "items": items,
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Can't update contract in current (complete) tender status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/some_id".format(self.tender_id), {"data": {"status": "active"}}, status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.patch_json("/tenders/some_id/contracts/some_id", {"data": {"status": "active"}}, status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract["id"]))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(
        to_decimal(response.json["data"]["value"]["amountPerformance"]), self.expected_contract_amountPerformance
    )
    self.assertEqual(to_decimal(response.json["data"]["value"]["amount"]), self.expected_contract_amount)
    self.assertNotEqual(response.json["data"]["value"]["amountNet"], response.json["data"]["value"]["amount"])
    self.assertEqual(to_decimal(response.json["data"]["value"]["amountNet"]), self.expected_contract_amount - 1)


def patch_econtract(self):
    contract_id = self.contracts_ids[0]
    response = self.app.get(f"/contracts/{contract_id}")
    contract = response.json["data"]

    self.assertEqual(to_decimal(contract["value"]["amountNet"]), self.expected_contract_amount)
    tender = self.mongodb.tenders.get(self.tender_id)

    # old_tender_date_modified = tender["dateModified"]
    # old_date = contract["date"]

    value = contract["value"]
    items = deepcopy(contract["items"])
    value["amountNet"] = value["amount"] - 1
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")

    items[0]["description"] = "New Description"
    fake_suppliers_data = [{"name": "New Name"}]

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"items": items, "suppliers": fake_suppliers_data}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0], {"location": "body", "name": "suppliers", "description": "Rogue field"}
    )

    response = self.app.get(f"/contracts/{contract_id}")
    self.assertNotEqual(items, response.json["data"]["items"])
    self.assertNotEqual(fake_suppliers_data, response.json["data"]["suppliers"])

    patch_fields = {
        "currency": "USD",
        "amountPerformance": 0,
        "yearlyPaymentsPercentage": 0,
        "annualCostsReduction": 0,
        "contractDuration": {"years": 9},
    }
    for field, field_value in patch_fields.items():
        new_value = dict(value)
        new_value[field] = field_value
        response = self.app.patch_json(
            f"/contracts/{contract_id}?acc_token={self.tender_token}",
            {"data": {"value": new_value}},
            status=403,
        )
        new_value.pop(field)
        self.assertEqual(response.status_code, 403, field)
        self.assertEqual(response.json["errors"][0]["description"], "Can't update {} for contract value".format(field))

    value["amountNet"] = float(self.expected_contract_amount) + 1
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"value": value}},
        status=403,
    )
    self.assertEqual(response.status_code, 403)
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be equal or greater than amountNet and differ by no more than 20.0%",
    )

    value["amountNet"] = 10
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"value": value}},
        status=403,
    )
    self.assertEqual(response.status_code, 403)
    self.assertIn(
        "Amount should be equal or greater than amountNet and differ by no more than 20.0%",
        response.json["errors"][0]["description"],
    )

    value["amountNet"] = float(self.expected_contract_amount) - 1
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"value": value}},
    )
    self.assertEqual(response.status_code, 200)

    # response = self.app.patch_json(
    #     f"/contracts/{contract['id']}?acc_token={self.tender_token}",
    #     {"data": {"status": "active"}},
    #     status=403,
    # )
    # self.assertEqual(response.status, "403 Forbidden")
    # self.assertEqual(response.content_type, "application/json")
    # self.assertIn("Can't sign contract before stand-still period end (", response.json["errors"][0]["description"])

    self.set_status("complete", {"status": "active.awarded"})

    token = self.initial_bids_tokens[self.initial_bids[0]["id"]]
    response = self.app.post_json(
        "/tenders/{}/awards/{}/complaints?acc_token={}".format(self.tender_id, self.award_id, token),
        {"data": test_tender_below_draft_complaint},
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    if get_now() < RELEASE_2020_04_19:
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "pending"}},
        )
    else:
        with change_auth(self.app, ("Basic", ("bot", ""))):
            response = self.app.patch_json(
                "/tenders/{}/awards/{}/complaints/{}".format(self.tender_id, self.award_id, complaint["id"]),
                {"data": {"status": "pending"}},
            )

    self.assertEqual(response.status, "200 OK")

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
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

    one_hour_in_future = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"dateSigned": one_hour_in_future}},
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
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"dateSigned": custom_signature_date}},
    )
    self.assertEqual(response.status, "200 OK")

    # response = self.app.patch_json(
    #     "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
    #     {"data": {"status": "active"}},
    #     status=403,
    # )
    # self.assertEqual(response.status, "403 Forbidden")
    # self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["errors"][0]["description"], "Can't sign contract before reviewing all complaints")

    with change_auth(self.app, ("Basic", ("reviewer", ""))):
        response = self.app.patch_json(
            "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
                self.tender_id, self.award_id, complaint["id"], owner_token
            ),
            {"data": {"status": "invalid", "rejectReason": "buyerViolationsCorrected"}},
        )
        self.assertEqual(response.status, "200 OK")

    # response = self.app.patch_json(
    #     "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
    #     {"data": {"status": "active"}},
    # )
    # self.assertEqual(response.status, "200 OK")
    # self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["data"]["status"], "active")

    # new_value["annualCostsReduction"] = [780.5] * 21
    # new_value["yearlyPaymentsPercentage"] = 0.9
    # new_value["contractDuration"] = {"years": 10}
    #
    # response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, contract["id"]))
    # self.assertEqual(response.status, "200 OK")
    # self.assertEqual(response.content_type, "application/json")
    # self.assertEqual(response.json["data"]["status"], "active")
    # self.assertEqual(
    #     to_decimal(response.json["data"]["value"]["amountPerformance"]),
    #     self.expected_contract_amountPerformance
    # )
    # self.assertEqual(
    #     to_decimal(response.json["data"]["value"]["amount"]),
    #     self.expected_contract_amount
    # )
    # self.assertNotEqual(
    #     response.json["data"]["value"]["amountNet"],
    #     response.json["data"]["value"]["amount"]
    # )
    # self.assertEqual(
    #     to_decimal(response.json["data"]["value"]["amountNet"]),
    #     self.expected_contract_amount - 1
    # )


def patch_tender_contract_status_by_owner(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    contract_id = contract["id"]
    self.set_status("complete", {"status": "active.awarded"})

    # prepare contract
    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.mongodb.tenders.save(doc)

    # Tender owner
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

    old_date = response.json["data"]["date"]

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
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

    doc = self.mongodb.tenders.get(self.tender_id)
    self.assertEqual(response.json["data"]["date"], doc["dateModified"])
    self.assertEqual(response.json["data"]["date"], response.json["data"]["dateSigned"])
    self.assertNotEqual(response.json["data"]["date"], old_date)


def patch_tender_contract_status_by_supplier(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    contract_id = contract["id"]
    self.set_status("complete", {"status": "active.awarded"})

    doc = self.mongodb.tenders.get(self.tender_id)
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
    self.mongodb.tenders.save(doc)

    # Supplier
    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"status": "pending.winner-signing"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{'description': 'Supplier can change status to `pending`', 'location': 'body', 'name': 'data'}],
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"value": {"amount": 10000}}},
        status=422,
    )
    self.assertEqual(response.json["errors"], [{"location": "body", "name": "value", "description": "Rogue field"}])

    # Tender owner
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
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{'description': 'Supplier can change status to `pending`', 'location': 'body', 'name': 'data'}],
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"value": {"amount": 10000}, "status": "pending"}},
        status=422,
    )
    self.assertEqual(response.json["errors"], [{"location": "body", "name": "value", "description": "Rogue field"}])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    old_date = response.json["data"]["date"]

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
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

    doc = self.mongodb.tenders.get(self.tender_id)
    self.assertEqual(response.json["data"]["date"], doc["dateModified"])
    self.assertEqual(response.json["data"]["date"], response.json["data"]["dateSigned"])
    self.assertNotEqual(response.json["data"]["date"], old_date)


def patch_tender_contract_status_by_others(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    contract_id = contract["id"]
    self.set_status("complete", {"status": "active.awarded"})

    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if 'value' in doc['contracts'][0] and doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.mongodb.tenders.save(doc)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id!='{}'].owner_token".format(bid_id), doc)[0]

    self.app.authorization = ("Basic", ("broker", ""))
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"status": "pending.winner-signing"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract_id, bid_token),
        {"data": {"status": "pending"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])


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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.get("/tenders/some_id/contracts/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


def create_tender_contract_document_by_supplier(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    contract = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "pending")
    doc = self.mongodb.tenders.get(self.tender_id)
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
    self.mongodb.tenders.save(doc)

    # Supplier
    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{'description': "Supplier can't add document in current contract status", 'location': 'body', 'name': 'data'}],
    )

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Supplier
    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
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
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}])

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?download={}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.mongodb.tenders.save(tender)

    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Supplier can't add document in current contract status"
    )

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Supplier can't add document in current contract status"
    )


def create_tender_contract_document_by_others(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    contract = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "pending")

    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if 'value' in doc['contracts'][0] and doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.mongodb.tenders.save(doc)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id!='{}'].owner_token".format(bid_id), doc)[0]

    # Bid owner
    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Bid owner
    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{"location": "url", "name": "permission", "description": "Forbidden"}])

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.mongodb.tenders.save(tender)

    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Forbidden")


def put_tender_contract_document(self):
    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
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

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Tender owner can't update document in current contract status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
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
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?download={}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
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
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?download={}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.mongodb.tenders.save(tender)

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update document in current contract status")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
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
    doc = self.mongodb.tenders.get(self.tender_id)
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
    self.mongodb.tenders.save(doc)

    # Supplier
    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Supplier can't add document in current contract status"
    )

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Supplier
    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
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

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
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
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?download={}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
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
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?download={}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.mongodb.tenders.save(tender)

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Supplier can't update document in current contract status"
    )

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, bid_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"], "Supplier can't update document in current contract status"
    )


def put_tender_contract_document_by_others(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    contract = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "pending")
    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if 'value' in doc['contracts'][0] and doc['contracts'][0]['value']['valueAddedTaxIncluded']:
        doc['contracts'][0]['value']['amountNet'] = str(float(doc['contracts'][0]['value']['amount']) - 1)
    self.mongodb.tenders.save(doc)
    bid_id = jmespath.search("awards[?id=='{}'].bid_id".format(contract["awardID"]), doc)[0]
    bid_token = jmespath.search("bids[?id!='{}'].owner_token".format(bid_id), doc)[0]

    # Bid owner
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])

    # Tender owner
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    # Bid owner
    response = self.app.post(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        upload_files=[("file", "name.doc", b"content")],
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{'description': 'Forbidden', 'location': 'url', 'name': 'permission'}])


def patch_tender_contract_document_by_supplier(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    contract = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "pending")
    doc = self.mongodb.tenders.get(self.tender_id)
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
    self.mongodb.tenders.save(doc)

    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Supplier can't add document in current contract status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, bid_token),
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

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.mongodb.tenders.save(tender)

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


def contract_termination(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]
    value = contract["value"]
    value["amountNet"] = value["amount"] - 1
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "terminated"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update contract status")


def create_tender_contract(self):
    auth = self.app.authorization
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

    self.app.authorization = auth
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


def not_found(self):
    response = self.app.post_json(
        "/tenders/some_id/contracts/some_id/documents?acc_token={}".format(self.tender_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.post_json(
        "/tenders/{}/contracts/some_id/documents?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.get("/tenders/some_id/contracts/some_id/documents", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.get("/tenders/{}/contracts/some_id/documents".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.get("/tenders/some_id/contracts/some_id/documents/some_id", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.get("/tenders/{}/contracts/some_id/documents/some_id".format(self.tender_id), status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/some_id".format(self.tender_id, self.contract_id), status=404
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}])

    response = self.app.put_json(
        "/tenders/some_id/contracts/some_id/documents/some_id?acc_token={}".format(self.tender_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])

    response = self.app.put(
        "/tenders/{}/contracts/some_id/documents/some_id?acc_token={}".format(self.tender_id, self.tender_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}])

    response = self.app.put_json(
        "/tenders/{}/contracts/{}/documents/some_id?acc_token={}".format(
            self.tender_id, self.contract_id, self.tender_token
        ),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "document_id"}])


def create_tender_contract_document(self):
    response = self.app.get("/tenders/{}/contracts/{}".format(self.tender_id, self.contract_id))
    self.assertEqual(response.json["data"]["status"], "pending")

    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if "complaintPeriod" in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    if 'value' in doc["contracts"][0] and doc["contracts"][0]["value"]["valueAddedTaxIncluded"]:
        doc["contracts"][0]["value"]["amountNet"] = str(float(doc["contracts"][0]["value"]["amount"]) - 1)
    self.mongodb.tenders.save(doc)

    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
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
    self.assertEqual("name.doc", response.json["data"]["title"])
    key = self.get_doc_id_from_url(response.json["data"]["url"])

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
        {"data": {"status": "pending.winner-signing"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {
            "data": {
                "title": "contract.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'description': "Tender owner can't add document in current contract status",
                'location': 'body',
                'name': 'data',
            }
        ],
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending"}},
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
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "download"}])

    response = self.app.get(
        "/tenders/{}/contracts/{}/documents/{}?download={}".format(self.tender_id, self.contract_id, doc_id, key)
    )
    self.assertEqual(response.status, "302 Moved Temporarily")
    self.assertIn("http://localhost/get/", response.location)
    self.assertIn("Signature=", response.location)
    self.assertIn("KeyID=", response.location)

    response = self.app.get("/tenders/{}/contracts/{}/documents/{}".format(self.tender_id, self.contract_id, doc_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(doc_id, response.json["data"]["id"])
    self.assertEqual("name.doc", response.json["data"]["title"])

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.mongodb.tenders.save(tender)

    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't add document in current contract status")

    self.set_status("{}".format(self.forbidden_contract_document_modification_actions_status))

    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {
            "data": {
                "title": "name.doc",
                "url": self.generate_docservice_url(),
                "hash": "md5:" + "0" * 32,
                "format": "application/msword",
            }
        },
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


def patch_tender_contract_document(self):
    response = self.app.post_json(
        "/tenders/{}/contracts/{}/documents?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
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

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending.winner-signing"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "pending.winner-signing")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}/documents/{}?acc_token={}".format(
            self.tender_id, self.contract_id, doc_id, self.tender_token
        ),
        {"data": {"description": "document description"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"], "Tender owner can't update document in current contract status"
    )

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, self.contract_id, self.tender_token),
        {"data": {"status": "pending"}},
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

    tender = self.mongodb.tenders.get(self.tender_id)
    tender["contracts"][-1]["status"] = "cancelled"
    self.mongodb.tenders.save(tender)

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


def patch_tender_contract_datesigned(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    self.set_status("complete", {"status": "active.awarded"})

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    value = contract["value"]
    value["amountNet"] = value["amount"] - 1
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
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
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertIn("dateSigned", response.json["data"].keys())
