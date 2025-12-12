from copy import deepcopy
from datetime import timedelta
from unittest import mock

from openprocurement.api.utils import get_now
from openprocurement.contracting.core.tests.data import test_signer_info
from openprocurement.tender.belowthreshold.tests.base import test_tender_below_claim
from openprocurement.tender.core.procedure.utils import prepare_tender_item_for_contract


def patch_tender_multi_contracts(self):
    contracts_response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contracts = contracts_response.json["data"]

    response = self.app.get(f"/contracts/{contracts[0]['id']}")
    contract_1 = response.json["data"]
    response = self.app.get(f"/contracts/{contracts[1]['id']}")
    contract_2 = response.json["data"]
    # 1st contract contains 1 item, 2nd contract contains 2 items
    self.assertEqual(len(contract_1["items"]), 1)
    self.assertEqual(len(contract_2["items"]), 2)

    self.assertEqual(contract_1["value"]["amount"], 0)
    self.assertEqual(contract_2["value"]["amount"], 0)

    self.assertEqual(contract_1["value"]["valueAddedTaxIncluded"], True)
    self.assertEqual(contract_2["value"]["valueAddedTaxIncluded"], True)

    response = self.app.patch_json(
        f"/contracts/{contract_1['id']}?acc_token={self.tender_token}",
        {"data": {"value": {"amount": 200, "amountNet": 201, "currency": "UAH"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    self.assertEqual(
        response.json["errors"],
        [
            {
                'location': 'body',
                'name': 'value',
                'description': 'Amount should be equal or greater than amountNet and differ by no more than 20.0%',
            }
        ],
    )
    # patch 1st contract
    response = self.app.patch_json(
        f"/contracts/{contract_1['id']}?acc_token={self.tender_token}",
        {"data": {"value": {"amount": 200, "amountNet": 195, "currency": "UAH"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 200)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 195)

    # patch 2nd contract
    response = self.app.patch_json(
        f"/contracts/{contract_2['id']}?acc_token={self.tender_token}",
        {"data": {"value": {"amount": 400, "amountNet": 390, "currency": "UAH"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    self.assertEqual(
        response.json["errors"],
        [{'location': 'body', 'name': 'value', 'description': 'Amount should be less or equal to awarded amount'}],
    )

    # 1st contract.value + 2nd contract.value <= award.amount.value
    contract_2["items"][0]["quantity"] = 4
    contract_2["items"][0]["unit"]["value"]["amount"] = 20
    contract_2["items"][1]["quantity"] = 4
    contract_2["items"][1]["unit"]["value"]["amount"] = 20
    response = self.app.patch_json(
        f"/contracts/{contract_2['id']}?acc_token={self.tender_token}",
        {"data": {"value": {"amount": 190, "amountNet": 185, "currency": "UAH"}, "items": contract_2["items"]}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 190)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 185)

    # prepare contract for activating
    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(doc)

    if "contractTemplateName" in self.initial_data:
        # set signerInfo for buyer
        response = self.app.put_json(
            f"/contracts/{contract_1['id']}/buyer/signer_info?acc_token={self.tender_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        # set signerInfo for suppliers
        response = self.app.put_json(
            f"/contracts/{contract_1['id']}/suppliers/signer_info?acc_token={self.bid_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

    # in case any contract become active and there are no pending contracts -> tender should have complete status
    response = self.app.patch_json(
        f"/contracts/{contract_1['id']}?acc_token={self.tender_token}",
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
    self.assertNotEqual(response.json["data"]["status"], "complete")  # because second contract still in pending

    if "contractTemplateName" in self.initial_data:
        # set signerInfo for buyer
        response = self.app.put_json(
            f"/contracts/{contract_2['id']}/buyer/signer_info?acc_token={self.tender_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        # set signerInfo for suppliers
        response = self.app.put_json(
            f"/contracts/{contract_2['id']}/suppliers/signer_info?acc_token={self.bid_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract_2['id']}?acc_token={self.tender_token}",
        {
            "data": {
                "status": "active",
                "contractNumber": "124",
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


def patch_tender_multi_contracts_cancelled(self):
    contracts_response = self.app.get(f"/tenders/{self.tender_id}/contracts")
    contracts = contracts_response.json["data"]
    self.assertEqual(len(contracts), 2)

    # cancel 1st contract
    response = self.app.patch_json(
        f"/contracts/{contracts[0]['id']}?acc_token={self.tender_token}",
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # try to cancel 2nd contract
    response = self.app.patch_json(
        f"/contracts/{contracts[1]['id']}?acc_token={self.tender_token}",
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": (
                    "Can't update contract status from pending to cancelled for last not "
                    "cancelled contract. Cancel award instead."
                ),
            }
        ],
    )

    # check 2nd contract not cancelled
    response = self.app.get(
        f"/contracts/{contracts[1]['id']}",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "pending")

    # cancel award
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    # check 2nd contract also cancelled
    response = self.app.get(
        f"/contracts/{contracts[1]['id']}",
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")


def patch_tender_multi_contracts_cancelled_with_one_activated(self):
    contracts_response = self.app.get(f"/tenders/{self.tender_id}/contracts")
    contracts = contracts_response.json["data"]
    self.assertEqual(len(contracts), 2)

    # patch 1st contract
    response = self.app.patch_json(
        f"/contracts/{contracts[0]['id']}?acc_token={self.tender_token}",
        {"data": {"value": {"amount": 200, "amountNet": 195, "currency": "UAH"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 200)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 195)

    # prepare contract for activating
    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(doc)

    if "contractTemplateName" in self.initial_data:
        # set signerInfo for buyer
        response = self.app.put_json(
            f"/contracts/{contracts[0]['id']}/buyer/signer_info?acc_token={self.tender_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        # set signerInfo for suppliers
        response = self.app.put_json(
            f"/contracts/{contracts[0]['id']}/suppliers/signer_info?acc_token={self.bid_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

    # activate 1st contract
    response = self.app.patch_json(
        f"/contracts/{contracts[0]['id']}?acc_token={self.tender_token}",
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

    # try to cancel award
    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
        {"data": {"status": "cancelled"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "data", "description": "Can\'t cancel award contract in active status"}],
    )


def patch_tender_multi_contracts_cancelled_validate_amount(self):
    contracts_response = self.app.get(f"/tenders/{self.tender_id}/contracts")
    contracts = contracts_response.json["data"]
    self.assertEqual(len(contracts), 2)

    # patch 2nd contract
    response = self.app.patch_json(
        f"/contracts/{contracts[1]['id']}?acc_token={self.tender_token}",
        {"data": {"value": {"amount": 200, "amountNet": 195, "currency": "UAH"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 200)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 195)

    # patch 1st contract
    response = self.app.patch_json(
        f"/contracts/{contracts[0]['id']}?acc_token={self.tender_token}",
        {"data": {"value": {"amount": 400, "amountNet": 395, "currency": "UAH"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "value", "description": "Amount should be less or equal to awarded amount"}],
    )

    # cancel 2nd contract
    response = self.app.patch_json(
        f"/contracts/{contracts[1]['id']}?acc_token={self.tender_token}",
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    # patch 1st contract (2nd attempt)
    # should success because 2nd contract value does not taken into account (now its cancelled)
    response = self.app.patch_json(
        f"/contracts/{contracts[0]['id']}?acc_token={self.tender_token}",
        {"data": {"value": {"amount": 400, "amountNet": 395, "currency": "UAH"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 400)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 395)

    # prepare contract for activating
    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(doc)

    if "contractTemplateName" in self.initial_data:
        # set signerInfo for buyer
        response = self.app.put_json(
            f"/contracts/{contracts[0]['id']}/buyer/signer_info?acc_token={self.tender_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        # set signerInfo for suppliers
        response = self.app.put_json(
            f"/contracts/{contracts[0]['id']}/suppliers/signer_info?acc_token={self.bid_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

    # activate 1st contract
    response = self.app.patch_json(
        f"/contracts/{contracts[0]['id']}?acc_token={self.tender_token}",
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
    self.assertEqual(response.json["data"]["status"], "complete")


def patch_tender_contract(self):
    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get(f"/tenders/{self.tender_id}/contracts")
    contract = response.json["data"][0]
    response = self.app.get(f"/contracts/{contract['id']}")
    contract = response.json["data"]

    self.assertEqual(contract["value"]["amount"], contract["value"]["amountNet"])

    self.app.authorization = ("Basic", ("broker", ""))

    self.set_status("complete", {"status": "active.awarded"})

    token = list(self.initial_bids_tokens.values())[0]
    response = self.app.post_json(
        f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints?acc_token={token}",
        {"data": test_tender_below_claim},
    )
    self.assertEqual(response.status, "201 Created")
    complaint = response.json["data"]
    owner_token = response.json["access"]["token"]

    tender = self.mongodb.tenders.get(self.tender_id)

    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    value = contract["value"]
    value["amountNet"] = value["amount"] - 1

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {
            "data": {
                "contractID": "myselfID",
            }
        },
        status=422,
    )
    self.assertEqual(
        response.json["errors"][0], {"location": "body", "name": "contractID", "description": "Rogue field"}
    )

    new_items = deepcopy(contract["items"])
    new_items[0]["description"] = "New Description"
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {
            "data": {
                "items": new_items,
            }
        },
        status=403,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Updated could be only ('unit', 'quantity') in item, description change forbidden",
    )

    response = self.app.get(f"/contracts/{contract['id']}")
    self.assertEqual(response.json["data"]["contractID"], contract["contractID"])
    self.assertEqual(response.json["data"]["items"], contract["items"])
    self.assertEqual(response.json["data"]["suppliers"], contract["suppliers"])

    old_currency = value["currency"]
    value["currency"] = "USD"
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
        status=403,
    )
    value["currency"] = old_currency
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")

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
                    "Contract signature date should be after award activation date ({})".format(
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
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
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
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"dateSigned": custom_signature_date}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{self.award_id}/complaints/{complaint['id']}?acc_token={self.tender_token}",
        {"data": {"status": "answered", "resolutionType": "resolved", "resolution": "resolution text " * 2}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "answered")
    self.assertEqual(response.json["data"]["resolutionType"], "resolved")
    self.assertEqual(response.json["data"]["resolution"], "resolution text " * 2)

    response = self.app.patch_json(
        "/tenders/{}/awards/{}/complaints/{}?acc_token={}".format(
            self.tender_id, self.award_id, complaint["id"], owner_token
        ),
        {"data": {"satisfied": True, "status": "resolved"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "resolved")

    if "contractTemplateName" in self.initial_data:
        # set signerInfo for buyer
        response = self.app.put_json(
            f"/contracts/{contract['id']}/buyer/signer_info?acc_token={self.tender_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        # set signerInfo for suppliers
        response = self.app.put_json(
            f"/contracts/{contract['id']}/suppliers/signer_info?acc_token={self.bid_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        contract['suppliers'][0]['signerInfo'] = test_signer_info

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
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

    response = self.app.get(f"/contracts/{contract['id']}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertEqual(response.json["data"]["contractID"], contract["contractID"])
    self.assertEqual(response.json["data"]["items"], contract["items"])
    self.assertEqual(response.json["data"]["suppliers"], contract["suppliers"])
    self.assertEqual(response.json["data"]["dateSigned"], custom_signature_date)


def patch_tender_contract_rationale_simple(self):
    # make tender procurementMethodRationale simple
    doc = self.mongodb.tenders.get(self.tender_id)
    doc["procurementMethodRationale"] = "simple"
    self.mongodb.tenders.save(doc)

    self.app.authorization = ("Basic", ("token", ""))
    response = self.app.get(f"/tenders/{self.tender_id}/contracts")
    contract = response.json["data"][0]

    self.assertEqual(contract["value"]["amount"], contract["value"]["amountNet"])

    value = contract["value"]
    value["amountNet"] = value["amount"] - 1
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")

    self.app.authorization = ("Basic", ("broker", ""))

    if "contractTemplateName" in self.initial_data:
        # set signerInfo for buyer
        response = self.app.put_json(
            f"/contracts/{contract['id']}/buyer/signer_info?acc_token={self.tender_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        # set signerInfo for suppliers
        response = self.app.put_json(
            f"/contracts/{contract['id']}/suppliers/signer_info?acc_token={self.bid_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {
            "data": {
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
                "status": "active",
            }
        },
        status=200,
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.json["data"]["status"], "complete")


def patch_tender_contract_value(self):
    response = self.app.get(f"/tenders/{self.tender_id}/contracts")
    contract = response.json["data"][0]

    value = {"amount": 501, "amountNet": 501, "currency": "UAH"}
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount should be less or equal to awarded amount")

    value["amount"] = 502
    value["amountNet"] = 501
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount should be less or equal to awarded amount")

    value["amount"] = 238
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be equal or greater than amountNet and differ by no more than 20.0%",
    )

    value["amount"] = 100
    value["amountNet"] = 80
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be equal or greater than amountNet and differ by no more than 20.0%",
    )

    value["amount"] = 238
    value["amountNet"] = 238
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")

    value["amount"] = 100
    value["amountNet"] = 85
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": {"amount": 100, "amountNet": 85, "currency": "UAH"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 100)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 85)

    value["valueAddedTaxIncluded"] = False
    response = self.app.patch_json(
        f"/contracts/{contract['id']}?acc_token={self.tender_token}",
        {"data": {"value": value}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount and amountNet should be equal")


def patch_tender_contract_value_vat_not_included(self):
    contract_id = self.contracts_ids[0]
    response = self.app.get(f"/contracts/{contract_id}")
    contract = response.json["data"]
    new_value = contract["value"]

    new_value["currency"] = "USD"
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"value": new_value}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Can't update currency for contract value")

    new_value["currency"] = "UAH"
    new_value["amount"] = 468
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"value": new_value}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount and amountNet should be equal")

    new_value["amount"] = 600
    new_value["amountNet"] = 600
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"value": new_value}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"][0]["description"], "Amount should be less or equal to awarded amount")

    new_value["amount"] = 400
    new_value["amountNet"] = 400
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"value": new_value}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 400)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 400)

    new_value["valueAddedTaxIncluded"] = True
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"value": new_value}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["valueAddedTaxIncluded"], True)
    self.assertEqual(response.json["data"]["value"]["amount"], 400)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 400)


def patch_contract_single_item_unit_value(self):
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract = response.json["data"]
    contract_id = contract["id"]
    self.assertEqual(len(contract["items"]), len(self.initial_data["items"]))
    expected_item_unit_currency = contract["items"][0]["unit"]["value"]["currency"]  # "UAH"

    new_items = deepcopy(contract["items"])
    new_items[0]["unit"]["value"]["amount"] = 2000
    new_items[0]["unit"]["value"]["currency"] = "GBP"
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"items": new_items}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "items",
                "description": ["Value mismatch. Expected: currency UAH"],
            }
        ],
    )

    # prepare contract
    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(doc)
    doc = self.mongodb.contracts.get(contract_id)

    if doc['value']['valueAddedTaxIncluded']:
        doc['value']['amountNet'] = str(float(doc['value']['amount']) - 1)
        doc["items"][0]["unit"]["value"]["amount"] = 2000
    self.mongodb.contracts.save(doc)

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
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
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Total amount of unit values can't be greater than contract.value.amount",
                "location": "body",
                "name": "items",
            }
        ],
    )

    new_items = deepcopy(contract["items"])
    new_items[0]["unit"]["value"]["amount"] = 15
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"items": new_items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["amount"], 15.0)

    if "contractTemplateName" in self.initial_data:
        # set signerInfo for buyer
        response = self.app.put_json(
            f"/contracts/{contract['id']}/buyer/signer_info?acc_token={self.tender_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        # set signerInfo for suppliers
        response = self.app.put_json(
            f"/contracts/{contract['id']}/suppliers/signer_info?acc_token={self.bid_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
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
        status=200,
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")

    new_items = deepcopy(contract["items"])
    new_items[0]["unit"]["value"]["amount"] = 555555


def patch_contract_single_item_unit_value_with_status(self):
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract = response.json["data"]
    contract_id = contract["id"]
    self.assertEqual(len(contract["items"]), len(self.initial_data["items"]))

    new_items = deepcopy(contract["items"])
    new_items[0]["unit"]["value"]["amount"] = 2000
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"items": new_items}},
    )
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["amount"], 2000.0)

    # prepare contract
    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(doc)

    doc = self.mongodb.contracts.get(contract_id)
    if doc['value']['valueAddedTaxIncluded']:
        doc['value']['amountNet'] = str(float(doc['value']['amount']) - 1)
    self.mongodb.contracts.save(doc)

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
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
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Total amount of unit values can't be greater than contract.value.amount",
                "location": "body",
                "name": "items",
            }
        ],
    )

    if "contractTemplateName" in self.initial_data:
        # set signerInfo for buyer
        response = self.app.put_json(
            f"/contracts/{contract['id']}/buyer/signer_info?acc_token={self.tender_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        # set signerInfo for suppliers
        response = self.app.put_json(
            f"/contracts/{contract['id']}/suppliers/signer_info?acc_token={self.bid_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

    new_items = deepcopy(contract["items"])
    new_items[0]["unit"]["value"]["amount"] = 15
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {
            "data": {
                "status": "active",
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
                "items": new_items,
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["amount"], 15.0)
    self.assertEqual(response.json["data"]["status"], "active")


def patch_contract_single_item_unit_value_round(self):
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract = response.json["data"]
    contract_id = contract["id"]
    self.assertEqual(len(contract["items"]), 1)
    quantity = contract["items"][0]["quantity"]

    if "contractTemplateName" in self.initial_data:
        # set signerInfo for buyer
        response = self.app.put_json(
            f"/contracts/{contract['id']}/buyer/signer_info?acc_token={self.tender_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        # set signerInfo for suppliers
        response = self.app.put_json(
            f"/contracts/{contract['id']}/suppliers/signer_info?acc_token={self.bid_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

    # prepare contract
    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(doc)
    doc = self.mongodb.contracts.get(contract_id)
    if doc['value']['valueAddedTaxIncluded']:
        doc['value']['amountNet'] = str(float(doc['value']['amount']) - 1)
    self.mongodb.contracts.save(doc)

    unit_value_amount = doc['value']['amount'] / quantity + 0.001

    new_items = deepcopy(contract["items"])
    new_items[0]["unit"]["value"]["amount"] = unit_value_amount
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {
            "data": {
                "status": "active",
                "contractNumber": "123",
                "period": {
                    "startDate": "2016-03-18T18:47:47.155143+02:00",
                    "endDate": "2016-05-18T18:47:47.155143+02:00",
                },
                "items": new_items,
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["amount"], unit_value_amount)
    self.assertEqual(response.json["data"]["status"], "active")


@mock.patch(
    "openprocurement.contracting.core.procedure.state.contract.UNIT_PRICE_REQUIRED_FROM", get_now() - timedelta(days=1)
)
def patch_contract_multi_items_unit_value(self):
    auth = self.app.authorization
    self.app.authorization = ("Basic", ("token", ""))
    contract_id = self.contracts_ids[0]

    contract_items = []
    for i in range(3):
        item = deepcopy(self.initial_data["items"][0])
        item['id'] = str(i + 1) * 10
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

    if self.initial_status != 'active.awarded':
        self.set_status("complete", {"status": "active.awarded"})

    # prepare contract
    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(doc)
    doc = self.mongodb.contracts.get(contract_id)
    if doc['value']['valueAddedTaxIncluded']:
        doc['value']['amountNet'] = str(float(doc['value']['amount']) - 1)
        doc["items"] = contract_items
    self.mongodb.contracts.save(doc)

    response = self.app.get(f"/contracts/{contract_id}")
    contract = response.json["data"]

    self.app.authorization = auth

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(response.json["status"], "error")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Item.unit.value.amount should be updated to 0 if item.quantity equal to 0",
                "location": "body",
                "name": "data",
            }
        ],
    )

    new_items = deepcopy(contract["items"])
    new_items[2]["unit"]["value"]["amount"] = 0
    # new_items[1]["unit"]["value"] = {"amount": 1}
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"items": new_items}},
    )

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['items'][2]["unit"]["value"]["amount"], 0.0)
    self.assertEqual(response.json["data"]["status"], "pending")

    unit_value_amount_sum = sum(
        item['unit']['value']['amount'] * item['quantity']
        for item in response.json['data']['items']
        if item['unit'].get('value')
    )
    self.assertEqual(unit_value_amount_sum, 2000)  # 10 * 200 for first item

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Total amount of unit values can't be greater than contract.value.amount",
                "location": "body",
                "name": "items",
            }
        ],
    )

    if "contractTemplateName" in self.initial_data:
        # set signerInfo for buyer
        response = self.app.put_json(
            f"/contracts/{contract['id']}/buyer/signer_info?acc_token={self.tender_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

        # set signerInfo for suppliers
        response = self.app.put_json(
            f"/contracts/{contract['id']}/suppliers/signer_info?acc_token={self.bid_token}",
            {"data": test_signer_info},
        )
        self.assertEqual(response.status, "200 OK")

    new_items[0]["unit"]["value"]["amount"] = 7.56345
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"items": new_items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json['data']['items'][0]["unit"]["value"]["amount"], 7.56345)

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
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
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't activate contract while unit.value is not set for each item",
                "location": "body",
                "name": "data",
            }
        ],
    )

    new_items[1]["unit"]["value"] = {"amount": 10, "currency": "EUR", "valueAddedTaxIncluded": False}
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"items": new_items}},
        status=422,
    )
    self.assertEqual(
        response.json['errors'],
        [
            {
                "location": "body",
                "name": "items",
                "description": ["Value mismatch. Expected: currency UAH"],
            }
        ],
    )

    new_items[1]["unit"]["value"] = {"amount": 10, "currency": "UAH", "valueAddedTaxIncluded": True}
    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"items": new_items}},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
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


