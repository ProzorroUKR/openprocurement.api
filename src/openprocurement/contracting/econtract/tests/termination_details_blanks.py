COMPLETED_TERMINATION_DETAILS = {
    "reasonType": "completed",
    "reason": "all obligations fulfilled",
    "amountPaid": {"amount": 100, "currency": "UAH", "amountNet": 100},
}

DISRUPTED_TERMINATION_DETAILS = {
    "reasonType": "disrupted",
    "reason": "terminated by mutual agreement",
    "amountPaid": {"amount": 50, "currency": "UAH", "amountNet": 50},
}

SIGN_DATA = {
    "documentType": "terminationSignature",
    "title": "sign.p7s",
    "format": "application/pkcs7-signature",
}


def patch_termination_details_buyer_only(self):
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.supplier_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")
    self.assertEqual(
        response.json["errors"],
        [{"location": "url", "name": "permission", "description": "Forbidden"}],
    )


def patch_termination_details_draft(self):
    # touching reasonType without the rest of the required data fails and is not persisted
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": {"reasonType": "completed"}}},
        status=422,
    )
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "terminationDetails",
                "description": "reason is required to activate terminationDetails",
            }
        ],
    )
    response = self.app.get(f"/contracts/{self.contract_id}?acc_token={self.contract_token}")
    self.assertNotIn("terminationDetails", response.json["data"])

    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    self.assertEqual(response.status, "200 OK")
    termination_details = response.json["data"]
    self.assertEqual(termination_details["status"], "draft")
    self.assertEqual(termination_details["reasonType"], "completed")
    self.assertIn("dateCreated", termination_details)
    self.assertNotIn("datePublished", termination_details)


def activate_termination_details_without_required_fields(self):
    # no PATCH was ever made yet, so terminationDetails doesn't exist at all
    sign_data = dict(SIGN_DATA, url=self.generate_docservice_url(), hash="md5:" + "0" * 32)
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.contract_token}",
        {"data": sign_data},
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")


def upload_termination_signature_requires_buyer(self):
    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    sign_data = dict(SIGN_DATA, url=self.generate_docservice_url(), hash="md5:" + "0" * 32)
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.supplier_token}",
        {"data": sign_data},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")


def upload_termination_signature_wrong_document_type(self):
    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    sign_data = {
        "documentType": "contractSignature",
        "title": "sign.p7s",
        "url": self.generate_docservice_url(),
        "hash": "md5:" + "0" * 32,
        "format": "application/pkcs7-signature",
    }
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.contract_token}",
        {"data": sign_data},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")


def activate_termination_details_completed(self):
    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    sign_data = dict(SIGN_DATA, url=self.generate_docservice_url(), hash="md5:" + "0" * 32)
    response = self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.contract_token}",
        {"data": sign_data},
    )
    self.assertEqual(response.status, "201 Created")
    self.assertEqual(response.json["data"]["author"], "buyer")

    response = self.app.get(f"/contracts/{self.contract_id}?acc_token={self.contract_token}")
    termination_details = response.json["data"]["terminationDetails"]
    self.assertEqual(termination_details["status"], "active")
    self.assertIn("datePublished", termination_details)
    self.assertEqual(len(termination_details["documents"]), 1)
    self.assertEqual(response.json["data"]["status"], "terminated")

    # immutable once published
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": {"reason": "changed my mind"}}},
        status=403,
    )
    self.assertEqual(response.status, "403 Forbidden")


def get_termination_details(self):
    response = self.app.get(
        f"/contracts/{self.contract_id}/termination_details",
        status=404,
    )
    self.assertEqual(response.status, "404 Not Found")

    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    response = self.app.get(f"/contracts/{self.contract_id}/termination_details")
    self.assertEqual(response.status, "200 OK")
    self.assertNotIn("context", response.json)
    termination_details = response.json["data"]
    self.assertEqual(termination_details["status"], "draft")
    self.assertEqual(termination_details["reasonType"], "completed")
    self.assertNotIn("documents", termination_details)


def get_termination_details_context(self):
    self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": COMPLETED_TERMINATION_DETAILS}},
    )
    sign_data = dict(SIGN_DATA, url=self.generate_docservice_url(), hash="md5:" + "0" * 32)
    self.app.post_json(
        f"/contracts/{self.contract_id}/termination_details/documents?acc_token={self.contract_token}",
        {"data": sign_data},
    )

    response = self.app.get(f"/contracts/{self.contract_id}/termination_details?opt_context=true")
    self.assertEqual(response.status, "200 OK")
    termination_details = response.json["data"]
    self.assertEqual(termination_details["status"], "active")
    self.assertEqual(len(termination_details["documents"]), 1)
    document = termination_details["documents"][0]
    self.assertEqual(document["documentType"], "terminationSignature")
    self.assertEqual(document["title"], "sign.p7s")

    context = response.json["context"]
    self.assertIn("id", context["contract"])
    self.assertIn("items", context["contract"])
    self.assertEqual(context["contract"]["id"], self.contract_id)
    self.assertEqual(context["contract"]["status"], "terminated")


def activate_termination_details_disrupted_amount_exceeds_value(self):
    # for reasonType `disrupted`, amountPaid must not exceed the contract value
    # (checked eagerly, not only at signing time)
    contract = self.app.get(f"/contracts/{self.contract_id}").json["data"]
    value = contract["value"]

    too_much = dict(DISRUPTED_TERMINATION_DETAILS)
    too_much["amountPaid"] = {"amount": value["amount"] + 1, "currency": value["currency"]}
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": too_much}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "terminationDetails",
                "description": "terminationDetails.amountPaid.amount must not exceed contract value.amount",
            }
        ],
    )

    wrong_currency = dict(DISRUPTED_TERMINATION_DETAILS)
    wrong_currency["amountPaid"] = {"amount": 1, "currency": "EUR"}
    response = self.app.patch_json(
        f"/contracts/{self.contract_id}/termination_details?acc_token={self.contract_token}",
        {"data": {"terminationDetails": wrong_currency}},
        status=422,
    )
    self.assertEqual(response.status, "422 Unprocessable Entity")
    self.assertEqual(
        response.json["errors"],
        [
            {
                "location": "body",
                "name": "terminationDetails",
                "description": "terminationDetails.amountPaid currency must match contract value currency",
            }
        ],
    )
