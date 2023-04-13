# -*- coding: utf-8 -*-
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import get_now, to_decimal
from openprocurement.tender.core.tests.utils import change_auth
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_draft_complaint
from datetime import timedelta
from copy import deepcopy


# TenderContractResourceTest


def patch_tender_contract(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    self.assertEqual(
        to_decimal(contract["value"]["amountNet"]),
        self.expected_contract_amount
    )
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
        status=422
    )
    self.assertEqual(
        response.json["errors"][0],
        {"location": "body", "name": "suppliers", "description": "Rogue field"}
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
                "/tenders/{}/awards/{}/complaints/{}".format(
                    self.tender_id, self.award_id, complaint["id"]
                ),
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
            {"data": {
                "status": "invalid",
                "rejectReason": "buyerViolationsCorrected"
            }},
        )
        self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
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
    self.assertEqual(
        response.json["errors"], [{"description": "Not Found", "location": "url", "name": "contract_id"}]
    )

    response = self.app.patch_json("/tenders/some_id/contracts/some_id", {"data": {"status": "active"}}, status=404)
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
    self.assertEqual(
        to_decimal(response.json["data"]["value"]["amountPerformance"]),
        self.expected_contract_amountPerformance
    )
    self.assertEqual(
        to_decimal(response.json["data"]["value"]["amount"]),
        self.expected_contract_amount
    )
    self.assertNotEqual(
        response.json["data"]["value"]["amountNet"],
        response.json["data"]["value"]["amount"]
    )
    self.assertEqual(
        to_decimal(response.json["data"]["value"]["amountNet"]),
        self.expected_contract_amount - 1
    )