def create_tender_contract(self):
    # tender = self.mongodb.tenders.get(self.tender_id)
    #
    # criterion = tender["criteria"][0]
    # criterion["relatesTo"] = "item"
    # criterion["relatedItem"] = tender["items"][0]["id"]
    # self.mongodb.tenders.save(tender)

    contract_id = self.contracts_ids[0]

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    tender = response.json["data"]

    response = self.app.get(f"/tenders/{self.tender_id}/awards/{self.award_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    award = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get(f"/contracts/{contract_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    contract_fields = {
        "id",
        "awardID",
        "contractID",
        "dateCreated",
        "dateModified",
        "items",
        "tender_id",
        "owner",
        "status",
        "suppliers",
        "buyer",
        "milestones",
    }

    if "contractTemplateName" in tender:
        contract_fields.update({"contractTemplateName"})

    if "value" in award:
        contract_fields.update({"value"})

    self.assertEqual(contract_fields, set(response.json["data"].keys()))
    # self.assertIn("attributes", response.json["data"]["items"][0])

    response = self.activate_contract(contract_id)
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")


def cancelling_award_contract_sync(self):
    contract_id = self.contracts_ids[0]
    response = self.app.get(f"/tenders/{self.tender_id}/awards/{self.award_id}")

    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")

    award = response.json["data"]
    self.assertEqual(response.json["data"]["status"], "active")

    # prepare contract for activating
    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(doc)

    response = self.app.patch_json(
        f"/tenders/{self.tender_id}/awards/{self.award_id}?acc_token={self.tender_token}",
        {"data": {"status": "cancelled"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "cancelled")

    response = self.app.get(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
    )
    self.assertEqual(response.json["data"]["status"], "cancelled")


def patch_multiple_contracts_in_contracting(self):
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract1 = response.json["data"]
    response = self.app.get(f"/contracts/{self.contracts_ids[1]}")
    contract2 = response.json["data"]
    # 1st contract contains 1 item, 2nd contract contains 2 items
    self.assertEqual(len(contract1["items"]), 1)
    self.assertEqual(len(contract2["items"]), 2)

    self.assertEqual(contract1["value"]["amount"], 0)
    self.assertEqual(contract2["value"]["amount"], 0)

    self.assertEqual(contract1["value"]["valueAddedTaxIncluded"], True)
    self.assertEqual(contract2["value"]["valueAddedTaxIncluded"], True)

    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"value": {**contract1["value"], "amount": 200, "currency": "UAH"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    self.assertEqual(
        response.json["errors"],
        [
            {
                'location': 'body',
                'name': 'value',
                'description': 'Amount should be equal or greater than amountNet and differ by no more than 20.0%',
            }
        ],
    )
    # patch 1st contract
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"value": {**contract1["value"], "amount": 200, "amountNet": 195, "currency": "UAH"}}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 200)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 195)

    # patch 2nd contract
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[1]}?acc_token={self.tender_token}",
        {"data": {"value": {**contract2["value"], "amount": 400, "amountNet": 390, "currency": "UAH"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")

    self.assertEqual(
        response.json["errors"],
        [{'location': 'body', 'name': 'value', 'description': 'Amount should be less or equal to awarded amount'}],
    )

    # 1st contract.value + 2nd contract.value <= award.amount.value
    contract2["items"][0]["quantity"] = 4
    contract2["items"][0]["unit"]["value"]["amount"] = 20
    contract2["items"][1]["quantity"] = 4
    contract2["items"][1]["unit"]["value"]["amount"] = 20
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[1]}?acc_token={self.tender_token}",
        {
            "data": {
                "value": {**contract2["value"], "amount": 190, "amountNet": 185, "currency": "UAH"},
                "items": contract2["items"],
            }
        },
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], 190)
    self.assertEqual(response.json["data"]["value"]["amountNet"], 185)

    # prepare contract for activating
    doc = self.mongodb.tenders.get(self.tender_id)
    for i in doc.get("awards", []):
        if 'complaintPeriod' in i:
            i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(doc)

    for i in self.contracts_ids:
        response = self.app.put_json(
            f"/contracts/{i}/buyer/signer_info?acc_token={self.tender_token}",
            {
                "data": {
                    "name": "Test Testovich",
                    "telephone": "+380950000000",
                    "email": "example@email.com",
                    "iban": "1" * 15,
                    "authorizedBy": "документ який дозволяє",
                    "position": "статус",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

        response = self.app.put_json(
            f"/contracts/{i}/suppliers/signer_info?acc_token={self.bid_token}",
            {
                "data": {
                    "name": "Test Testovich",
                    "telephone": "+380950000000",
                    "email": "example@email.com",
                    "iban": "1" * 15,
                    "authorizedBy": "документ який дозволяє",
                    "position": "статус",
                }
            },
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.content_type, "application/json")

    # in case any contract become active and there are no pending contracts -> tender should have complete status
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
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

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertNotEqual(response.json["data"]["status"], "complete")  # because second contract still in pending

    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[1]}?acc_token={self.tender_token}",
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

    response = self.app.get(f"/tenders/{self.tender_id}")
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "complete")
