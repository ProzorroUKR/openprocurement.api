from copy import deepcopy
from datetime import timedelta

from openprocurement.api.constants import RELEASE_2020_04_19, SANDBOX_MODE
from openprocurement.api.procedure.utils import parse_date
from openprocurement.api.utils import get_now
from openprocurement.tender.belowthreshold.tests.base import (
    test_tender_below_cancellation,
    test_tender_below_organization,
)
from openprocurement.tender.belowthreshold.tests.utils import set_tender_lots
from openprocurement.tender.core.tests.cancellation import (
    activate_cancellation_after_2020_04_19,
)
from openprocurement.tender.limited.tests.base import test_lots

# TenderContractResourceTes


def patch_tender_contract(self):
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract = response.json["data"]
    self.contract_id = contract["id"]

    tender = self.mongodb.tenders.get(self.tender_id)

    value = contract["value"]
    value["amountNet"] = value["amount"] - 1
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")

    old_currency = value["currency"]

    value["currency"] = "USD"
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
        {"data": {"value": value}},
        status=403,
    )
    value["currency"] = old_currency
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")

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
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertIn("dateSigned", response.json["data"])

    # at next steps we test to patch contract in 'cancelled' tender status
    response = self.app.post_json("/tenders?acc_token={}", {"data": self.initial_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender_id = response.json["data"]["id"]
    tender_token = response.json["access"]["token"]
    self.set_initial_status(response.json)

    response = self.app.post_json(
        f"/tenders/{tender_id}/awards?acc_token={tender_token}",
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
            }
        },
    )
    award_id = response.json["data"]["id"]
    self.app.patch_json(
        f"/tenders/{tender_id}/awards/{award_id}?acc_token={tender_token}",
        {"data": {"qualified": True, "status": "active"}},
    )

    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
        }
    )
    response = self.app.post_json(
        f"/tenders/{tender_id}/cancellations?acc_token={tender_token}",
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")

    cancellation_id = response.json["data"]["id"]

    if get_now() > RELEASE_2020_04_19:
        activate_cancellation_after_2020_04_19(self, cancellation_id, tender_id, tender_token)

    response = self.app.get(f"/tenders/{tender_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.get(f"/contracts/{self.contract_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get(f"/tenders/{self.tender_id}/contracts/{self.contract_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")


def tender_contract_signature_date(self):
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract = response.json["data"]
    self.contract_id = contract["id"]

    value = contract["value"]
    value["amountNet"] = value["amount"] - 1
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")

    one_hour_in_furure = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
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
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
        {"data": {"dateSigned": custom_signature_date}},
    )
    self.assertEqual(response.status, "200 OK")

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
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["dateSigned"], custom_signature_date)
    self.assertIn("dateSigned", response.json["data"])


def get_tender_contract(self):
    response = self.app.get(f"/tenders/{self.tender_id}/contracts")
    self.contract_id = response.json["data"][0]["id"]

    response = self.app.get(f"/tenders/{self.tender_id}/contracts/some_id", status=404)
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
    response = self.app.get(f"/tenders/{self.tender_id}/contracts")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    response = self.app.get("/tenders/some_id/contracts", status=404)
    self.assertEqual(response.status, "404 Not Found")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(response.json["errors"], [{"description": "Not Found", "location": "url", "name": "tender_id"}])


# TenderNegotiationContractResourceTes


def tender_negotiation_contract_signature_date(self):
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract = response.json["data"]
    self.assertNotIn("dateSigned", contract)
    self.contract_id = contract["id"]

    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    value = contract["value"]
    value["amountNet"] = value["amount"] - 1
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")

    one_hour_in_furure = (get_now() + timedelta(hours=1)).isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
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

    before_stand_still = i["complaintPeriod"]["startDate"]
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
        {"data": {"dateSigned": before_stand_still}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": [
                    f"Contract signature date should be after award complaint period end date ({i['complaintPeriod']['endDate']})"
                ],
                "location": "body",
                "name": "dateSigned",
            }
        ],
    )

    custom_signature_date = get_now().isoformat()
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
        {"data": {"dateSigned": custom_signature_date}},
    )
    self.assertEqual(response.status, "200 OK")

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
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["dateSigned"], custom_signature_date)
    self.assertIn("dateSigned", response.json["data"])


def activate_contract_cancelled_lot(self):
    response = self.app.get(f"/tenders/{self.tender_id}/lots")
    lot = response.json["data"][0]

    # Create cancellation on lot
    self.set_all_awards_complaint_period_end()
    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update(
        {
            "cancellationOf": "lot",
            "relatedLot": lot["id"],
        }
    )
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/cancellations?acc_token={self.tender_token}",
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    cancellation_id = response.json["data"]["id"]

    if RELEASE_2020_04_19 > get_now():
        self.assertEqual(response.json["data"]["status"], "pending")
    else:
        response = self.app.post_json(
            f"/tenders/{self.tender_id}/cancellations/{cancellation_id}/documents?acc_token={self.tender_token}",
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

        response = self.app.patch_json(
            f"/tenders/{self.tender_id}/cancellations/{cancellation_id}?acc_token={self.tender_token}",
            {"data": {"status": "pending"}},
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.json["data"]["status"], "pending")

    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract = response.json["data"]

    # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # reporting procedure does not have complaintPeriod
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    value = contract["value"]
    value["valueAddedTaxIncluded"] = False
    resp = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
        status=403,
    )
    self.assertEqual(
        resp.json["errors"],
        [{'location': 'body', 'name': 'data', 'description': "Can't perform action due to a pending cancellation"}],
    )

    # update value by admin
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("contracts", []):
        i["value"] = value
    self.mongodb.tenders.save(tender)

    # Try to sign (activate) contract
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't perform action due to a pending cancellation",
    )


