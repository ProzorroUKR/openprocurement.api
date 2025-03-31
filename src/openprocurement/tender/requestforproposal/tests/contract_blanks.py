def patch_econtract_multi_currency(self):
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract = response.json["data"]
    self.assertEqual(contract["value"]["amount"], 500)
    self.assertEqual(contract["value"]["currency"], "UAH")

    # try to change contract value VAT
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
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Forbidden to change currency in contract items unit",
    )

    # try to change amount in contract items unit and contract value to less value
    contract["items"][0]["unit"]["value"]["amount"] = 0.5
    contract["items"][0]["unit"]["value"]["currency"] = "UAH"
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

    del contract["items"][0]["unit"]["value"]
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": contract["items"]}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Forbidden to delete fields in unit: {'value'}",
    )

    # try to activate contract with amount of unit values greater than contract.value.amount
    response = self.activate_contract(self.contracts_ids[0])
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["status"], "active")
