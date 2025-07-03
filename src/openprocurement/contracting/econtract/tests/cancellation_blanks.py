def create_cancellation_by_buyer(self):
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/cancellations?acc_token={self.contract_token}",
        {"data": {}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {"location": "body", "name": "reason", "description": ["This field is required."]},
            {"location": "body", "name": "reasonType", "description": ["This field is required."]},
        ],
    )
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/cancellations?acc_token={self.contract_token}",
        {"data": {"reasonType": "something", "reason": "want to change info"}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [{"location": "body", "name": "reasonType", 'description': ["Value must be one of ['requiresChanges']."]}],
    )

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/cancellations?acc_token={self.contract_token}",
        {"data": {"reasonType": "requiresChanges", "reason": "want to change info"}},
    )
    self.assertEqual(response.status, "201 Created")

    # try to add one more
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/cancellations?acc_token={self.supplier_token}",
        {"data": {"reasonType": "requiresChanges", "reason": "want to change info"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Cancellation for contract already exists",
            }
        ],
    )

    # try to add signature after cancellation
    contract_sign_data = {
        "documentType": "contractSignature",
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }
    # add signature for supplier
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.supplier_token}",
        {"data": contract_sign_data},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Forbidden to sign contract with cancellation",
            }
        ],
    )


def create_cancellation_by_supplier(self):
    # add signature before cancellation by buyer
    contract_sign_data = {
        "documentType": "contractSignature",
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }
    self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {"data": contract_sign_data},
    )

    # add cancellation by supplier
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/cancellations?acc_token={self.supplier_token}",
        {"data": {"reasonType": "requiresChanges", "reason": "want to change info"}},
    )
    self.assertEqual(response.status, "201 Created")


def create_cancellation_after_signing_contract(self):
    # add signature before cancellation by supplier
    contract_sign_data = {
        "documentType": "contractSignature",
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }
    self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.supplier_token}",
        {"data": contract_sign_data},
    )

    # try to add cancellation by the same author after signing
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/cancellations?acc_token={self.supplier_token}",
        {"data": {"reasonType": "requiresChanges", "reason": "want to change info"}},
        status=403,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "data",
                "description": "Contract already signed by supplier",
            }
        ],
    )


def get_cancellation(self):
    # add cancellation by supplier
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/cancellations?acc_token={self.supplier_token}",
        {"data": {"reasonType": "requiresChanges", "reason": "want to change info"}},
    )
    self.assertEqual(response.status, "201 Created")
    cancellation_id = response.json["data"]["id"]

    response = self.app.get(f"/contracts/{self.contract_id}/cancellations")
    self.assertEqual(len(response.json["data"]), 1)
    self.assertEqual(response.json["data"][0]["status"], "pending")

    response = self.app.get(f"/contracts/{self.contract_id}/cancellations/{cancellation_id}")
    self.assertEqual(response.json["data"]["author"], "supplier")

    response = self.app.get(f"/contracts/{self.contract_id}")
    self.assertEqual(len(response.json["data"]["cancellations"]), 1)
