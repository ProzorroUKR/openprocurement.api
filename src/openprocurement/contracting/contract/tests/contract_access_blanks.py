def get_credentials(self):
    response = self.app.get(
        f"/contracts/{self.contract_id}/credentials?acc_token={self.tender_token}",
        status=405,
    )
    self.assertEqual(response.status, "405 Method Not Allowed")


def generate_credentials(self):
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/credentials?acc_token={self.tender_token}", {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["id"], self.initial_data["id"])
    self.assertNotIn("tender_token", response.json["data"])
    self.assertNotIn("owner_token", response.json["data"])
    self.assertEqual(response.json["data"]["owner"], "broker")
    self.assertEqual(len(response.json["access"]["token"]), 32)
    token1 = response.json["access"]["token"]

    # try second time generation
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/credentials?acc_token={self.tender_token}", {"data": ""}
    )
    self.assertEqual(response.status, "200 OK")
    self.assertEqual(response.json["data"]["id"], self.initial_data["id"])
    self.assertEqual(len(response.json["access"]["token"]), 32)
    token2 = response.json["access"]["token"]
    self.assertNotEqual(token1, token2)

    # first access token is non-workable
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={token1}", {"data": {"status": "active"}}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={token2}",
        {"data": {"value": {**self.contract["value"], "amountNet": self.contract["value"]["amountNet"] - 1}}},
    )
    # terminated contract is also protected
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}?acc_token={token2}",
        {"data": {"status": "terminated", "amountPaid": {"amount": 100, "amountNet": 90}}},
    )
    self.assertEqual(response.status, "200 OK")
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/credentials?acc_token={self.tender_token}", {"data": ""}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "description": "Can't generate credentials in current (terminated) contract status",
                "location": "body",
                "name": "data",
            }
        ],
    )


def generate_credentials_invalid(self):
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/credentials?acc_token=fake token", {"data": ""}, status=403
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.json["errors"], [{"description": "Forbidden", "location": "url", "name": "permission"}])

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/credentials?acc_token=токен з кирилицею",
        {"data": ""},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                'location': 'body',
                'name': 'UnicodeEncodeError',
                'description': "'latin-1' codec can't encode characters in position 10-14: ordinal not in range(256)",
            }
        ],
    )
