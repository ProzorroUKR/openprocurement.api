from datetime import timedelta

from openprocurement.api.utils import get_now


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
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")
    self.assertIn("dateSigned", response.json["data"].keys())


def patch_tender_contract(self):
    response = self.app.get("/tenders/{}/contracts".format(self.tender_id))
    contract = response.json["data"][0]

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Can't sign contract before stand-still period end (", response.json["errors"][0]["description"])

    self.set_status("complete", {"status": "active.awarded"})

    tender = self.mongodb.tenders.get(self.tender_id)

    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    old_tender_date_modified = tender["dateModified"]
    old_date = contract["date"]

    value = contract["value"]
    value["amountNet"] = value["amount"] - 1
    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")

    tender = self.mongodb.tenders.get(self.tender_id)

    self.assertNotEqual(tender["dateModified"], old_tender_date_modified)
    self.assertEqual(response.json["data"]["date"], old_date)

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
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "active"}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.patch_json(
        "/tenders/{}/contracts/{}?acc_token={}".format(self.tender_id, contract["id"], self.tender_token),
        {"data": {"status": "pending"}},
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


def patch_tender_econtract(self):
    response = self.app.get(f"/tenders/{self.tender_id}/contracts")
    contract = response.json["data"][0]

    contract_id = self.contracts_ids[0]

    test_signer_info = {
        "name": "Test Testovich",
        "telephone": "+380950000000",
        "email": "example@email.com",
        "iban": "1" * 15,
        "authorizedBy": "статут",
        "position": "Генеральний директор",
    }
    response = self.app.put_json(
        f"/contracts/{contract_id}/suppliers/signer_info?acc_token={self.bid_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.put_json(
        f"/contracts/{contract_id}/buyer/signer_info?acc_token={self.tender_token}",
        {"data": test_signer_info},
    )
    self.assertEqual(response.status, "200 OK")

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"status": "active"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertIn("Can't sign contract before stand-still period end (", response.json["errors"][0]["description"])

    self.set_status("complete", {"status": "active.awarded"})

    tender = self.mongodb.tenders.get(self.tender_id)

    for i in tender.get("awards", []):
        i["complaintPeriod"]["endDate"] = i["complaintPeriod"]["startDate"]
    self.mongodb.tenders.save(tender)

    response = self.app.patch_json(
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
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
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
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
        f"/contracts/{contract_id}?acc_token={self.tender_token}",
        {"data": {"dateSigned": custom_signature_date}},
    )
    self.assertEqual(response.status, "200 OK")


def patch_econtract_multi_currency(self):
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract = response.json["data"]
    self.assertEqual(contract["value"]["amount"], 469.0)
    self.assertEqual(contract["value"]["currency"], "UAH")

    # try to change VAT different from contract value VAT
    contract["items"][0]["unit"]["value"]["valueAddedTaxIncluded"] = False

    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": contract["items"]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Value mismatch. Expected: valueAddedTaxIncluded True"],
    )

    # try to change VAT along with contract value VAT
    contract["items"][0]["unit"]["value"]["valueAddedTaxIncluded"] = False
    contract["value"]["valueAddedTaxIncluded"] = False

    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": contract["items"], "value": contract["value"]}},
    )
    self.assertEqual(response.status, "200 OK")

    # try to change currency in contract value
    contract["value"]["currency"] = "EUR"
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"value": contract["value"]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update currency for contract value",
    )

    # try to change currency in contract items unit
    contract["items"][0]["unit"]["value"]["currency"] = "EUR"
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": contract["items"]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Value mismatch. Expected: currency UAH"],
    )

    # try to change amount in contract items unit and contract value to less value
    contract["items"][0]["unit"]["value"] = {"amount": 0.5, "currency": "UAH", "valueAddedTaxIncluded": False}
    contract["value"] = {"amount": 100, "amountNet": 100, "currency": "UAH", "valueAddedTaxIncluded": False}
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": contract["items"], "value": contract["value"]}},
    )
    self.assertEqual(response.status, "200 OK")

    # try to change amount in contract items unit and contract value to greater value
    contract["items"][0]["unit"]["value"]["amount"] = 50
    contract["value"] = {"amount": 10000, "amountNet": 10000, "currency": "UAH", "valueAddedTaxIncluded": False}
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": contract["items"], "value": contract["value"]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Amount should be less or equal to awarded amount",
    )

    # check total amount of unit values can't be greater than contract.value.amount
    contract["items"][0]["unit"]["value"]["amount"] = 50
    contract["items"][0]["quantity"] = 10  # 50 * 10 = 500
    contract["value"] = {"amount": 400, "amountNet": 400, "currency": "UAH", "valueAddedTaxIncluded": False}
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": contract["items"], "value": contract["value"]}},
    )
    self.assertEqual(response.status, "200 OK")

    # try to activate contract with amount of unit values greater than contract.value.amount
    response = self.activate_contract(self.contracts_ids[0], status=403)
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Total amount of unit values can't be greater than contract.value.amount",
    )


def patch_econtract_dps_multi_currency(self):
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract = response.json["data"]
    self.assertEqual(contract["value"]["amount"], 469.0)
    self.assertEqual(contract["value"]["currency"], "UAH")

    # try to change VAT different from contract value VAT
    contract["items"][0]["unit"]["value"]["valueAddedTaxIncluded"] = False

    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": contract["items"]}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"][0]["description"],
        ["Value mismatch. Expected: valueAddedTaxIncluded True"],
    )

    # try to change VAT along with contract value VAT
    contract["items"][0]["unit"]["value"]["valueAddedTaxIncluded"] = False
    contract["value"]["valueAddedTaxIncluded"] = False

    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": contract["items"], "value": contract["value"]}},
    )
    self.assertEqual(response.status, "200 OK")

    # try to change currency in contract value
    contract["value"]["currency"] = "EUR"
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"value": contract["value"]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update currency for contract value",
    )

    # try to change currency in contract items unit
    contract["items"][0]["unit"]["value"]["currency"] = "EUR"
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": contract["items"]}},
    )
    self.assertEqual(response.status, "200 OK")

    # try to change amount in contract items unit and contract value to less value
    contract["items"][0]["unit"]["value"] = {"amount": 0.5, "currency": "UAH", "valueAddedTaxIncluded": False}
    contract["value"] = {"amount": 100, "amountNet": 100, "currency": "UAH", "valueAddedTaxIncluded": False}
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": contract["items"], "value": contract["value"]}},
    )
    self.assertEqual(response.status, "200 OK")

    # try to change amount in contract items unit and contract value to greater value
    contract["items"][0]["unit"]["value"]["amount"] = 50
    contract["value"] = {"amount": 10000, "amountNet": 10000, "currency": "UAH", "valueAddedTaxIncluded": False}
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": contract["items"], "value": contract["value"]}},
    )
    self.assertEqual(response.status, "200 OK")

    # check total amount of unit values can't be greater than contract.value.amount
    contract["items"][0]["unit"]["value"]["amount"] = 50
    contract["items"][0]["quantity"] = 10  # 50 * 10 = 500
    contract["value"] = {"amount": 400, "amountNet": 400, "currency": "UAH", "valueAddedTaxIncluded": False}
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": contract["items"], "value": contract["value"]}},
    )
    self.assertEqual(response.status, "200 OK")

    # try to activate contract with amount of unit values greater than contract.value.amount
    response = self.activate_contract(self.contracts_ids[0])
    self.assertEqual(response.status, "200 OK")
