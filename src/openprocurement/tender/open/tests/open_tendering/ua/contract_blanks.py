def patch_contract_value_multi_currency(self):
    """valueCurrencyEquality=False: the contract value isn't limited by the award value"""
    response = self.app.get(f"/contracts/{self.contracts_ids[0]}")
    contract = response.json["data"]
    self.assertEqual(contract["value"]["amount"], self.award_value["amount"])

    # the contract amount may exceed the award amount
    value = {**contract["value"], "amount": self.award_value["amount"] * 2, "amountNet": self.award_value["amount"] * 2}
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"value": value}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["value"]["amount"], value["amount"])

    # the currency of the contract items stays the one of the contract
    items = contract["items"]
    items[0]["unit"]["value"] = {"amount": 1, "currency": "EUR", "valueAddedTaxIncluded": False}
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": items}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Forbidden to change currency in contract items unit",
    )

    # the total of the item unit values isn't limited by the contract value
    items[0]["unit"]["value"] = {"amount": value["amount"] * 10, "currency": "UAH", "valueAddedTaxIncluded": False}
    response = self.app.patch_json(
        f"/contracts/{self.contracts_ids[0]}?acc_token={self.tender_token}",
        {"data": {"items": items}},
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["items"][0]["unit"]["value"]["amount"], value["amount"] * 10)
