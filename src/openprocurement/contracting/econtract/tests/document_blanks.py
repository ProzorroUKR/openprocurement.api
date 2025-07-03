def sign_pending_contract(self):
    contract_sign_data = {
        "documentType": "contractSignature",
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {"data": contract_sign_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("sign.p7s", response.json["data"]["title"])
    self.assertEqual(response.json["data"]["documentOf"], "contract")
    self.assertEqual(response.json["data"]["documentType"], "contractSignature")
    self.assertIn("author", response.json["data"])
    self.assertEqual(response.json["data"]["author"], "buyer")

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.supplier_token}", {"data": contract_sign_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]
    self.assertIn(doc_id, response.headers["Location"])
    self.assertEqual("sign.p7s", response.json["data"]["title"])
    self.assertEqual(response.json["data"]["documentOf"], "contract")
    self.assertEqual(response.json["data"]["documentType"], "contractSignature")
    self.assertIn("author", response.json["data"])
    self.assertEqual(response.json["data"]["author"], "supplier")

    # check contract status
    response = self.app.get(f"/contracts/{self.contract_id}?acc_token={self.supplier_token}")
    self.assertEqual(response.json["data"]["status"], "active")

    response = self.app.get(f"/tenders/{self.tender_id}/contracts/{self.contract_id}?acc_token={self.tender_token}")
    self.assertEqual(response.json["data"]["status"], "active")


def sign_active_contract(self):
    self.activate_contract()
    contract_sign_data = {
        "documentType": "contractSignature",
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {"data": contract_sign_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add sign document in current (active) contract status",
    )

    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.supplier_token}",
        {"data": contract_sign_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't add sign document in current (active) contract status",
    )


def patch_signature_in_active_contract(self):
    self.activate_contract()
    response = self.app.get(f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}")
    doc_id = response.json["data"][0]["id"]

    # patch signature
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.contract_token}",
        {"data": {"title": "new.p7s"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Can't update sign document in current (active) contract status",
    )


def patch_contract_signature_by_another_user(self):
    contract_sign_data = {
        "documentType": "contractSignature",
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}", {"data": contract_sign_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")
    doc_id = response.json["data"]["id"]

    # patch signature
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/documents/{doc_id}?acc_token={self.supplier_token}",
        {"data": {"title": "new.p7s"}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Only author can update this object",
    )


def patch_contract_signature_duplicate(self):
    contract_sign_data = {
        "documentType": "contractSignature",
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}", {"data": contract_sign_data}
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.content_type, "application/json")

    # put signature
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.contract_token}",
        {"data": contract_sign_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(response.content_type, "application/json")
    self.assertEqual(
        response.json["errors"][0]["description"],
        "Contract signature for buyer already exists",
    )


def activate_contract_after_signatures_and_document_upload(self):
    contract_before = self.mongodb.contracts.get(self.contract_id)
    self.assertEqual(contract_before["status"], "pending")

    # add signature for buyer
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
    # add signature for supplier
    self.app.post_json(
        f"/contracts/{self.contract_id}/documents?acc_token={self.bid_token}",
        {"data": contract_sign_data},
    )

    contract_after = self.mongodb.contracts.get(self.contract_id)
    self.assertEqual(contract_after["status"], "active")

    tender = self.mongodb.tenders.get(self.tender_id)
    self.assertEqual(tender["contracts"][0]["status"], "active")