# TenderNegotiationLot2ContractResourceTest


def sign_second_contract(self):
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract1 = response.json["data"]
    response = self.app.get(f"/contracts/{self.contracts_ids[1]}")
    contract2 = response.json["data"]
    self.contract1_id = contract1["id"]
    self.contract2_id = contract2["id"]

    # at next steps we test to create contract in 'complete' tender status
    # time travel
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        if i.get("complaintPeriod", {}):  # reporting procedure does not have complaintPeriod
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    value2 = contract1["value"]
    value2["amountNet"] = value2["amount"] - 1
    response = self.app.patch_json(
        f"/contracts/{self.contract2_id}?acc_token={self.tender_token}",
        {"data": {"value": value2}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract2_id}?acc_token={self.tender_token}",
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

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    value1 = contract1["value"]
    value1["amountNet"] = value1["amount"] - 1
    response = self.app.patch_json(
        f"/contracts/{self.contract1_id}?acc_token={self.tender_token}",
        {"data": {"value": value1}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract1_id}?acc_token={self.tender_token}",
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

    response = self.app.get("/tenders/{}".format(self.tender_id))
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "complete")


def patch_tender_negotiation_econtract(self):
    response = self.app.get(f"/tenders/{self.tender_id}/contracts")
    contract = response.json["data"][0]
    self.contract_id = contract["id"]

    test_signer_info = {
        "name": "Test Testovich",
        "telephone": "+380950000000",
        "email": "example@email.com",
        "iban": "1" * 15,
        "authorizedBy": "статут",
        "position": "Генеральний директор",
    }
    response = self.app.put_json(
        f"/contracts/{self.contract_id}/suppliers/signer_info?acc_token={self.tender_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put_json(
        f"/contracts/{self.contract_id}/buyer/signer_info?acc_token={self.tender_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Can't sign contract before stand-still period end (", response.json["errors"][0]["description"])

    response = self.app.get("/tenders/{}/awards".format(self.tender_id))
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(len(response.json["data"]), 1)
    award = response.json["data"][0]
    start = parse_date(award["complaintPeriod"]["startDate"])
    end = parse_date(award["complaintPeriod"]["endDate"])
    delta = end - start
    self.assertEqual(delta.days, 0 if SANDBOX_MODE else self.stand_still_period_days)

    # at next steps we test to patch contract in 'complete' tender status
    tender = self.mongodb.tenders.get(self.tender_id)
    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    value = contract["value"]
    old_currency = value["currency"]
    value["currency"] = "USD"
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
        {"data": {"value": value}},
        status=403,
    )
    value["currency"] = old_currency
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")

    value["amount"] = 238
    value["amountNet"] = 200
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={self.tender_token}",
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 238)

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
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertIn("dateSigned", response.json["data"])

    # at next steps we test to patch contract in 'cancelled' tender status
    tender_data = deepcopy(self.initial_data)
    set_tender_lots(tender_data, test_lots)
    lot_id = tender_data["lots"][0]["id"]
    response = self.app.post_json("/tenders?acc_token={}", {"data": tender_data, "config": self.initial_config})
    self.assertEqual(response.status, "201 Created")
    tender_id = self.tender_id = response.json["data"]["id"]
    tender_token = self.tender_token = response.json["access"]["token"]
    self.set_initial_status(response.json)

    response = self.app.post_json(
        f"/tenders/{tender_id}/awards?acc_token={tender_token}",
        {
            "data": {
                "suppliers": [test_tender_below_organization],
                "status": "pending",
                "lotID": lot_id,
                "value": {"amount": 40, "currency": "UAH", "valueAddedTaxIncluded": False},
            }
        },
    )
    award_id = response.json["data"]["id"]
    response = self.app.patch_json(
        f"/tenders/{tender_id}/awards/{award_id}?acc_token={tender_token}",
        {"data": {"qualified": True, "status": "active"}},
    )

    response = self.app.get(f"/tenders/{tender_id}/contracts")
    contract_id = response.json["data"][0]["id"]
    self.set_all_awards_complaint_period_end()

    cancellation = dict(**test_tender_below_cancellation)
    cancellation.update(
        {
            "status": "active",
        }
    )
    response = self.app.post_json(
        f"/tenders/{tender_id}/cancellations?acc_token={tender_token}",
        {"data": cancellation},
    )
    self.assertEqual(response.status, "201 Created")
    cancellation_id = response.json["data"]["id"]
    activate_cancellation_after_2020_04_19(self, cancellation_id)

    response = self.app.get(f"/tenders/{tender_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={tender_token}",
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update contract in current (cancelled) status")
